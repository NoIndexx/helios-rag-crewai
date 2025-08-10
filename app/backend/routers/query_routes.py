from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..database.connection import get_db
from .. import queries
from ..schemas import (
    HighestRiskRequest,
    CountryYearVsHistRequest,
    SimilarYearRequest,
    GlobalMonthAvgRequest,
    TopKRequest,
    TrendRequest,
    CountrySeasonChangeRequest,
    YieldRiskRequest,
    UpcomingSpikeRequest,
    EuRiskComparisonRequest,
    EuOverallRiskComparisonRequest,
    AnswerResponse,
)


router = APIRouter(prefix="/api/v1/query", tags=["query"])


@router.post("/highest-current-risk", response_model=AnswerResponse)
async def highest_current_risk(req: HighestRiskRequest, db=Depends(get_db)):
    result = await queries.get_highest_current_risk(db, req.commodity)
    if result is None:
        raise HTTPException(status_code=404, detail="No data available")
    return {"answer": result, "params": req.model_dump()}


@router.post("/compare-country-year-vs-hist", response_model=AnswerResponse)
async def compare_country_year_vs_hist(req: CountryYearVsHistRequest, db=Depends(get_db)):
    result = await queries.compare_country_year_vs_hist(db, req.commodity, req.country_code, req.year)
    if result is None:
        raise HTTPException(status_code=404, detail="No data available")
    return {"answer": result, "params": req.model_dump()}


@router.post("/most-similar-year", response_model=AnswerResponse)
async def most_similar_year(req: SimilarYearRequest, db=Depends(get_db)):
    result = await queries.get_most_similar_year(db, req.commodity, req.scope, req.country_code)
    if result is None:
        raise HTTPException(status_code=404, detail="No data available")
    return {"answer": result, "params": req.model_dump()}


@router.post("/global-avg-for-month", response_model=AnswerResponse)
async def global_avg_for_month(req: GlobalMonthAvgRequest, db=Depends(get_db)):
    result = await queries.get_global_avg_for_month(db, req.commodity, req.year, req.month)
    # result contains keys: global_avg_wapr, global_max_wapr, year, month, region
    if result is None or result.get("global_avg_wapr") is None:
        raise HTTPException(status_code=404, detail="No data available for given month")
    return {"answer": result, "params": req.model_dump()}


@router.post("/top-k-lowest-hist-risk", response_model=AnswerResponse)
async def top_k_lowest_hist_risk(req: TopKRequest, db=Depends(get_db)):
    result = await queries.get_top_k_lowest_hist_risk(db, req.commodity, req.k)
    return {"answer": result, "params": req.model_dump()}


@router.post("/top-k-highest-current-risk", response_model=AnswerResponse)
async def top_k_highest_current_risk(req: TopKRequest, db=Depends(get_db)):
    result = await queries.get_top_k_highest_current_risk(db, req.commodity, req.k)
    return {"answer": result, "params": req.model_dump()}


@router.post("/trend-max-risk", response_model=AnswerResponse)
async def trend_max_risk(req: TrendRequest, db=Depends(get_db)):
    result = await queries.get_trend_max_risk(db, req.commodity, req.start_year, req.end_year)
    return {"answer": result, "params": req.model_dump()}


@router.post("/country-season-change", response_model=AnswerResponse)
async def country_season_change(req: CountrySeasonChangeRequest, db=Depends(get_db)):
    result = await queries.get_country_season_change(db, req.country_code, req.commodity)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data to compare")
    return {"answer": result, "params": req.model_dump()}


@router.post("/yield-and-risk-relation", response_model=AnswerResponse)
async def yield_and_risk_relation(req: YieldRiskRequest, db=Depends(get_db)):
    result = await queries.get_yield_and_risk_relation(db, req.commodity, req.scope, req.country_code)
    if result is None:
        raise HTTPException(status_code=404, detail="No data available")
    return {"answer": result, "params": req.model_dump()}


@router.post("/upcoming-spike-regions", response_model=AnswerResponse)
async def upcoming_spike_regions(req: UpcomingSpikeRequest, db=Depends(get_db)):
    result = await queries.get_upcoming_spike_regions(db, req.commodity, req.threshold)
    return {"answer": result, "params": req.model_dump()}


@router.post("/eu-risk-comparison", response_model=AnswerResponse)
async def eu_risk_comparison(req: EuRiskComparisonRequest, db=Depends(get_db)):
    result = await queries.get_eu_risk_comparison(db, req.commodity, req.current_year, req.previous_year)
    if result is None:
        raise HTTPException(status_code=404, detail="No data available for EU countries")
    return {"answer": result, "params": req.model_dump()}


@router.post("/eu-risk-comparison-overall", response_model=AnswerResponse)
async def eu_risk_comparison_overall(req: EuOverallRiskComparisonRequest, db=Depends(get_db)):
    result = await queries.get_eu_overall_risk_comparison(db, req.current_year, req.previous_year)
    if result is None:
        raise HTTPException(status_code=404, detail="No overall data available for EU")
    return {"answer": result, "params": req.model_dump()}


