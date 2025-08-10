from __future__ import annotations

from typing import Any, Optional

import httpx


class CrewApiClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=20.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            return r.json()

    # Tools (single agent with multiple tools)
    def get_highest_current_risk(self, commodity: Optional[str] = None) -> dict[str, Any]:
        return self.post("/api/v1/query/highest-current-risk", {"commodity": commodity})

    def compare_country_year_vs_hist(self, commodity: str, country_code: str, year: int) -> dict[str, Any]:
        return self.post("/api/v1/query/compare-country-year-vs-hist", {"commodity": commodity, "country_code": country_code, "year": year})

    def get_most_similar_year(self, commodity: str, scope: str = "global", country_code: Optional[str] = None) -> dict[str, Any]:
        return self.post("/api/v1/query/most-similar-year", {"commodity": commodity, "scope": scope, "country_code": country_code})

    def get_global_avg_for_month(self, commodity: str, year: int, month: int) -> dict[str, Any]:
        return self.post("/api/v1/query/global-avg-for-month", {"commodity": commodity, "year": year, "month": month})

    def get_top_k_lowest_hist_risk(self, commodity: str, k: int = 3) -> dict[str, Any]:
        return self.post("/api/v1/query/top-k-lowest-hist-risk", {"commodity": commodity, "k": k})

    def get_top_k_highest_current_risk(self, commodity: str, k: int = 5) -> dict[str, Any]:
        return self.post("/api/v1/query/top-k-highest-current-risk", {"commodity": commodity, "k": k})

    def get_trend_max_risk(self, commodity: str, start_year: int, end_year: int) -> dict[str, Any]:
        return self.post("/api/v1/query/trend-max-risk", {"commodity": commodity, "start_year": start_year, "end_year": end_year})

    def get_trend_max_risk_overall(self, start_year: int, end_year: int) -> dict[str, Any]:
        return self.post("/api/v1/query/trend-max-risk-overall", {"start_year": start_year, "end_year": end_year})

    def get_country_season_change(self, commodity: str, country_code: str) -> dict[str, Any]:
        return self.post("/api/v1/query/country-season-change", {"commodity": commodity, "country_code": country_code})

    def get_country_season_change_overall(self, country_code: str) -> dict[str, Any]:
        return self.post("/api/v1/query/country-season-change-overall", {"country_code": country_code})

    def get_yield_and_risk_relation(self, commodity: str, scope: str = "global", country_code: Optional[str] = None) -> dict[str, Any]:
        return self.post("/api/v1/query/yield-and-risk-relation", {"commodity": commodity, "scope": scope, "country_code": country_code})

    def get_upcoming_spike_regions(self, commodity: str, threshold: float = 0.0) -> dict[str, Any]:
        return self.post("/api/v1/query/upcoming-spike-regions", {"commodity": commodity, "threshold": threshold})

    def get_eu_risk_comparison(self, commodity: str, current_year: int, previous_year: int) -> dict[str, Any]:
        return self.post("/api/v1/query/eu-risk-comparison", {"commodity": commodity, "current_year": current_year, "previous_year": previous_year})

    def get_eu_overall_risk_comparison(self, current_year: int, previous_year: int) -> dict[str, Any]:
        return self.post("/api/v1/query/eu-risk-comparison-overall", {"current_year": current_year, "previous_year": previous_year})


