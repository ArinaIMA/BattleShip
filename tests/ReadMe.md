Для определения покрытия тестами использовать команду:

```commandline
pytest tests/ -v --cov=models --cov-report=term-missing
```

models/ship.py - покрытие 100%
models/grid.py - покрытие 99% (строка 91)