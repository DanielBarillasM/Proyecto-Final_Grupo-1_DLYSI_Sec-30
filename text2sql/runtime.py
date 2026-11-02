from __future__ import annotations

import random
import threading
from pathlib import Path
from typing import Any

from .config import ProjectConfig


class TextToSQLRuntime:
    """Carga perezosa y thread-safe del modelo base y el adapter opcional."""

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        self._model: Any = None
        self._tokenizer: Any = None
        self._lock = threading.Lock()

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            try:
                import numpy as np
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            except ImportError as exc:
                raise RuntimeError(
                    "Faltan dependencias del modelo. Instala requirements.txt "
                    "en el entorno local de ejecución."
                ) from exc

            random.seed(self.config.semilla)
            np.random.seed(self.config.semilla)
            torch.manual_seed(self.config.semilla)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.config.semilla)

            tokenizer = AutoTokenizer.from_pretrained(
                self.config.modelo_base,
                revision=self.config.modelo_revision,
                trust_remote_code=False,
            )
            if tokenizer.pad_token_id is None:
                tokenizer.pad_token = tokenizer.eos_token

            model_kwargs: dict[str, Any] = {
                "device_map": "auto",
                "revision": self.config.modelo_revision,
                "trust_remote_code": False,
                "low_cpu_mem_usage": True,
                "use_safetensors": True,
            }
            if torch.cuda.is_available():
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=torch.float16,
                )
            else:
                model_kwargs["torch_dtype"] = torch.float32

            model = AutoModelForCausalLM.from_pretrained(
                self.config.modelo_base,
                **model_kwargs,
            )
            if self.config.usar_adapter:
                adapter_path = Path(self.config.adapter)
                local_weights = tuple(adapter_path.glob("adapter_model.*"))
                if (adapter_path / "adapter_config.json").is_file() and any(
                    path.is_file() and path.stat().st_size > 0 for path in local_weights
                ):
                    adapter_source = str(adapter_path)
                elif self.config.adapter_repo_id:
                    adapter_source = self.config.adapter_repo_id
                else:
                    raise FileNotFoundError(
                        "No se encontró un adapter local ni adapter_repo_id. "
                        "Descarga el adapter o establece usar_adapter=false."
                    )
                from peft import PeftModel

                adapter_kwargs: dict[str, Any] = {"is_trainable": False}
                if adapter_source == self.config.adapter_repo_id and self.config.adapter_revision:
                    adapter_kwargs["revision"] = self.config.adapter_revision
                model = PeftModel.from_pretrained(model, adapter_source, **adapter_kwargs)

            model.eval()
            generation_config = getattr(model, "generation_config", None)
            if generation_config is not None:
                generation_config.temperature = None
                generation_config.top_p = None
                generation_config.top_k = None
            self._tokenizer = tokenizer
            self._model = model

    def generate(self, prompt: str, *, max_new_tokens: int = 256) -> str:
        self._load()
        import torch

        tokenizer = self._tokenizer
        model = self._model
        messages = [{"role": "user", "content": prompt}]
        if hasattr(tokenizer, "apply_chat_template"):
            rendered = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            rendered = prompt
        inputs = tokenizer(rendered, return_tensors="pt", truncation=True, max_length=8192)
        device = next(model.parameters()).device
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with self._lock, torch.inference_mode():
            output = model.generate(
                **inputs,
                do_sample=False,
                num_beams=1,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        generated = output[0, inputs["input_ids"].shape[1] :]
        return tokenizer.decode(generated, skip_special_tokens=True).strip()
