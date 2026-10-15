import json
import pathlib
import random

random.seed(7)

# Зачем: Это заготовки (справочники) для наполнения полей.
# Из них Python будет случайным образом собирать строки бюджета.
communities = ["Київська ТГ", "Львівська ТГ", "Одеська ТГ", "Харківська ТГ", "Дніпровська ТГ"]
budget_articles = ["Заробітна плата вчителів", "Ремонт доріг та інфраструктури", ...]
budget_types = ["income", "expense"]

path = pathlib.Path("data/large.jsonl")
path.parent.mkdir(parents=True, exist_ok=True)

prev = None

with path.open("w", encoding="utf-8") as f:
    for i in range(200_000):
        if i % 10 == 3 and prev is not None:
            row = dict(prev)

        else:
            row = {
                
                "code": f"{random.choice(communities)}-{i}",
                # Название статьи: берем из списка + делаем 4000 уникальных вариаций
                "name": f"{random.choice(budget_articles)} {i%4000}",
               
                "amount": str(random.randint(500, 5000)) if i % 7 else "за домовленістю",
                # Направление: случайно выбираем доход это или расход
                "type": random.choice(budget_types),
            }

            # Зачем: Имитация критической ошибки данных. Каждую 1000-ю строку мы намеренно ломаем —
            # зануляем в ней код ('code': ''). Анализатор должен будет отфильтровать такие пустые строки.
            if i % 1000 == 0:
                row = dict(row, code="")

       
        prev = row

        #  Превращаем Python-словарь в текстовую строку формата JSON и записываем её в файл с новой строки (\n).
        # ensure_ascii=False нужен, чтобы украинские буквы (ї, є, і) записались красиво, а не кодами типа \u0456.
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
