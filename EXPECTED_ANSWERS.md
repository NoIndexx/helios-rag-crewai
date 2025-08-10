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
- **Expected Answer**: 2018 was most similar to the 2025 growing season
- **API Endpoint**: `/api/v1/query/most-similar-year`
- **Key Data**: Global (GLB) scope for Cocoa beans, similar year: 2018, risk category: Low, rating: 3 stars
- **Tool**: `get_most_similar_year`

### 4. What's the global average climate risk for Cocoa beans in September 2025?
- **Expected Answer**: Global average WAPR: 29.6, Global maximum WAPR: 56.7
- **API Endpoint**: `/api/v1/query/global-avg-for-month`
- **Key Data**: Cocoa beans, year 2025, month 9, global_avg_wapr: 29.6, global_max_wapr: 56.7
- **Tool**: `get_global_avg_for_month`

### 5. How does the EU's risk for Wheat in 2026 compare with 2025?
- **Expected Answer**: EU risk unchanged - both years at 23.5 WAPR
- **API Endpoint**: `/api/v1/query/eu-risk-comparison`
- **Key Data**: Wheat commodity, 2026: 23.5 WAPR, 2025: 23.5 WAPR, delta: 0.0, trend: unchanged
- **Tool**: `get_eu_risk_comparison`

### 6. What are the top 3 countries with the lowest historical risk for Cocoa beans?
- **Expected Answer**: 1. Peru (PE): 13.4, 2. Brazil (BR): 14.2, 3. Ecuador (EC): 14.8
- **API Endpoint**: `/api/v1/query/top-k-lowest-hist-risk`
- **Key Data**: Peru (PE) with 13.4 hist_avg_wapr as lowest, followed by Brazil (14.2) and Ecuador (14.8)
- **Tool**: `get_top_k_lowest_hist_risk`

### 7. What's the trend in maximum climate risk for Cocoa beans from 2016 to 2025?
- **Expected Answer**: Declining trend from 100.0 WAPR in 2016 to 56.1 WAPR in 2025
- **API Endpoint**: `/api/v1/query/trend-max-risk`
- **Key Data**: 100 data points from 2016-2025, starting with 100.0 WAPR in 2016, ending with 56.1 WAPR in 2025
- **Tool**: `get_trend_max_risk`

### 8. Did India's risk increase or decrease from the previous growing season for Cocoa beans?
- **Expected Answer**: India's risk remained unchanged at 45.7 WAPR
- **API Endpoint**: `/api/v1/query/country-season-change`
- **Key Data**: India (IN) current: 45.7 WAPR, previous: 45.7 WAPR, delta: 0.0, direction: no_change
- **Tool**: `get_country_season_change`

### 9. What is the current yield rating for Oil palm fruit and how does it relate to risk?
- **Expected Answer**: Yield rating "Good" with 2.88 mt/ha, historical avg risk 16.5 WAPR
- **API Endpoint**: `/api/v1/query/yield-and-risk-relation`
- **Key Data**: Oil palm fruit, global scope, yield_rating: "Good", total_yield: 2.88 mt/ha, hist_avg_wapr: 16.5
- **Tool**: `get_yield_and_risk_relation`

### 10. Which regions are showing a spike in upcoming seasonal risk for Rice?
- **Expected Answer**: Bangladesh (BD) and Brazil (BR) showing spikes
- **API Endpoint**: `/api/v1/query/upcoming-spike-regions`
- **Key Data**: Bangladesh (BD) with 4.9 avg_risk_score_diff and 41.2 upcoming_year_risk_score, Brazil (BR) with 3.5 diff and 28.5 upcoming
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

The test suite is based on actual API responses verified through direct database queries. **Data verified: December 2024**

### Database Statistics:
- **Commodities**: 8 total (`Cocoa beans`, `Coffee, green`, `Corn: Commodity Tracked`, `Oil palm fruit`, `Rice`, `Soya beans`, `Sugar cane`, `Wheat`)
- **Records**: 
  - climate_risk_by_country: 1,170 records
  - risk_compared_hist_box: 390 records  
  - risk_global_avg_max: 1,000 records
  - most_similar_year: 39 records

### Key Verified Values:
- **Highest Risk**: India (IN) with 45.7 WAPR for Cocoa beans ✅
- **Brazil 2025**: 16.6 WAPR vs 14.2 historical (16.9% increase) ✅  
- **Similar Year**: 2018 most similar to 2025 growing season ✅
- **Lowest Risk Countries**: Peru (13.4), Brazil (14.2), Ecuador (14.8) ✅
- **EU Wheat**: Unchanged at 23.5 WAPR between 2025-2026 ✅

If database content changes, update the expected keywords in `test_fix.py` accordingly.

## Optional Test Questions

### Additional Question 1: What are the top 5 countries with highest climate risk for Rice?
- **Expected Answer**: 1. Pakistan (PK): 48.8 WAPR, 2. United States (US): 45.4 WAPR, 3. Myanmar (MM): 43.2 WAPR
- **API Endpoint**: Custom endpoint for top-k highest risk
- **Key Data**: Pakistan leads with 48.8 WAPR (2025-2026), followed by US (45.4) and Myanmar (43.2)
- **Tool**: `get_top_k_highest_risk` (NEW tool created for highest risk queries)

### Additional Question 2: How does Indonesia's climate risk for Oil palm fruit compare between 2024 and 2025?
- **Expected Answer**: Only 2025 data available - Indonesia 11.5 WAPR vs 18.0 historical (-36.11%)
- **API Endpoint**: `/api/v1/query/compare-country-year-vs-hist`
- **Key Data**: Indonesia (ID) 2025: 11.5 WAPR, historical: 18.0 WAPR, 2024 data not available
- **Tool**: `compare_country_year_vs_hist`

### Additional Question 3: What is the global production volume for Soya beans and its risk category?
- **Expected Answer**: Global yield: 2.74 mt/ha with Neutral yield rating, historical avg WAPR: 27.4
- **API Endpoint**: `/api/v1/query/yield-and-risk-relation`
- **Key Data**: Soya beans global yield: 2.74 mt/ha, yield rating: Neutral, historical avg WAPR: 27.4, max WAPR: 51.2
- **Tool**: `get_yield_and_risk_relation`
