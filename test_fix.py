#!/usr/bin/env python3
"""
Comprehensive test script to verify all 10 questions from instructions.txt
are answered correctly using the right tools and returning accurate data.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.crew.run_agent import kickoff_example

class TestCase:
    def __init__(self, question: str, expected_keywords: List[str], expected_tool: str, description: str):
        self.question = question
        self.expected_keywords = expected_keywords  # Keywords that should appear in the answer
        self.expected_tool = expected_tool
        self.description = description

def run_test_case(test_case: TestCase) -> Dict[str, Any]:
    """Run a single test case and return results."""
    print(f"\n🧪 Testing: {test_case.description}")
    print(f"Question: {test_case.question}")
    print(f"Expected tool: {test_case.expected_tool}")
    print(f"Expected keywords: {', '.join(test_case.expected_keywords)}")
    print("=" * 80)
    
    try:
        result = kickoff_example(test_case.question)
        
        # Check if correct tool was used
        tool_correct = False
        if hasattr(result, 'query') and result.query.get('tool') == test_case.expected_tool:
            tool_correct = True
            print("✅ TOOL: Correct tool used")
        else:
            print(f"❌ TOOL: Expected '{test_case.expected_tool}', got '{result.query.get('tool') if hasattr(result, 'query') else 'None'}'")
        
        # Check if expected keywords appear in answer
        keywords_found = []
        answer_text = str(result.answer).lower()
        source_text = str(result.source).lower() if hasattr(result, 'source') else ""
        
        for keyword in test_case.expected_keywords:
            if keyword.lower() in answer_text or keyword.lower() in source_text:
                keywords_found.append(keyword)
        
        keywords_correct = len(keywords_found) > 0
        if keywords_correct:
            print(f"✅ CONTENT: Found keywords: {', '.join(keywords_found)}")
        else:
            print(f"❌ CONTENT: None of expected keywords found: {', '.join(test_case.expected_keywords)}")
        
        # Print results
        print(f"\nAnswer: {result.answer}")
        print(f"Source: {result.source}")
        print(f"Query: {result.query}")
        
        return {
            "success": tool_correct and keywords_correct,
            "tool_correct": tool_correct,
            "keywords_correct": keywords_correct,
            "keywords_found": keywords_found,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return {
            "success": False,
            "tool_correct": False,
            "keywords_correct": False,
            "keywords_found": [],
            "error": str(e)
        }

def main():
    """Run all test cases based on the 10 questions from instructions.txt"""
    
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("Testing all 10 questions from instructions.txt with expected correct answers")
    print("=" * 80)
    
    # Define test cases based on API results and instructions.txt
    test_cases = [
        TestCase(
            question="What country has the highest current climate risk for Cocoa beans?",
            expected_keywords=["India", "45.7"],
            expected_tool="get_highest_current_risk",
            description="1. Highest current climate risk"
        ),
        TestCase(
            question="How does Brazil's 2025 climate risk compare to its 10-year average for Cocoa beans?",
            expected_keywords=["Brazil", "16.6", "BR"],
            expected_tool="compare_country_year_vs_hist",
            description="2. Brazil 2025 vs historical average"
        ),
        TestCase(
            question="What year was most similar to this season for Cocoa beans?",
            expected_keywords=["Cocoa beans", "similar", "year"],
            expected_tool="get_most_similar_year",
            description="3. Most similar year"
        ),
        TestCase(
            question="What's the global average climate risk for Cocoa beans in September 2025?",
            expected_keywords=["Cocoa beans", "2025", "September", "global"],
            expected_tool="get_global_avg_for_month",
            description="4. Global average for September 2025"
        ),
        TestCase(
            question="How does the EU's risk for Wheat in 2026 compare with 2025?",
            expected_keywords=["Wheat", "2026", "2025", "EU"],
            expected_tool="get_eu_risk_comparison",
            description="5. EU risk comparison"
        ),
        TestCase(
            question="What are the top 3 countries with the lowest historical risk for Cocoa beans?",
            expected_keywords=["Peru", "3", "lowest", "Cocoa beans"],
            expected_tool="get_top_k_lowest_hist_risk",
            description="6. Top 3 lowest historical risk"
        ),
        TestCase(
            question="What's the trend in maximum climate risk for Cocoa beans from 2016 to 2025?",
            expected_keywords=["Cocoa beans", "2016", "2025", "trend"],
            expected_tool="get_trend_max_risk",
            description="7. Trend 2016-2025"
        ),
        TestCase(
            question="Did India's risk increase or decrease from the previous growing season for Cocoa beans?",
            expected_keywords=["India", "Cocoa beans", "season"],
            expected_tool="get_country_season_change",
            description="8. India season change"
        ),
        TestCase(
            question="What is the current yield rating for Oil palm fruit and how does it relate to risk?",
            expected_keywords=["Oil palm fruit", "yield", "rating"],
            expected_tool="get_yield_and_risk_relation",
            description="9. Yield rating and risk relation"
        ),
        TestCase(
            question="Which regions are showing a spike in upcoming seasonal risk for Rice?",
            expected_keywords=["Rice", "Bangladesh", "spike", "regions"],
            expected_tool="get_upcoming_spike_regions",
            description="10. Upcoming spike regions"
        ),
    ]
    
    results = []
    
    for test_case in test_cases:
        result = run_test_case(test_case)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results if r["success"])
    tool_correct_tests = sum(1 for r in results if r["tool_correct"])
    content_correct_tests = sum(1 for r in results if r["keywords_correct"])
    
    print(f"Overall Success: {successful_tests}/{len(results)} tests passed")
    print(f"Tool Usage: {tool_correct_tests}/{len(results)} correct tools used")
    print(f"Content Accuracy: {content_correct_tests}/{len(results)} correct content")
    
    if successful_tests < len(results):
        print(f"\n⚠️ FAILED TESTS:")
        for i, (test_case, result) in enumerate(zip(test_cases, results)):
            if not result["success"]:
                print(f"  {i+1}. {test_case.description}")
                if not result["tool_correct"]:
                    print(f"     - Wrong tool used")
                if not result["keywords_correct"]:
                    print(f"     - Expected keywords not found")
                if "error" in result:
                    print(f"     - Error: {result['error']}")
    
    print(f"\n🎯 Success Rate: {(successful_tests/len(results)*100):.1f}%")
    
    if successful_tests == len(results):
        print("🎉 ALL TESTS PASSED! The LLM is correctly using tools and providing accurate answers.")
    else:
        print("⚠️ Some tests failed. The LLM may be hallucinating or using wrong tools.")

if __name__ == "__main__":
    main()
