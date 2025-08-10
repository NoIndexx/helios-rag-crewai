from __future__ import annotations

from typing import Any, Optional

from .database.connection import fetch_all, fetch_one


async def get_highest_current_risk(conn, commodity: Optional[str] = None) -> Optional[dict[str, Any]]:
    params: list[Any] = []
    sql = (
        """
        SELECT ctry.name AS country_name, ctry.code AS country_code,
               com.name AS commodity, byc.this_year_avg_wapr, byc.hist_avg_wapr, byc.year
        FROM climate_risk_by_country byc
        JOIN countries ctry ON ctry.id = byc.country_id
        JOIN commodities com ON com.id = byc.commodity_id
        WHERE byc.this_year_avg_wapr IS NOT NULL
        """
    )
    if commodity:
        sql += " AND com.name = ?"
        params.append(commodity)
    # Order by highest current risk
    sql += " ORDER BY byc.this_year_avg_wapr DESC, byc.year DESC LIMIT 1"
    return await fetch_one(conn, sql, tuple(params))


async def compare_country_year_vs_hist(conn, commodity: str, country_code: str, year: int) -> Optional[dict[str, Any]]:
    sql = (
        """
        SELECT com.name AS commodity, ctry.code AS country_code, ctry.name AS country_name,
               byc.hist_avg_wapr, byc.this_year_avg_wapr
        FROM climate_risk_by_country byc
        JOIN commodities com ON com.id = byc.commodity_id
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE com.name = ? AND ctry.code = ? AND byc.year = ?
        """
    )
    row = await fetch_one(conn, sql, (commodity, country_code, year))
    if not row:
        return None
    hist = row.get("hist_avg_wapr")
    curr = row.get("this_year_avg_wapr")
    if hist is None or curr is None:
        return row | {"delta": None, "pct": None}
    delta = float(curr) - float(hist)
    pct = (delta / float(hist) * 100.0) if float(hist) != 0 else None
    return row | {"delta": delta, "pct": pct}


async def get_most_similar_year(conn, commodity: str, scope: str = "global", country_code: Optional[str] = None) -> Optional[dict[str, Any]]:
    if scope == "country" and country_code:
        sql = (
            """
            SELECT com.name AS commodity, ctry.code AS country_code, ctry.name AS country_name,
                   m.*
            FROM most_similar_year m
            JOIN commodities com ON com.id = m.commodity_id
            JOIN countries ctry ON ctry.id = m.country_id
            WHERE com.name = ? AND ctry.code = ?
            ORDER BY this_growing_season_year DESC LIMIT 1
            """
        )
        return await fetch_one(conn, sql, (commodity, country_code))
    # global
    sql = (
        """
        SELECT com.name AS commodity, ctry.code AS country_code, ctry.name AS country_name,
               m.*
        FROM most_similar_year m
        JOIN commodities com ON com.id = m.commodity_id
        JOIN countries ctry ON ctry.id = m.country_id
        WHERE com.name = ? AND ctry.code = 'GLB'
        ORDER BY this_growing_season_year DESC LIMIT 1
        """
    )
    return await fetch_one(conn, sql, (commodity,))


async def get_global_avg_for_month(conn, commodity: str, year: int, month: int) -> Optional[dict[str, Any]]:
    # Get global average climate risk data for a specific year (month is approximated to year)
    sql = (
        """
        SELECT r.hist_avg_wapr as monthly_avg_wapr, r.hist_max_wapr, r.year
        FROM risk_global_avg_max r
        JOIN commodities com ON com.id = r.commodity_id
        JOIN countries ctry ON ctry.id = r.country_id
        WHERE com.name = ? AND ctry.code = 'GLB' AND r.year = ?
        """
    )
    row = await fetch_one(conn, sql, (commodity, year))
    if not row:
        return None
    return {
        "commodity": commodity,
        "year": year,
        "month": month,
        "global_avg_wapr": row.get("monthly_avg_wapr"),
        "global_max_wapr": row.get("hist_max_wapr"),
        "region": "Global"
    }


async def get_top_k_lowest_hist_risk(conn, commodity: str, k: int = 3):
    sql = (
        """
        SELECT ctry.name AS country_name, ctry.code AS country_code, byc.hist_avg_wapr
        FROM climate_risk_by_country byc
        JOIN commodities com ON com.id = byc.commodity_id
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE com.name = ?
        ORDER BY (byc.hist_avg_wapr IS NULL) ASC, byc.hist_avg_wapr ASC
        LIMIT ?
        """
    )
    return await fetch_all(conn, sql, (commodity, k))


