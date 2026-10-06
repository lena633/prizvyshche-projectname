from src.jobradar.services.pipeline import PipelineStats, batched, parse_all


def test_invalid_rows_are_counted():
    rows = [
        {"code": "11010100", "name": "Tax 1", "amount": "4500000", "type": "income"},
        {"code": "", "name": "Tax 2", "amount": "1200000", "type": "income"},
    ]

    stats = PipelineStats()
    result = list(parse_all(rows, stats))

    assert len(result) == 1
    assert stats.read == 2
    assert stats.invalid == 1


def test_batched_splits_tail():
    assert [len(b) for b in batched(range(7), 3)] == [3, 3, 1]
