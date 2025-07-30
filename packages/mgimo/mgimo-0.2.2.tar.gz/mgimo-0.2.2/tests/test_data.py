from mgimo.data import capital_cities_ru


def test_capital_cities():
    assert capital_cities_ru["Италия"] == "Рим"


def test_n_countries():
    assert len(capital_cities_ru) == 193
