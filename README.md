# Controle de gastos

Aplicativo de terminal para registrar despesas em CSV e consultar totais por categoria.

## Requisitos

- Python 3.9 ou superior

## Como usar

```bash
python expenses.py add 25.90 Alimentacao "Almoço"
python expenses.py add 12.00 Transporte "Ônibus"
python expenses.py list
python expenses.py summary
```

Os registros são salvos em `expenses.csv` no diretório atual. O valor pode usar ponto ou vírgula como separador decimal.

Para executar os testes:

```bash
python -m unittest discover -s tests -v
```

## O que este projeto pratica

Persistência em CSV, validação de datas e valores monetários com `Decimal`, agregação de dados e testes automatizados.
