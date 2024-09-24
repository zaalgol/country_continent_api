# app/crud/__init__.py

# This file makes it easier to import CRUD functions elsewhere in the project
from .crud import (
    get_country_by_name, get_countries, create_country, update_country, delete_country,
    get_continent_by_code, get_continents, create_continent, update_continent, delete_continent
)
