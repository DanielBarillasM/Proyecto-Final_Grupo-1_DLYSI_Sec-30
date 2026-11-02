from text2sql.evaluation import ScoredExample, execution_match, weighted_execution_accuracy


def test_extra_column_does_not_penalize() -> None:
    expected = {"ok": True, "columnas": ["name"], "filas": [["Ana"], ["Luis"]]}
    predicted = {
        "ok": True,
        "columnas": ["id", "name"],
        "filas": [[2, "Luis"], [1, "Ana"]],
    }
    assert execution_match(expected, predicted)


def test_order_only_matters_when_requested() -> None:
    left = {"ok": True, "columnas": ["n"], "filas": [[1], [2]]}
    right = {"ok": True, "columnas": ["n"], "filas": [[2], [1]]}
    assert execution_match(left, right)
    assert not execution_match(left, right, order_matters=True)


def test_weighted_accuracy() -> None:
    score = weighted_execution_accuracy(
        [
            ScoredExample("facil", True),
            ScoredExample("media", False),
            ScoredExample("dificil", True),
        ]
    )
    assert score == 4 / 6
