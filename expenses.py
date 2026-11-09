"""Registro de despesas em CSV e resumo por categoria."""

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Expense:
    amount: Decimal
    category: str
    description: str
    spent_on: date


def parse_amount(value: str) -> Decimal:
    """Converte um valor decimal em formato de ponto ou vírgula."""
    normalized = value.strip().replace(",", ".")
    try:
        amount = Decimal(normalized)
    except InvalidOperation as error:
        raise ValueError("Informe um valor numérico válido.") from error
    if not amount.is_finite() or amount <= 0:
        raise ValueError("O valor da despesa deve ser maior que zero.")
    return amount.quantize(Decimal("0.01"))


def load_expenses(path: Path) -> list[Expense]:
    if not path.exists():
        return []

    expenses = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                expense = Expense(
                    amount=parse_amount(row["amount"]),
                    category=row["category"],
                    description=row["description"],
                    spent_on=date.fromisoformat(row["spent_on"]),
                )
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Registro inválido em {path}: {row}") from error
            expenses.append(expense)
    return expenses


def save_expenses(expenses: list[Expense], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["amount", "category", "description", "spent_on"]
        )
        writer.writeheader()
        for expense in expenses:
            writer.writerow(
                {
                    "amount": f"{expense.amount:.2f}",
                    "category": expense.category,
                    "description": expense.description,
                    "spent_on": expense.spent_on.isoformat(),
                }
            )


def create_expense(
    amount: str,
    category: str,
    description: str,
    spent_on: Optional[str] = None,
) -> Expense:
    category = category.strip()
    description = description.strip()
    if not category or not description:
        raise ValueError("Categoria e descrição não podem ficar vazias.")
    try:
        expense_date = date.fromisoformat(spent_on) if spent_on else date.today()
    except ValueError as error:
        raise ValueError("A data deve estar no formato AAAA-MM-DD.") from error
    return Expense(parse_amount(amount), category, description, expense_date)


def summarize_by_category(expenses: list[Expense]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for expense in expenses:
        totals[expense.category] += expense.amount
    return dict(sorted(totals.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Registre e consulte suas despesas.")
    parser.add_argument("--file", type=Path, default=Path("expenses.csv"))
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="registra uma despesa")
    add_parser.add_argument("amount")
    add_parser.add_argument("category")
    add_parser.add_argument("description")
    add_parser.add_argument("--date", dest="spent_on", help="data no formato AAAA-MM-DD")
    commands.add_parser("list", help="lista as despesas")
    commands.add_parser("summary", help="mostra totais por categoria")
    args = parser.parse_args()

    expenses = load_expenses(args.file)
    if args.command == "add":
        expenses.append(
            create_expense(args.amount, args.category, args.description, args.spent_on)
        )
        save_expenses(expenses, args.file)
        print("Despesa registrada.")
    elif args.command == "list":
        if not expenses:
            print("Nenhuma despesa cadastrada.")
        for expense in expenses:
            print(
                f"{expense.spent_on.isoformat()} | {expense.category} | "
                f"R$ {expense.amount:.2f} | {expense.description}"
            )
    else:
        totals = summarize_by_category(expenses)
        if not totals:
            print("Nenhuma despesa cadastrada.")
        for category, total in totals.items():
            print(f"{category}: R$ {total:.2f}")


if __name__ == "__main__":
    main()
