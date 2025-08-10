# Expected Correct Answers for Climate Risk Questions

Based on API testing and database queries, these are the expected correct answers for the 10 questions from `instructions.txt`.

## Test Results Summary

All 10 API endpoints are functional and return the following expected data:

### 1. What country has the highest current climate risk for Cocoa beans?
- **Expected Answer**: India
- **API Endpoint**: `/api/v1/query/highest-current-risk`
- **Key Data**: India (IN) with 45.7 WAPR for Cocoa beans
- **Tool**: `get_highest_current_risk`

### 2. How does Brazil's 2025 climate risk compare to its 10-year average for Cocoa beans?
- **Expected Answer**: Brazil with specific comparison data
- **API Endpoint**: `/api/v1/query/compare-country-year-vs-hist`
- **Key Data**: Brazil (BR) with 16.6 WAPR for Cocoa beans in 2025
- **Tool**: `compare_country_year_vs_hist`

### 3. What year was most similar to this season for Cocoa beans?
- **Expected Answer**: Specific year with similarity data
- **API Endpoint**: `/api/v1/query/most-similar-year`
- **Key Data**: Global (GLB) scope for Cocoa beans
- **Tool**: `get_most_similar_year`

### 4. What's the global average climate risk for Cocoa beans in September 2025?
- **Expected Answer**: Global average WAPR for September 2025
- **API Endpoint**: `/api/v1/query/global-avg-for-month`
- **Key Data**: Cocoa beans, year 2025, month 9
- **Tool**: `get_global_avg_for_month`

### 5. How does the EU's risk for Wheat in 2026 compare with 2025?
- **Expected Answer**: EU risk comparison between years
- **API Endpoint**: `/api/v1/query/eu-risk-comparison`
- **Key Data**: Wheat commodity, comparing 2026 vs 2025
- **Tool**: `get_eu_risk_comparison`

### 6. What are the top 3 countries with the lowest historical risk for Cocoa beans?
- **Expected Answer**: List including Peru as first
- **API Endpoint**: `/api/v1/query/top-k-lowest-hist-risk`
- **Key Data**: Peru (PE) with 13.4 hist_avg_wapr as lowest
- **Tool**: `get_top_k_lowest_hist_risk`

### 7. What's the trend in maximum climate risk for Cocoa beans from 2016 to 2025?
- **Expected Answer**: Trend data showing risk evolution
- **API Endpoint**: `/api/v1/query/trend-max-risk`
- **Key Data**: 100 data points from 2016-2025, starting with 100.0 WAPR in 2016
- **Tool**: `get_trend_max_risk`

### 8. Did India's risk increase or decrease from the previous growing season for Cocoa beans?
- **Expected Answer**: India seasonal change analysis
- **API Endpoint**: `/api/v1/query/country-season-change`
- **Key Data**: India (IN) for Cocoa beans seasonal comparison
- **Tool**: `get_country_season_change`

### 9. What is the current yield rating for Oil palm fruit and how does it relate to risk?
- **Expected Answer**: Yield rating and risk relationship
- **API Endpoint**: `/api/v1/query/yield-and-risk-relation`
- **Key Data**: Oil palm fruit, global scope
- **Tool**: `get_yield_and_risk_relation`

### 10. Which regions are showing a spike in upcoming seasonal risk for Rice?
- **Expected Answer**: Regions with risk spikes, including Bangladesh
- **API Endpoint**: `/api/v1/query/upcoming-spike-regions`
- **Key Data**: Bangladesh (BD) with 4.9 avg_risk_score_diff and 41.2 upcoming_year_risk_score
- **Tool**: `get_upcoming_spike_regions`

## Testing Instructions

To verify the LLM is working correctly:

1. **Run the comprehensive test**:
   ```bash
   python test_fix.py
   ```

2. **Check for these success criteria**:
   - ✅ **Tool Usage**: Each question should use the correct tool
   - ✅ **Content Accuracy**: Answers should contain expected keywords and data
   - ✅ **No Hallucination**: All data should come from actual API calls, not LLM knowledge

3. **Expected Success Rate**: 100% (10/10 tests passing)

## Debugging Failed Tests

If tests fail, check the logs for:
- `🔧 TOOL CALLED:` messages showing tool invocation
- Parameter passing (especially `commodity` parameter)
- API response data vs LLM output
- Query metadata in the UI showing correct tool and endpoint

## API Data Verification

The test suite is based on actual API responses verified on [timestamp]. If database content changes, update the expected keywords in `test_fix.py` accordingly.
