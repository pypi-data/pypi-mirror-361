# Данные и программные утилиты МГИМО

## Установка

```console
pip install mgimo
```

## Использование

```python
from random import choice
from mgimo.data import capital_cities_by_country

countries = list(capital_cities_by_country)["ru"].keys()
country = choice(countries)
city = capital_cities_by_country["ru"][country]
print(f"Страна: {country}, столица: {city}.")
```