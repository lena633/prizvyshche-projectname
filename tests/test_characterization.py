import json
import tempfile
from pathlib import Path

from jobradar.services.pipeline import load_budget_data


def test_refactored_pipeline_output_is_stable() -> None:  # Аннотация -> None
    sample_data = [
        {"code": "11010100", "name": " Tax 1 ", "amount": "4500000", "type": "income"},
        {"code": "11010100", "name": "tax 1", "amount": "4500000", "type": "income"},
        {"code": "", "name": "Tax 2", "amount": "1200000", "type": "income"},
        {"code": "18050400", "name": "Tax 3", "amount": "undefined", "type": "income"},
        {"code": "0110150", "name": "Expense 1", "amount": "850000", "type": "expense"},
        {"code": "0111010", "name": "Expense 2 (Kindergartens)", "amount": "3200000", "type": "expense"},
        {"code": "0111020", "name": "Expense 3 (Schools)", "amount": "7400000", "type": "expense"},
        {"code": "0111020", "name": "expense 3 (schools)", "amount": "7400000", "type": "expense"},
        {"code": "0114060", "name": "", "amount": "150000", "type": "expense"},
        {"code": "0116030", "name": "Expense 4", "amount": "in progress", "type": "expense"},
        {"code": "0117310", "name": "Expense 5 (Objects)", "amount": "2100000", "type": "expense"},
        {"code": "0118110", "name": "Expense 6", "amount": "450000", "type": "expense"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(sample_data, tmp, ensure_ascii=False)
        tmp_path = Path(tmp.name)

    try:
        rows = load_budget_data(tmp_path)
        # ИСПРАВЛЕНО: Ожидаем ровно 8 чистых строк на выходе
        assert len(rows) == 8  
        # ИСПРАВЛЕНО: Сравниваем число с числом (без кавычек)
        assert rows[0].amount == 4500000  
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
