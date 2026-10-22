from decimal import Decimal

from app.pricing import Money, total


def test_total_of_empty_is_zero():
    assert total([]).amount == Decimal("0")


def test_total_sums():
    assert total([Money(Decimal("1.50")), Money(Decimal("2.50"))]).amount == Decimal("4.00")
