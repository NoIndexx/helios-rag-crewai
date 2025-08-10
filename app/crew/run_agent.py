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


def create_agent(api_base: str = "http://localhost:8000") -> Agent:
    llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    client = CrewApiClient(api_base)

    # Tool classes following CrewAI best practices
    class HighestCurrentRiskTool(BaseTool):
        name: str = "get_highest_current_risk"
        description: str = """Get the country with the highest current climate risk.
        Use for questions about: highest risk, worst risk, most dangerous, maximum risk
        Examples: 'What country has highest risk?', 'Which country is most at risk for Cocoa beans?'
        Params: commodity (optional) - specify commodity name like 'Cocoa beans', 'Rice', etc."""

        def _run(self, commodity=None) -> str:
            """Get the country with the highest current climate risk for a given commodity"""
            try:
                result = client.get_highest_current_risk(commodity)
                return json.dumps(result, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving highest current risk data: {str(e)}"

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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
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
                return json.dumps(result, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving upcoming spike regions data: {str(e)}"

    class EuRiskComparisonTool(BaseTool):
        name: str = "get_eu_risk_comparison"
        description: str = """Compare European Union's climate risk between current year and previous year.
        Use for questions about: EU risk comparison, Europe year-over-year, EU vs last year
        Examples: 'How does EU risk compare with last year?', 'EU risk today vs previous year'
        Params: commodity (e.g. 'Cocoa beans'), current_year (e.g. 2025), previous_year (e.g. 2024)"""

        def _run(self, commodity: str, current_year: int, previous_year: int) -> str:
            """Compare EU's climate risk between two years"""
            try:
                result = client.get_eu_risk_comparison(commodity, current_year, previous_year)
                return json.dumps(result, ensure_ascii=False)
            except Exception as e:
                return f"Error retrieving EU risk comparison data: {str(e)}"

    tools = [
        HighestCurrentRiskTool(),
        CompareCountryYearVsHistTool(),
        MostSimilarYearTool(),
        GlobalAvgForMonthTool(),
        TopKLowestHistRiskTool(),
        TrendMaxRiskTool(),
        CountrySeasonChangeTool(),
        YieldAndRiskRelationTool(),
        UpcomingSpikeRegionsTool(),
        EuRiskComparisonTool(),
    ]

    return Agent(
        role="Climate Risk Analyst",
        goal=(
            "Answer climate risk questions by intelligently selecting and using the appropriate tools. "
            "Analyze the user's question to determine what data is needed, extract relevant parameters "
            "(commodity names, country codes, years, etc.), and use the right tools to get comprehensive answers. "
            "You can use multiple tools if needed to provide complete responses."
        ),
        backstory=(
            "You are an expert climate risk analyst at Helios AI, specializing in commodity crop risk analysis. "
            "You have access to comprehensive climate risk data covering historical trends, current conditions, "
            "and future projections. You understand WAPR (climate risk metrics), seasonal patterns, "
            "and country-specific agricultural vulnerabilities. Your responses should be professional, "
            "data-driven, and include relevant context about the climate risk implications."
        ),
        tools=tools,
        llm=llm_model,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )


def kickoff_example(question: str) -> QAOutput:
    load_dotenv()
    agent = create_agent(os.getenv("API_BASE", "http://localhost:8000"))
    
    task = Task(
        description=f"""
        Answer the following climate risk question: {question}
        
        Instructions:
        1. Analyze the question to understand what specific information is needed
        2. Extract relevant parameters from the question (commodity, country, year, etc.)
        3. Select the most appropriate tool(s) to get the required data
        4. If the question mentions specific commodities, countries, or time periods, use those parameters
        5. Use multiple tools if needed to provide a comprehensive answer
        6. Provide clear, actionable insights with specific numbers and context
        7. Explain the climate risk implications for decision-making
        
        Available commodities: Cocoa beans, Coffee beans, Maize, Oil palm fruit, Rice, Soya beans, Sugar cane, Wheat
        
        Examples of parameter extraction:
        - "What country has highest risk for Cocoa beans?" → commodity="Cocoa beans"
        - "How does Brazil compare in 2024?" → country_code="BR", year=2024
        - "Top 3 lowest risk countries for Rice" → commodity="Rice", k=3
        """,
        agent=agent,
        expected_output=(
            "A comprehensive answer that includes specific data points, time periods, "
            "and clear explanation of climate risk implications for decision-making."
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


