#!/usr/bin/env python3
"""
Test all API endpoints to discover correct answers for comprehensive testing.
"""

import requests
import json
from typing import Dict, Any

def test_endpoint(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single API endpoint and return the result."""
    base_url = "http://localhost:8000/api/v1/query"
    try:
        response = requests.post(f"{base_url}/{endpoint}", json=payload, timeout=10)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "details": response.text}
    except Exception as e:
        return {"success": False, "error": "Exception", "details": str(e)}

def main():
    """Test all endpoints based on the 10 questions from instructions.txt"""
    
    print("🧪 Testing API Endpoints for Comprehensive Test Data")
    print("=" * 60)
    
    # Map questions to endpoint tests
    test_cases = {
        "1. Highest current climate risk": {
            "endpoint": "highest-current-risk",
            "payload": {"commodity": "Cocoa beans"}
        },
        "2. Brazil 2025 vs 10-year average": {
            "endpoint": "compare-country-year-vs-hist", 
            "payload": {"commodity": "Cocoa beans", "country_code": "BR", "year": 2025}
        },
        "3. Most similar year": {
            "endpoint": "most-similar-year",
            "payload": {"commodity": "Cocoa beans", "scope": "global"}
        },
        "4. Global avg for September 2025": {
            "endpoint": "global-avg-for-month",
            "payload": {"commodity": "Cocoa beans", "year": 2025, "month": 9}
        },
        "5. EU risk comparison": {
            "endpoint": "eu-risk-comparison",
            "payload": {"commodity": "Wheat", "current_year": 2026, "previous_year": 2025}
        },
        "6. Top 3 lowest historical risk": {
            "endpoint": "top-k-lowest-hist-risk",
            "payload": {"commodity": "Cocoa beans", "k": 3}
        },
        "7. Trend 2016-2025": {
            "endpoint": "trend-max-risk",
            "payload": {"commodity": "Cocoa beans", "start_year": 2016, "end_year": 2025}
        },
        "8. India season change": {
            "endpoint": "country-season-change",
            "payload": {"commodity": "Cocoa beans", "country_code": "IN"}
        },
        "9. Yield rating and risk": {
            "endpoint": "yield-and-risk-relation",
            "payload": {"commodity": "Oil palm fruit", "scope": "global"}
        },
        "10. Upcoming spike regions": {
            "endpoint": "upcoming-spike-regions",
            "payload": {"commodity": "Rice", "threshold": -4.0}
        }
    }
    
    results = {}
    
    for question, test_case in test_cases.items():
        print(f"\n{question}")
        print(f"Endpoint: {test_case['endpoint']}")
        print(f"Payload: {test_case['payload']}")
        
        result = test_endpoint(test_case["endpoint"], test_case["payload"])
        results[question] = result
        
        if result["success"]:
            answer = result["data"]["answer"]
            print(f"✅ SUCCESS")
            if isinstance(answer, dict):
                # Extract key information
                if "country_name" in answer:
                    print(f"   Country: {answer['country_name']} ({answer.get('country_code', 'N/A')})")
                if "this_year_avg_wapr" in answer:
                    print(f"   Risk Score: {answer['this_year_avg_wapr']}")
                if "commodity" in answer:
                    print(f"   Commodity: {answer['commodity']}")
            elif isinstance(answer, list):
                print(f"   List with {len(answer)} items")
                if answer:
                    print(f"   First item: {answer[0]}")
            else:
                print(f"   Result: {answer}")
        else:
            print(f"❌ FAILED: {result['error']}")
            if "details" in result:
                print(f"   Details: {result['details']}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    print(f"Successful tests: {successful}/{total}")
    
    if successful < total:
        print("\n⚠️ Failed tests:")
        for question, result in results.items():
            if not result["success"]:
                print(f"  - {question}: {result['error']}")

if __name__ == "__main__":
    main()
