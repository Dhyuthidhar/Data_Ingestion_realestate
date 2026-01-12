# JSON Enforcement Test Results - Agents 1-2

**Date:** 2026-01-12  
**Test Property:** 1148 Greenbrook Drive, Danville, CA  
**Tests Run:** 2 iterations

---

## ✅ SUCCESSES

### 1. JSON Format Enforcement: 100% Success
- **Agent 1:** ✅ Returns valid JSON (parse method: `json_extraction`)
- **Agent 2:** ✅ Returns valid JSON (parse method: `json_extraction`)
- **No parsing errors:** Both agents successfully parsed by `_extract_json_from_response()`
- **No fallback needed:** Not using `text_extraction_fallback` for Agents 1-2

### 2. Infrastructure Working Correctly
- ✅ `_extract_json_from_response()` helper function working
- ✅ `_parse_dual_format_response()` updated to use JSON extractor
- ✅ Field validation working (missing fields filled with null)
- ✅ Perplexity API accepting JSON system prompt

### 3. Structure Validation
- ✅ All expected fields present in response
- ✅ Proper JSON syntax (no markdown wrappers)
- ✅ No explanatory text before/after JSON

---

## ⚠️ CRITICAL ISSUE IDENTIFIED

### Problem: All Fields Returning Null

**Agent 1 Response:**
```json
{
  "parcel_number": null,
  "property_tax_annual": null,
  "hoa_monthly": null,
  "hoa_association_name": null,
  "owner_name": null,
  "last_sale_date": null,
  "mortgage_amount": null,
  "mortgage_lender": null,
  "confidence": "HIGH"
}
```

**Agent 2 Response:**
```json
{
  "bedrooms": null,
  "bathrooms": null,
  "square_feet": null,
  "year_built": null,
  "lot_size_sqft": null,
  "property_type": null,
  "current_status": null,
  "last_sold_price": null,
  "last_sold_date": null,
  "price_per_sqft": null,
  "confidence": "HIGH"
}
```

### Root Cause Analysis

**Hypothesis 1: Perplexity Not Searching Web**
- Despite `"SEARCH THE WEB and {prompt}"` in user message
- Despite `search_recency_filter: "month"` in API call
- Agents may be returning empty JSON to comply with format requirements
- Citations are present but may be generic/unrelated to property

**Evidence:**
- Agent 1 citations: AWS IoT docs, Bitbucket API, GeeksForGeeks JSON tutorials
- Agent 2 citations: JSON schema docs, technical tutorials
- **None of these are property-related sites** (no Zillow, Redfin, Realtor.com)

**Hypothesis 2: JSON Enforcement Too Strong**
- System prompt emphasizes format so heavily that agents prioritize format over content
- Agents may interpret "return ONLY JSON" as "return empty JSON rather than risk format violation"
- Balance between format enforcement and data collection not optimal

**Hypothesis 3: Property Data Not Accessible**
- This specific property may not have public data available
- Need to test with different property that has confirmed data

---

## 📊 Test Metrics

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| **JSON Parsing Success** | 2/2 (100%) | 100% | ✅ PASS |
| **Parse Method** | json_extraction | json_extraction | ✅ PASS |
| **Fields Populated (Agent 1)** | 0/8 (0%) | 60-75% | ❌ FAIL |
| **Fields Populated (Agent 2)** | 0/10 (0%) | 85-95% | ❌ FAIL |
| **Citations (Agent 1)** | 10 | 3+ | ✅ PASS |
| **Citations (Agent 2)** | 10 | 3+ | ✅ PASS |
| **Citation Quality** | Poor (generic) | Property-specific | ❌ FAIL |

---

## 🔍 RECOMMENDATIONS

### Option 1: Adjust System Prompt Balance (RECOMMENDED)
**Status:** ✅ ATTEMPTED (Test Run 2)

Updated system prompt to emphasize:
1. **STEP 1:** Search web and find actual data FIRST
2. **STEP 2:** Return data in JSON format AFTER searching

**Result:** Still returning all nulls - suggests deeper issue with web search

### Option 2: Test with Different Property
**Rationale:** Verify if issue is property-specific or systemic

**Action:** Test with property known to have public data:
- 350 Fifth Avenue, New York, NY (Empire State Building - definitely has data)
- Or another well-documented property

### Option 3: Verify Perplexity Web Search
**Action:** Add explicit search verification to prompts

Update Agent 1 prompt to include:
```
BEFORE returning JSON, you MUST:
1. Search "1148 Greenbrook Drive Danville CA" on Zillow.com
2. Search "1148 Greenbrook Drive Danville CA" on Redfin.com
3. Extract the actual data you find
4. ONLY THEN format as JSON

If you return all nulls, it means you didn't search properly.
```

### Option 4: Hybrid Approach - Allow Narrative with JSON
**Rationale:** Current approach may be too restrictive

Allow agents to:
1. Provide search narrative/explanation
2. Include JSON at the end
3. Use `_extract_json_from_response()` to extract JSON from narrative

This gives agents freedom to explain what they found while still providing structured data.

### Option 5: Reduce JSON Enforcement Strictness
**Action:** Make system prompt less intimidating

Instead of:
> "IF YOU VIOLATE THESE RULES, THE ENTIRE SYSTEM WILL FAIL"

Use:
> "Return JSON format. If you need to explain your search process, do so, then provide the JSON."

---

## 🎯 NEXT STEPS

### Immediate Actions

1. **Test Option 3:** Add explicit search verification to Agent 1-2 prompts
2. **Monitor citations:** Check if property-specific URLs appear
3. **Test different property:** Verify if issue is property-specific

### If Still Failing

4. **Try Option 4:** Allow hybrid narrative + JSON approach
5. **Review Perplexity API docs:** Verify web search is actually enabled
6. **Consider fallback:** If Perplexity won't search, may need different approach

---

## 💡 KEY INSIGHTS

### What's Working
1. ✅ JSON extraction infrastructure is solid
2. ✅ Format enforcement working perfectly
3. ✅ Field validation working correctly
4. ✅ No parsing errors

### What's Not Working
1. ❌ Agents not actually searching web for property data
2. ❌ Citations are generic, not property-specific
3. ❌ All fields returning null despite data being available

### The Core Problem
**Format enforcement is working TOO well** - agents are complying with JSON format requirements but not actually performing web searches to populate the data. Need to find balance between:
- Strict JSON format (for parsing)
- Actual web search and data extraction (for content)

---

## 🔄 DECISION POINT

**User: Which approach should we try next?**

**Option A:** Continue with current JSON-only approach, add explicit search verification (Option 3)  
**Option B:** Switch to hybrid narrative + JSON approach (Option 4)  
**Option C:** Test with different property first to isolate issue (Option 2)  
**Option D:** Reduce JSON enforcement strictness (Option 5)

**My Recommendation:** Try **Option C first** (test different property), then **Option 3** (explicit search verification) if issue persists.

---

## 📈 PROGRESS SUMMARY

**Completed:**
- ✅ TASK 1-3: JSON helper + Agents 1-2 prompts rewritten
- ✅ TASK 4: Updated execution method
- ✅ TASK 5: Updated Perplexity API with JSON system prompt
- ✅ TASK 6: Tested Agents 1-2

**Status:** JSON infrastructure working, but agents not populating data. Need to adjust approach to balance format with content.

**Next:** Decide on approach to fix null data issue before continuing with Agents 3-5.
