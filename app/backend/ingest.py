from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import httpx

from dotenv import load_dotenv
from .database.connection import get_db, execute_script, execute, fetch_one
from .utils.config import ENDPOINTS, SCHEMA_PATH
from .utils.common import to_bool, safe_float, safe_int


async def ensure_schema() -> None:
    async for conn in get_db():
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            await execute_script(conn, f.read())


async def get_or_create_commodity(conn, name: str) -> int:
    row = await fetch_one(conn, "SELECT id FROM commodities WHERE name = ?", (name,))
    if row:
        return int(row["id"])
    await execute(conn, "INSERT INTO commodities(name, slug) VALUES(?, ?)", (name, name.lower().replace(" ", "_")))
    row = await fetch_one(conn, "SELECT id FROM commodities WHERE name = ?", (name,))
    return int(row["id"]) if row else 0


async def get_or_create_country(conn, code: str, name: str | None) -> int:
    row = await fetch_one(conn, "SELECT id FROM countries WHERE code = ?", (code,))
    if row:
        return int(row["id"])
    try:
        await execute(conn, "INSERT INTO countries(name, code) VALUES(?, ?)", (name or code, code))
    except Exception:
        # Another concurrency path inserted it; fetch again
        pass
    row = await fetch_one(conn, "SELECT id FROM countries WHERE code = ?", (code,))
    return int(row["id"]) if row else 0


