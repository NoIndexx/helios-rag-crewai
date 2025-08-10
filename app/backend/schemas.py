from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HighestRiskRequest(BaseModel):
    commodity: Optional[str] = Field(default=None)


class CountryYearVsHistRequest(BaseModel):
    commodity: str
    country_code: str
    year: int


class SimilarYearRequest(BaseModel):
    commodity: str
    scope: str = Field(default="global")
    country_code: Optional[str] = None


class GlobalMonthAvgRequest(BaseModel):
    commodity: str
    year: int
    month: int


class TopKRequest(BaseModel):
    commodity: str
    k: int = Field(default=3, ge=1, le=50)


class TrendRequest(BaseModel):
    commodity: str
    start_year: int
    end_year: int


class CountrySeasonChangeRequest(BaseModel):
    commodity: str
    country_code: str


class YieldRiskRequest(BaseModel):
    commodity: str
    scope: str = Field(default="global")
    country_code: Optional[str] = None


class UpcomingSpikeRequest(BaseModel):
    commodity: str
    threshold: float = 0.0


class EuRiskComparisonRequest(BaseModel):
    commodity: str
    current_year: int
    previous_year: int


class AnswerResponse(BaseModel):
    answer: Any
    params: Dict[str, Any]


