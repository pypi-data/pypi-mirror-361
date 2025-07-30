from mgimo.data import capital_cities_by_country


def test_capital_cities():
    assert capital_cities_by_country["ru"]["Италия"] == "Рим"


def test_n_countries():
    assert len(capital_cities_by_country["ru"]) == 193