async def ingest_endpoint(name: str, url: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    now = datetime.now(timezone.utc).isoformat()

    async for conn in get_db():
        # raw log (best-effort, ignore duplicates by redis_key and endpoint_name)
        for item in data:
            try:
                await execute(
                    conn,
                    "INSERT INTO raw_ingest(endpoint_name, redis_key, payload, ingested_at) VALUES(?,?,?,?)",
                    (
                        name,
                        item.get("redis_key"),
                        json.dumps(item, ensure_ascii=False),
                        now,
                    ),
                )
            except Exception:
                pass

        if name == "climate_risk_by_country":
            for r in data:
                commodity_id = await get_or_create_commodity(conn, r.get("commodity"))
                country_id = await get_or_create_country(conn, r.get("country_code"), r.get("country_name"))
                await execute(
                    conn,
                    """
                    INSERT INTO climate_risk_by_country(
                      redis_key, commodity_id, country_id, year, hist_avg_wapr, this_year_avg_wapr,
                      current_season, most_recent_season, upcoming_season, just_ended_season
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(commodity_id, country_id, year) DO UPDATE SET
                      redis_key=excluded.redis_key,
                      hist_avg_wapr=excluded.hist_avg_wapr,
                      this_year_avg_wapr=excluded.this_year_avg_wapr,
                      current_season=excluded.current_season,
                      most_recent_season=excluded.most_recent_season,
                      upcoming_season=excluded.upcoming_season,
                      just_ended_season=excluded.just_ended_season
                    """,
                    (
                        r.get("redis_key"),
                        commodity_id,
                        country_id,
                        safe_int(r.get("year")),
                        safe_float(r.get("hist_avg_wapr")),
                        safe_float(r.get("this_year_avg_wapr")),
                        to_bool(r.get("current_season")),
                        to_bool(r.get("most_recent_season")),
                        to_bool(r.get("upcoming_season")),
                        to_bool(r.get("just_ended_season")),
                    ),
                )

        elif name == "risk_compared_hist_box":
            for r in data:
                commodity_id = await get_or_create_commodity(conn, r.get("commodity"))
                country_id = await get_or_create_country(conn, r.get("country_code"), r.get("country_name"))
                await execute(
                    conn,
                    """
                    INSERT INTO risk_compared_hist_box(
                      redis_key, commodity_id, country_id, hist_risk_score, this_year_risk_score,
                      avg_risk_score_diff, upcoming_year_risk_score, risk_level, current_season,
                      just_ended_season, upcoming_season
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(commodity_id, country_id) DO UPDATE SET
                      redis_key=excluded.redis_key,
                      hist_risk_score=excluded.hist_risk_score,
                      this_year_risk_score=excluded.this_year_risk_score,
                      avg_risk_score_diff=excluded.avg_risk_score_diff,
                      upcoming_year_risk_score=excluded.upcoming_year_risk_score,
                      risk_level=excluded.risk_level,
                      current_season=excluded.current_season,
                      just_ended_season=excluded.just_ended_season,
                      upcoming_season=excluded.upcoming_season
                    """,
                    (
                        r.get("redis_key"),
                        commodity_id,
                        country_id,
                        safe_float(r.get("hist_risk_score")),
                        safe_float(r.get("this_year_risk_score")),
                        safe_float(r.get("avg_risk_score_diff")),
                        safe_float(r.get("upcoming_year_risk_score")),
                        r.get("risk_level"),
                        to_bool(r.get("current_season")),
                        to_bool(r.get("just_ended_season")),
                        to_bool(r.get("upcoming_season")),
                    ),
                )

        elif name == "risk_current_vs_hist":
            for r in data:
                commodity_id = await get_or_create_commodity(conn, r.get("commodity"))
                # Endpoint has country_name but no country_code; derive a short code from the name
                country_code = (r.get("country_name") or "").upper()[:3] or "GLB"
                country_id = await get_or_create_country(conn, country_code, r.get("country_name"))
                await execute(
                    conn,
                    """
                    INSERT INTO risk_current_vs_hist(
                      redis_key, commodity_id, country_id, hist_wapr, this_year_wapr, std_upper, std_lower,
                      date_on, season_status
                    ) VALUES(?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(commodity_id, country_id, date_on) DO UPDATE SET
                      redis_key=excluded.redis_key,
                      hist_wapr=excluded.hist_wapr,
                      this_year_wapr=excluded.this_year_wapr,
                      std_upper=excluded.std_upper,
                      std_lower=excluded.std_lower,
                      season_status=excluded.season_status
                    """,
                    (
                        r.get("redis_key"),
                        commodity_id,
                        country_id,
                        safe_float(r.get("hist_wapr")),
                        safe_float(r.get("this_year_wapr")),
                        safe_float(r.get("std_upper")),
                        safe_float(r.get("std_lower")),
                        r.get("date_on"),
                        r.get("season_status"),
                    ),
                )

        elif name == "risk_global_avg_max":
            for r in data:
                commodity_id = await get_or_create_commodity(conn, r.get("commodity"))
                # country_code may be missing; default to GLB (Global)
                code = r.get("country_code") or "GLB"
                country_id = await get_or_create_country(conn, code, r.get("country_name") or "Global")
                await execute(
                    conn,
                    """
                    INSERT INTO risk_global_avg_max(
                      redis_key, commodity_id, country_id, hist_max_wapr, hist_avg_wapr, year,
                      current_season, past_season, upcoming_season
                    ) VALUES(?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(commodity_id, country_id, year) DO UPDATE SET
                      redis_key=excluded.redis_key,
                      hist_max_wapr=excluded.hist_max_wapr,
                      hist_avg_wapr=excluded.hist_avg_wapr,
                      current_season=excluded.current_season,
                      past_season=excluded.past_season,
                      upcoming_season=excluded.upcoming_season
                    """,
                    (
                        r.get("redis_key"),
                        commodity_id,
                        country_id,
                        safe_float(r.get("hist_max_wapr")),
                        safe_float(r.get("hist_avg_wapr")),
                        safe_int(r.get("year")),
                        to_bool(r.get("current_season")),
                        to_bool(r.get("past_season")),
                        to_bool(r.get("upcoming_season")),
                    ),
                )

        elif name == "most_similar_year":
            for r in data:
                commodity_id = await get_or_create_commodity(conn, r.get("commodity"))
                code = r.get("country_code") or "GLB"
                country_id = await get_or_create_country(conn, code, r.get("country_name") or "Global")
                await execute(
                    conn,
                    """
                    INSERT INTO most_similar_year(
                      redis_key, commodity_id, country_id, most_similar_growing_season_year,
                      hist_avg_wapr_of_most_similar_year, risk_category, star_rating, total_production,
                      total_area_harvested, current_season, upcoming_season, just_ended_season,
                      this_growing_season_year, total_yield, total_yield_unit, yield_rating,
                      total_production_unit, total_area_harvested_unit
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(commodity_id, country_id, this_growing_season_year) DO UPDATE SET
                      redis_key=excluded.redis_key,
                      most_similar_growing_season_year=excluded.most_similar_growing_season_year,
                      hist_avg_wapr_of_most_similar_year=excluded.hist_avg_wapr_of_most_similar_year,
                      risk_category=excluded.risk_category,
                      star_rating=excluded.star_rating,
                      total_production=excluded.total_production,
                      total_area_harvested=excluded.total_area_harvested,
                      current_season=excluded.current_season,
                      upcoming_season=excluded.upcoming_season,
                      just_ended_season=excluded.just_ended_season,
                      total_yield=excluded.total_yield,
                      total_yield_unit=excluded.total_yield_unit,
                      yield_rating=excluded.yield_rating,
                      total_production_unit=excluded.total_production_unit,
                      total_area_harvested_unit=excluded.total_area_harvested_unit
                    """,
                    (
                        r.get("redis_key"),
                        commodity_id,
                        country_id,
                        safe_int(r.get("most_similar_growing_season_year")),
                        safe_float(r.get("hist_avg_wapr_of_most_similar_year")),
                        r.get("risk_category"),
                        safe_int(r.get("star_rating")),
                        safe_float(r.get("total_production")),
                        safe_float(r.get("total_area_harvested")),
                        to_bool(r.get("current_season")),
                        to_bool(r.get("upcoming_season")),
                        to_bool(r.get("just_ended_season")),
                        safe_int(r.get("this_growing_season_year")),
                        safe_float(r.get("total_yield")),
                        r.get("total_yield_unit"),
                        r.get("yield_rating"),
                        r.get("total_production_unit"),
                        r.get("total_area_harvested_unit"),
                    ),
                )


async def main() -> None:
    load_dotenv()
    await ensure_schema()
    # Run sequentially to avoid SQLite write locks
    for name, url in ENDPOINTS.items():
        await ingest_endpoint(name, url)


if __name__ == "__main__":
    asyncio.run(main())


