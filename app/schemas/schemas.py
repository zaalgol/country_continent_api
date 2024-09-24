# app/schemas/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CountryBase(BaseModel):
    """
    Base schema for Country, containing fields common to all schemas.
    """
    code: str
    name: str
    full_name: str
    iso3: str
    number: int
    continent_code: str

class CountryCreate(CountryBase):
    """
    Schema for creating a new Country.
    """
    pass

class CountryUpdate(BaseModel):
    """
    Schema for updating an existing Country.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    full_name: Optional[str] = None
    iso3: Optional[str] = None
    number: Optional[int] = None
    continent_code: Optional[str] = None

class CountryOut(CountryBase):
    """
    Schema for returning Country data, including the updated_at timestamp.
    """
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class ContinentBase(BaseModel):
    """
    Base schema for Continent, containing fields common to all schemas.
    """
    code: str
    name: str

class ContinentCreate(ContinentBase):
    """
    Schema for creating a new Continent.
    """
    pass

class ContinentUpdate(BaseModel):
    """
    Schema for updating an existing Continent.
    """
    name: Optional[str] = None

class ContinentOut(ContinentBase):
    """
    Schema for returning Continent data, including the updated_at timestamp.
    """
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2
