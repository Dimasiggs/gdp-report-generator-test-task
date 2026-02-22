from pydantic import BaseModel, field_validator
from typing import List, Optional


class ReportConfig(BaseModel):
    input_files: List[str]
    report_type: str = "average-gdp"


class GDPRecord(BaseModel):
    """Модель записи данных о ВВП"""
    country: str
    year: Optional[int] = None
    gdp: float

    @field_validator('country')
    @classmethod
    def validate_country_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Country name cannot be empty')
        return v.strip()

    @field_validator('gdp')
    @classmethod
    def validate_gdp_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError('GDP cannot be negative')
        return v


class CountryAverage(BaseModel):
    """Модель результата: страна со средним ВВП"""
    country: str
    average_gdp: float


# class Argument(BaseModel):
#     name: str
#     nargs: Optional[str]
#     required: bool = True
