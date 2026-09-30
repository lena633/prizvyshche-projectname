from pathlib import Path
from jobradar.services.pipeline import load_vacancies


def test_modern_pipeline_output_is_stable():
    base_path = Path(__file__).parent.parent
    data_file = base_path / "data" / "vacancies.json"

    vacancies = load_vacancies(data_file)

    assert len(vacancies) == 2

    # Проверяем первый элемент (Python Developer)
    assert vacancies[0].title == "python developer"
    assert vacancies[0].salary == 1500

    # Проверяем второй элемент (Data Analyst)
    assert vacancies[1].title == "data analyst"
    assert vacancies[1].salary is None  # нечисловая зарплата теперь None