async def get_top_k_highest_current_risk(conn, commodity: str, k: int = 5):
    """Get top-K countries with highest CURRENT climate risk (this_year_avg_wapr)"""
    sql = (
        """
        SELECT ctry.name AS country_name, ctry.code AS country_code,
               com.name AS commodity, byc.this_year_avg_wapr, byc.hist_avg_wapr, byc.year
        FROM climate_risk_by_country byc
        JOIN countries ctry ON ctry.id = byc.country_id
        JOIN commodities com ON com.id = byc.commodity_id
        WHERE byc.this_year_avg_wapr IS NOT NULL AND com.name = ?
        ORDER BY byc.this_year_avg_wapr DESC, byc.year DESC 
        LIMIT ?
        """
    )
    return await fetch_all(conn, sql, (commodity, k))


async def get_trend_max_risk(conn, commodity: str, start_year: int, end_year: int):
    sql = (
        """
        SELECT year, hist_max_wapr
        FROM risk_global_avg_max r
        JOIN commodities com ON com.id = r.commodity_id
        WHERE com.name = ? AND r.year BETWEEN ? AND ?
        ORDER BY r.year ASC
        """
    )
    return await fetch_all(conn, sql, (commodity, start_year, end_year))


async def get_country_season_change(conn, country_code: str, commodity: str) -> Optional[dict[str, Any]]:
    # Compare current year vs historical average to determine trend
    sql = (
        """
        SELECT byc.year, byc.this_year_avg_wapr, byc.hist_avg_wapr
        FROM climate_risk_by_country byc
        JOIN commodities com ON com.id = byc.commodity_id
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE com.name = ? AND ctry.code = ?
        ORDER BY byc.year DESC
        LIMIT 2
        """
    )
    rows = await fetch_all(conn, sql, (commodity, country_code))
    if len(rows) < 1:
        return None
    
    latest = rows[0]
    current_wapr = latest.get("this_year_avg_wapr") 
    hist_avg = latest.get("hist_avg_wapr")
    
    if current_wapr is None or hist_avg is None:
        return None
        
    # If we have 2 years, compare them directly
    if len(rows) >= 2:
        prev = rows[1]
        prev_wapr = prev.get("this_year_avg_wapr")
        if prev_wapr is not None:
            delta = float(current_wapr) - float(prev_wapr)
            direction = "increase" if delta > 0 else ("decrease" if delta < 0 else "no_change")
        else:
            # Fallback to current vs historical average
            delta = float(current_wapr) - float(hist_avg)
            direction = "increase" if delta > 0 else ("decrease" if delta < 0 else "no_change")
            prev_wapr = hist_avg
    else:
        # Only one year, compare current vs historical average
        delta = float(current_wapr) - float(hist_avg)
        direction = "increase" if delta > 0 else ("decrease" if delta < 0 else "no_change")
        prev_wapr = hist_avg
    
    return {
        "commodity": commodity,
        "country_code": country_code,
        "current_year": latest.get("year"),
        "current_wapr": float(current_wapr),
        "previous_wapr": float(prev_wapr),
        "delta": delta,
        "direction": direction
    }


async def get_yield_and_risk_relation(conn, commodity: str, scope: str = "global", country_code: Optional[str] = None):
    if scope == "country" and country_code:
        sql = (
            """
            SELECT m.yield_rating, m.total_yield, m.total_yield_unit,
                   g.hist_avg_wapr, g.hist_max_wapr, m.this_growing_season_year
            FROM most_similar_year m
            JOIN commodities com ON com.id = m.commodity_id
            LEFT JOIN risk_global_avg_max g
              ON g.commodity_id = m.commodity_id AND g.country_id = m.country_id AND g.year = m.this_growing_season_year
            JOIN countries ctry ON ctry.id = m.country_id
            WHERE com.name = ? AND ctry.code = ?
            ORDER BY m.this_growing_season_year DESC LIMIT 1
            """
        )
        return await fetch_one(conn, sql, (commodity, country_code))
    # global
    sql = (
        """
        SELECT m.yield_rating, m.total_yield, m.total_yield_unit,
               g.hist_avg_wapr, g.hist_max_wapr, m.this_growing_season_year
        FROM most_similar_year m
        JOIN commodities com ON com.id = m.commodity_id
        LEFT JOIN risk_global_avg_max g
          ON g.commodity_id = m.commodity_id AND g.country_id = m.country_id AND g.year = m.this_growing_season_year
        JOIN countries ctry ON ctry.id = m.country_id
        WHERE com.name = ? AND ctry.code = 'GLB'
        ORDER BY m.this_growing_season_year DESC LIMIT 1
        """
    )
    return await fetch_one(conn, sql, (commodity,))


