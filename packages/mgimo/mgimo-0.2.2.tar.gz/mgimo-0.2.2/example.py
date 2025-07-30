from random import choice

from mgimo.data import capital_cities_ru

countries = list(capital_cities_ru.keys())
country = choice(countries)
city = capital_cities_ru[country]
print(f"Страна: {country}, столица: {city}.")
