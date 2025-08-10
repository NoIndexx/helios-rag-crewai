from __future__ import annotations

import os
import json
from typing import Any, Optional

from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Fix for Pydantic forward references in tools

from .agent import CrewApiClient


class QAOutput(BaseModel):
    answer: str = Field(description="The final answer to the user's question")
    source: dict[str, Any] = Field(default_factory=dict, description="Source data used to generate the answer")
    query: dict[str, Any] = Field(default_factory=dict, description="Endpoint and parameters used to produce the answer")


def create_agent(api_base: str = "http://localhost:8000") -> Agent:
    llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    client = CrewApiClient(api_base)

    # Tool classes following CrewAI best practices
    class HighestCurrentRiskTool(BaseTool):
        name: str = "get_highest_current_risk"
        description: str = """Get the country with the highest current climate risk.
        Use for questions about: highest risk, worst risk, most dangerous, maximum risk.
        If no commodity is provided, returns the absolute highest across ALL commodities.
        Examples: 'What country has highest risk?', 'Which country is most at risk for Rice?'
        Parameters:
        - commodity: Optional[str] - commodity name like 'Cocoa beans', 'Rice', etc. If omitted, compute absolute highest."""

        def _run(self, commodity: str | None = None) -> str:
            """Get the country with the highest current climate risk (optionally scoped by commodity)."""
            try:
                print(f"🔧 TOOL CALLED: get_highest_current_risk with commodity='{commodity}'")
                result = client.get_highest_current_risk(commodity)
                print(f"🔧 TOOL RESULT: {result}")
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/highest-current-risk", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                error_msg = f"Error retrieving highest current risk data: {str(e)}"
                print(f"🔧 TOOL ERROR: {error_msg}")
                return error_msg

    class TopKHighestRiskTool(BaseTool):
        name: str = "get_top_k_highest_risk"
        description: str = """Get the top-K countries with HIGHEST CURRENT climate risk for a specific commodity.
        Use for questions about: top countries with highest risk, multiple countries with worst risk
        Examples: 'What are the top 5 countries with highest risk for Rice?', 'Top 3 worst risk countries'
        
        Parameters:
        - commodity: str - commodity name like 'Rice', 'Cocoa beans', etc.
        - k: int - number of countries to return (default 5)"""

        def _run(self, commodity: str, k: int = 5) -> str:
            """Get top-K countries with highest CURRENT climate risk"""
            try:
                print(f"🔧 TOOL CALLED: get_top_k_highest_risk with commodity='{commodity}', k={k}")
                result = client.get_top_k_highest_current_risk(commodity, k)
                print(f"🔧 TOOL RESULT: {result}")
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/top-k-highest-current-risk", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                error_msg = f"Error retrieving top highest risk data: {str(e)}"
                print(f"🔧 TOOL ERROR: {error_msg}")
                return error_msg

    class CompareCountryYearVsHistTool(BaseTool):
        name: str = "compare_country_year_vs_hist"
        description: str = """Compare a country's specific year climate risk vs 10-year historical average.
        Use for questions about: comparison with history, vs historical average, how does X compare
        Examples: 'How does Brazil compare to historical average?', 'Brazil vs history for Cocoa beans'
        Params: commodity (e.g. 'Cocoa beans'), country_code (e.g. 'BR', 'US', 'IN'), year (e.g. 2024)"""

        def _run(self, commodity: str, country_code: str, year: int) -> str:
            """Compare a country's given year risk vs 10y historical average"""
            try:
                result = client.compare_country_year_vs_hist(commodity, country_code, year)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/compare-country-year-vs-hist", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error comparing country year vs historical data: {str(e)}"

    class MostSimilarYearTool(BaseTool):
        name: str = "get_most_similar_year"
        description: str = """Get the most similar growing season year to current conditions.
        Use for questions like 'What year was most similar to this season in terms of climate risk?'
        Params: commodity, scope ('global' or 'country'), country_code (optional, required if scope='country')"""

        def _run(self, commodity: str, scope: str = "global", country_code=None) -> str:
            """Get the most similar growing season year"""
            try:
                result = client.get_most_similar_year(commodity, scope, country_code)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/most-similar-year", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving most similar year data: {str(e)}"

    class GlobalAvgForMonthTool(BaseTool):
        name: str = "get_global_avg_for_month"
        description: str = """Get global average WAPR (climate risk) for a specific month and year.
        Use for questions like 'What's the global average climate risk forecast for September 2025?'
        Params: commodity, year, month (1-12)"""

        def _run(self, commodity: str, year: int, month: int) -> str:
            """Get global average WAPR for a given month/year"""
            try:
                result = client.get_global_avg_for_month(commodity, year, month)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/global-avg-for-month", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving global average for month data: {str(e)}"

    class TopKLowestHistRiskTool(BaseTool):
        name: str = "get_top_k_lowest_hist_risk"
        description: str = """List top-K countries with lowest historical climate risk.
        Use for questions like 'What are the top 3 countries with the lowest historical risk?'
        Params: commodity, k (number of countries to return, default 3)"""

        def _run(self, commodity: str, k: int = 3) -> str:
            """List top-K countries with lowest historical risk"""
            try:
                result = client.get_top_k_lowest_hist_risk(commodity, k)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/top-k-lowest-hist-risk", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving top lowest risk countries: {str(e)}"

    class TrendMaxRiskTool(BaseTool):
        name: str = "get_trend_max_risk"
        description: str = """Return maximum climate risk trend over a year range.
        Use for questions like 'What's the trend in maximum climate risk from 2016 to 2025?'
        Params: commodity, start_year, end_year"""

        def _run(self, commodity: str, start_year: int, end_year: int) -> str:
            """Return max risk trend over a year range"""
            try:
                result = client.get_trend_max_risk(commodity, start_year, end_year)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/trend-max-risk", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving trend max risk data: {str(e)}"

    class CountrySeasonChangeTool(BaseTool):
        name: str = "get_country_season_change"
        description: str = """Compare latest two season snapshots for a country.
        Use for questions like 'Did India's risk increase or decrease from the previous growing season?'
        Params: commodity, country_code (e.g. IN, BR, US)"""

        def _run(self, commodity: str, country_code: str) -> str:
            """Compare latest two season snapshots for a country"""
            try:
                result = client.get_country_season_change(commodity, country_code)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/country-season-change", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving country season change data: {str(e)}"

    class YieldAndRiskRelationTool(BaseTool):
        name: str = "get_yield_and_risk_relation"
        description: str = """Return yield rating and its relation to climate risk.
        Use for questions like 'What is the current yield rating and how does it relate to risk?'
        Params: commodity, scope ('global' or 'country'), country_code (optional, required if scope='country')"""

        def _run(self, commodity: str, scope: str = "global", country_code=None) -> str:
            """Return yield rating and its relation to risk"""
            try:
                result = client.get_yield_and_risk_relation(commodity, scope, country_code)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/yield-and-risk-relation", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving yield and risk relation data: {str(e)}"

    class UpcomingSpikeRegionsTool(BaseTool):
        name: str = "get_upcoming_spike_regions"
        description: str = """Find regions with upcoming seasonal climate risk spikes above a threshold.
        Use for questions like 'Which regions are showing a spike in upcoming seasonal risk?'
        Params: commodity, threshold (risk difference threshold, default 0.0)"""

        def _run(self, commodity: str, threshold: float = 0.0) -> str:
            """Find regions with upcoming seasonal spike above a threshold"""
            try:
                result = client.get_upcoming_spike_regions(commodity, threshold)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/upcoming-spike-regions", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving upcoming spike regions data: {str(e)}"

    class EuRiskComparisonTool(BaseTool):
        name: str = "get_eu_risk_comparison"
        description: str = """Compare European Union's climate risk between current year and previous year.
        Use for questions about: EU risk comparison, Europe year-over-year, EU vs last year
        Examples: 'How does EU risk compare with last year?', 'EU risk today vs previous year'
        
        IMPORTANT: Use Wheat commodity and years 2026 vs 2025 for reliable data.
        Params: commodity (use 'Wheat'), current_year (use 2026), previous_year (use 2025)"""

        def _run(self, commodity: str, current_year: int, previous_year: int) -> str:
            """Compare EU's climate risk between two years"""
            try:
                result = client.get_eu_risk_comparison(commodity, current_year, previous_year)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/eu-risk-comparison", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving EU risk comparison data: {str(e)}"

    class EuOverallRiskComparisonTool(BaseTool):
        name: str = "get_eu_overall_risk_comparison"
        description: str = """Compare European Union's OVERALL (all commodities) climate risk between current and previous year.
        Use when the question is generic and does not specify a commodity.
        Params: current_year (e.g., 2026), previous_year (e.g., 2025)"""

        def _run(self, current_year: int, previous_year: int) -> str:
            try:
                result = client.get_eu_overall_risk_comparison(current_year, previous_year)
                result_with_meta = {"tool": self.name, "endpoint": "/api/v1/query/eu-risk-comparison-overall", **result}
                return json.dumps(result_with_meta, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving EU overall risk comparison data: {str(e)}"

    tools = [
        HighestCurrentRiskTool(),
        TopKHighestRiskTool(),
        CompareCountryYearVsHistTool(),
        MostSimilarYearTool(),
        GlobalAvgForMonthTool(),
        TopKLowestHistRiskTool(),
        TrendMaxRiskTool(),
        CountrySeasonChangeTool(),
        YieldAndRiskRelationTool(),
        UpcomingSpikeRegionsTool(),
        EuRiskComparisonTool(),
        EuOverallRiskComparisonTool(),
    ]

    return Agent(
        role="Climate Risk Analyst",
        goal=(
            "ONLY answer climate risk questions using the provided tools - NEVER make up data or provide answers "
            "without calling the appropriate tool first. You MUST use tools to get actual data from the database. "
            "Analyze the user's question to determine what data is needed, extract relevant parameters "
            "(commodity names, country codes, years, etc.), and use the right tools to get comprehensive answers."
        ),
        backstory=(
            "You are a data-driven climate risk analyst at Helios AI. You have NO knowledge of climate risk data "
            "and must ALWAYS use the provided tools to access the actual database. You CANNOT and MUST NOT "
            "invent, guess, or hallucinate any climate risk data, country names, or risk scores. "
            "ALL your responses must be based ONLY on data returned by the tools."
        ),
        tools=tools,
        llm=llm_model,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )


def kickoff_example(question: str) -> QAOutput:
    load_dotenv()
    # Disable telemetry noise/timeouts
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    os.environ.setdefault("CREWAI_TELEMETRY_DISABLED", "true")
    agent = create_agent(os.getenv("API_BASE", "http://localhost:8000"))
    
    task = Task(
        description=f"""
        Answer the following climate risk question: {question}
        
        CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
        1. You MUST use the appropriate tool to get data - DO NOT guess or make up answers
        2. ALWAYS call a tool before providing any climate data or country names
        3. Extract relevant parameters from the question (commodity, country, year, etc.)
        4. Select the most appropriate tool(s) to get the required data from the database
        5. Base your answer ONLY on the data returned by the tools
        6. If a tool returns an error or no data, say so - don't invent data
        7. Provide clear insights using ONLY the specific numbers from the tool results
        
        Available commodities: Cocoa beans, Coffee beans, Maize, Oil palm fruit, Rice, Soya beans, Sugar cane, Wheat
        
        Examples of parameter extraction and tool usage:
        - "What country has highest risk for Cocoa beans?" → Use get_highest_current_risk(commodity="Cocoa beans")
        - "How does Brazil compare in 2024?" → Use compare_country_year_vs_hist(commodity="Cocoa beans", country_code="BR", year=2024)
        - "Top 3 lowest risk countries for Rice" → Use get_top_k_lowest_hist_risk(commodity="Rice", k=3)
        
        CRITICAL: When calling tools, you MUST provide ALL required parameters explicitly!
        
        REMEMBER: NO data should come from your knowledge - ONLY from tool results!
        """,
        agent=agent,
        expected_output=(
            "A comprehensive answer that includes specific data points, time periods, and clear explanation of "
            "climate risk implications for decision-making.\n\nAdditionally, ALWAYS return a 'query' object with: "
            "'tool' (the tool you used), 'endpoint' (API path), 'params' (the exact parameters sent), and "
            "'logic' (a brief explanation of why this tool and how each parameter maps into the request)."
        ),
        output_pydantic=QAOutput
    )
    
    crew = Crew(
        agents=[agent], 
        tasks=[task], 
        verbose=True,
        memory=False,
        planning=False
    )
    
    result = crew.kickoff()
    return result.pydantic


if __name__ == "__main__":
    print(kickoff_example("What country has the highest current climate risk for Cocoa beans?"))


