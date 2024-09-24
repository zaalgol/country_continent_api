from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Continent(Base):
    """
    SQLAlchemy model for the 'continents' table.
    Represents a continent with a code and name.
    """
    __tablename__ = 'continents'

    code = Column(String(2), primary_key=True, comment='Continent code')
    name = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to countries
    countries = relationship("Country", back_populates="continent")

    # Adding index
    table_args__ = (
        Index('idx_continent_name', 'name'),
    )

class Country(Base):
    """
    SQLAlchemy model for the 'countries' table.
    Represents a country with various attributes and a foreign key to a continent.
    """
    __tablename__ = 'countries'

    code = Column(String(2), primary_key=True, comment='Two-letter country code (ISO 3166-1 alpha-2)')
    name = Column(String(255), nullable=False, comment='English country name')
    full_name = Column(String(255), nullable=False, comment='Full English country name')
    iso3 = Column(String(3), nullable=False, comment='Three-letter country code (ISO 3166-1 alpha-3)')
    number = Column(Integer, nullable=False, comment='Three-digit country number (ISO 3166-1 numeric)')
    continent_code = Column(String(2), ForeignKey('continents.code'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to continent
    continent = relationship("Continent", back_populates="countries")

    # Adding indexes
    __table_args__ = (
        Index('idx_country_name', 'name'),
        Index('idx_country_continent', 'continent_code'),
    )