async def get_upcoming_spike_regions(conn, commodity: str, threshold: float = 0.0):
    sql = (
        """
        SELECT ctry.name AS country_name, ctry.code AS country_code,
               r.avg_risk_score_diff, r.upcoming_year_risk_score
        FROM risk_compared_hist_box r
        JOIN commodities com ON com.id = r.commodity_id
        JOIN countries ctry ON ctry.id = r.country_id
        WHERE com.name = ? AND r.upcoming_season = 1 AND r.avg_risk_score_diff IS NOT NULL
          AND r.avg_risk_score_diff > ?
        ORDER BY r.avg_risk_score_diff DESC
        """
    )
    return await fetch_all(conn, sql, (commodity, threshold))


async def get_eu_risk_comparison(conn, commodity: str, current_year: int, previous_year: int) -> Optional[dict[str, Any]]:
    """Compare EU's climate risk between current year and previous year"""
    # Get current year data for EU
    current_sql = """
        SELECT byc.this_year_avg_wapr as avg_wapr
        FROM climate_risk_by_country byc
        JOIN commodities com ON com.id = byc.commodity_id
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE com.name = ? AND byc.year = ? AND ctry.code = 'EU'
    """
    
    current_row = await fetch_one(conn, current_sql, (commodity, current_year))
    
    # Get previous year data for EU
    previous_sql = """
        SELECT byc.this_year_avg_wapr as avg_wapr
        FROM climate_risk_by_country byc
        JOIN commodities com ON com.id = byc.commodity_id
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE com.name = ? AND byc.year = ? AND ctry.code = 'EU'
    """
    
    previous_row = await fetch_one(conn, previous_sql, (commodity, previous_year))
    
    if not current_row or not previous_row:
        return None
        
    current_wapr = current_row.get("avg_wapr")
    previous_wapr = previous_row.get("avg_wapr")
    
    if current_wapr is None or previous_wapr is None:
        return None
    
    # Calculate change
    delta = float(current_wapr) - float(previous_wapr)
    pct_change = (delta / float(previous_wapr) * 100.0) if float(previous_wapr) != 0 else None
    
    return {
        "commodity": commodity,
        "region": "European Union",
        "current_year": current_year,
        "previous_year": previous_year,
        "current_avg_wapr": float(current_wapr),
        "previous_avg_wapr": float(previous_wapr),
        "delta": delta,
        "percent_change": pct_change,
        "trend": "increased" if delta > 0 else "decreased" if delta < 0 else "unchanged"
    }


async def get_eu_overall_risk_comparison(conn, current_year: int, previous_year: int) -> Optional[dict[str, Any]]:
    """Aggregate EU risk across ALL commodities by averaging current WAPR.
    Returns a comparison between two years.
    """
    # Current year overall
    current_sql = (
        """
        SELECT AVG(byc.this_year_avg_wapr) as avg_wapr
        FROM climate_risk_by_country byc
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE ctry.code = 'EU' AND byc.year = ? AND byc.this_year_avg_wapr IS NOT NULL
        """
    )
    previous_sql = (
        """
        SELECT AVG(byc.this_year_avg_wapr) as avg_wapr
        FROM climate_risk_by_country byc
        JOIN countries ctry ON ctry.id = byc.country_id
        WHERE ctry.code = 'EU' AND byc.year = ? AND byc.this_year_avg_wapr IS NOT NULL
        """
    )

    current_row = await fetch_one(conn, current_sql, (current_year,))
    previous_row = await fetch_one(conn, previous_sql, (previous_year,))

    if not current_row or not previous_row:
        return None

    current_wapr = current_row.get("avg_wapr")
    previous_wapr = previous_row.get("avg_wapr")

    if current_wapr is None or previous_wapr is None:
        return None

    delta = float(current_wapr) - float(previous_wapr)
    pct_change = (delta / float(previous_wapr) * 100.0) if float(previous_wapr) != 0 else None

    return {
        "region": "European Union",
        "current_year": current_year,
        "previous_year": previous_year,
        "current_overall_avg_wapr": float(current_wapr),
        "previous_overall_avg_wapr": float(previous_wapr),
        "delta": delta,
        "percent_change": pct_change,
        "trend": "increased" if delta > 0 else "decreased" if delta < 0 else "unchanged"
    }


