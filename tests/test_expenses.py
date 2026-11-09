import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from expenses import (
    create_expense,
    load_expenses,
    parse_amount,
    save_expenses,
    summarize_by_category,
)


class ExpenseTests(unittest.TestCase):
    def test_amount_accepts_comma_decimal_separator(self):
        self.assertEqual(parse_amount("12,5"), Decimal("12.50"))

    def test_non_positive_amount_is_rejected(self):
        for value in ("0", "-2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_amount(value)

    def test_save_and_load_expenses(self):
        expense = create_expense("18.75", "Alimentação", "Lanche", "2025-01-02")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.csv"
            save_expenses([expense], path)
            self.assertEqual(load_expenses(path), [expense])

    def test_summary_adds_amounts_by_category(self):
        expenses = [
            create_expense("10", "Transporte", "Ônibus", "2025-01-02"),
            create_expense("5.50", "Transporte", "Metrô", "2025-01-03"),
            create_expense("20", "Lazer", "Cinema", "2025-01-04"),
        ]
        self.assertEqual(
            summarize_by_category(expenses),
            {"Lazer": Decimal("20.00"), "Transporte": Decimal("15.50")},
        )

    def test_default_date_is_today(self):
        self.assertEqual(create_expense("1", "Outros", "Teste").spent_on, date.today())

    def test_invalid_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "AAAA-MM-DD"):
            create_expense("1", "Outros", "Teste", "02-01-2025")


if __name__ == "__main__":
    unittest.main()
