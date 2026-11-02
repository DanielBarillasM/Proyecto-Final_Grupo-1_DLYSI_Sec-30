from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entrena una configuración QLoRA en una GPU CUDA local compatible.")
    parser.add_argument("--config", required=True, type=Path, help="JSON de configuraciones/.")
    parser.add_argument("--output", required=True, type=Path, help="Directorio de salida del adapter.")
    parser.add_argument("--smoke", action="store_true", help="Usa 32 ejemplos y 2 pasos para validar el pipeline.")
    parser.add_argument("--resume-from-checkpoint", type=Path, help="Checkpoint local desde el cual reanudar.")
    return parser.parse_args()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main() -> None:
    args = parse_args()
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass
    import numpy as np
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        DataCollatorForSeq2Seq,
        Trainer,
        TrainingArguments,
    )

    from text2sql.prompting import build_prompt

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Se requiere una GPU CUDA local compatible. Verifica el driver NVIDIA, "
            "PyTorch CUDA y bitsandbytes antes de entrenar."
        )
    config = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    project = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    seed = int(config["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    rows = [
        json.loads(line)
        for line in (ROOT / "datos" / "entrenamiento" / "aceptados.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    schema_ids = sorted({row["schema_id"] for row in rows})
    dev_schemas = set(schema_ids[-2:])
    train_rows = [row for row in rows if row["schema_id"] not in dev_schemas]
    eval_rows = [row for row in rows if row["schema_id"] in dev_schemas]
    if args.smoke:
        train_rows = train_rows[:32]
        eval_rows = eval_rows[:16]

    tokenizer = AutoTokenizer.from_pretrained(project["modelo_base"], trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    max_length = int(config["max_seq_length"])

    def tokenize(row: dict) -> dict:
        prompt = build_prompt(row["esquema"], row["pregunta"])
        if hasattr(tokenizer, "apply_chat_template"):
            prefix = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prefix = prompt + "\n"
        full = prefix + row["sql"] + tokenizer.eos_token
        encoded = tokenizer(full, truncation=True, max_length=max_length)
        prefix_ids = tokenizer(prefix, truncation=True, max_length=max_length)["input_ids"]
        labels = list(encoded["input_ids"])
        labels[: min(len(prefix_ids), len(labels))] = [-100] * min(len(prefix_ids), len(labels))
        encoded["labels"] = labels
        return encoded

    train_dataset = Dataset.from_list(train_rows).map(tokenize, remove_columns=list(train_rows[0]))
    eval_dataset = Dataset.from_list(eval_rows).map(tokenize, remove_columns=list(eval_rows[0]))
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        project["modelo_base"],
        quantization_config=quantization,
        device_map="auto",
        trust_remote_code=False,
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(
        model,
        LoraConfig(
            r=int(config["r"]),
            lora_alpha=int(config["lora_alpha"]),
            lora_dropout=float(config["lora_dropout"]),
            target_modules=config["target_modules"],
            task_type="CAUSAL_LM",
            bias="none",
        ),
    )
    model.print_trainable_parameters()
    output = (ROOT / args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    train_args = TrainingArguments(
        output_dir=str(output),
        num_train_epochs=float(config["epochs"]),
        learning_rate=float(config["learning_rate"]),
        per_device_train_batch_size=int(config["per_device_train_batch_size"]),
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=int(config["gradient_accumulation_steps"]),
        gradient_checkpointing=True,
        fp16=True,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=1 if args.smoke else 50,
        save_strategy="steps",
        save_steps=1 if args.smoke else 50,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        save_safetensors=True,
        seed=seed,
        data_seed=seed,
        max_steps=2 if args.smoke else -1,
    )
    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True, label_pad_token_id=-100),
    )
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    checkpoint = (ROOT / args.resume_from_checkpoint).resolve() if args.resume_from_checkpoint else None
    result = trainer.train(resume_from_checkpoint=str(checkpoint) if checkpoint else None)
    duration = time.perf_counter() - started
    trainer.save_model(str(output))
    tokenizer.save_pretrained(str(output))
    metrics = {
        **result.metrics,
        "duration_seconds_wall": duration,
        "train_examples": len(train_rows),
        "eval_examples": len(eval_rows),
        "train_schemas": sorted(set(schema_ids) - dev_schemas),
        "dev_schemas": sorted(dev_schemas),
        "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
        "total_parameters": sum(p.numel() for p in model.parameters()),
        "gpu": torch.cuda.get_device_name(0),
        "gpu_total_memory_gib": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 3),
        "gpu_peak_allocated_gib": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
        "gpu_peak_reserved_gib": round(torch.cuda.max_memory_reserved() / 1024**3, 3),
        "environment": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pytorch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "transformers": package_version("transformers"),
            "peft": package_version("peft"),
            "accelerate": package_version("accelerate"),
            "bitsandbytes": package_version("bitsandbytes"),
        },
        "config": config,
    }
    (output / "run_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "log_history.json").write_text(json.dumps(trainer.state.log_history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
