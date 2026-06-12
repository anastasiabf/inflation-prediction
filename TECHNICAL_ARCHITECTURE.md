# Technical Architecture & Engineering Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFLATION PREDICTION SYSTEM V3                      │
│                    End-to-End ML + LLM + Dashboard Pipeline                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DATA INGESTION & PREPROCESSING                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Input Sources:                      Processing:                            │
│  ├─ BI Inflation (Web Scraping)   → DataFrame Alignment                     │
│  ├─ Yahoo Finance USD/IDR APIs    → Daily → Monthly Aggregation            │
│  ├─ BI Policy Rate (Open Data)    → Forward/Backward Fill                  │
│  ├─ IHK Index (BPS Portal)        → Standardized Format                    │
│  ├─ News Headlines (RSS/HTML)     → Batch Aggregation by Month             │
│  └─ Social Media Posts (Scrape)   → Text Concatenation                     │
│                                                                              │
│  Output: Unified DataFrame (36 rows × 8 columns)                           │
│  ├─ date: DatetimeIndex                                                     │
│  ├─ inflation_rate: float64                                                │
│  ├─ bi_rate: float64                                                       │
│  ├─ exchange_rate_usd_idr: float64                                         │
│  ├─ ihk_index: float64                                                     │
│  ├─ news_text: str (1000-5000 chars)                                       │
│  ├─ social_media_text: str (2000-8000 chars)                               │
│  └─ [other optional features]                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: LLM-DRIVEN NLP SENTIMENT ANALYSIS                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  For each month:                                                            │
│  1. Batch news_text + social_media_text                                    │
│  2. Route to LLM API (OpenAI/Anthropic) or local model (HF/transformers)   │
│  3. System Prompt: "Analyze Indonesian inflation sentiment"                │
│  4. Parse JSON response: {"polarity_score": float, ...}                    │
│  5. Append scores to DataFrame                                             │
│                                                                              │
│  LLM Backends:                                                              │
│  ├─ OpenAI GPT-4o: Heavy-weight, high accuracy, requires API key           │
│  ├─ Anthropic Claude: Medium-weight, good reasoning, requires API key      │
│  ├─ HuggingFace Local: Light-weight, free, runs locally                    │
│  └─ Mock: Keyword heuristics for testing/demo                              │
│                                                                              │
│  Output: Enriched DataFrame with 2 new columns:                            │
│  ├─ news_sentiment_llm_score: float[-1.0, +1.0]                           │
│  └─ social_media_sentiment_llm_score: float[-1.0, +1.0]                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: MACHINE LEARNING - RANDOM FOREST MODEL                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Feature Engineering:                                                       │
│  X = [inflation_rate_t, bi_rate_t, exchange_rate_t, ihk_t,               │
│        news_sentiment_t, social_sentiment_t]                               │
│  y = inflation_rate_t+1  (shift forward by 1 month)                        │
│                                                                              │
│  Training Strategy (TimeSeriesSplit):                                       │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │ Fold 1: Train [1-20 months]   │ Test [21-23 months]         │           │
│  │ Fold 2: Train [1-23 months]   │ Test [24-26 months]         │           │
│  │ Fold 3: Train [1-26 months]   │ Test [27-29 months]         │           │
│  │ Final:  Train [1-35 months]   → Model deployed              │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  Model Parameters:                                                          │
│  ├─ n_estimators: 100 (trees)                                             │
│  ├─ max_depth: 15                                                          │
│  ├─ min_samples_split: 5                                                   │
│  ├─ min_samples_leaf: 2                                                    │
│  └─ random_state: 42 (reproducibility)                                     │
│                                                                              │
│  Evaluation Metrics:                                                        │
│  ├─ CV MAE:   0.244 ± 0.073%    (±0.25% uncertainty)                     │
│  ├─ CV RMSE:  0.345 ± 0.072%                                              │
│  ├─ CV R²:    0.713 ± 0.061    (71% variance explained in CV)            │
│  ├─ Final MAE: 0.124%                                                      │
│  ├─ Final RMSE: 0.249%                                                     │
│  └─ Final R²: 0.892 (89% variance explained on full data)                 │
│                                                                              │
│  Feature Importances Extracted:                                            │
│  ├─ inflation_rate: 78.4%         (historical momentum)                    │
│  ├─ social_sentiment: 16.4%       (public expectations)                    │
│  ├─ news_sentiment: 2.7%          (media narrative)                        │
│  ├─ ihk_index: 0.9%                                                        │
│  ├─ bi_rate: 0.8%                  (policy rate)                           │
│  └─ exchange_rate: 0.8%            (currency effects)                      │
│                                                                              │
│  Export to JavaScript:                                                      │
│  Linear approximation function for client-side prediction                 │
│  (see model_export.json for complete coefficients)                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: LLM ANALYTICAL INFERENCE - POLICY RECOMMENDATIONS                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Input Context Assembly:                                                    │
│  ├─ Predicted inflation from RF model (3.08%)                             │
│  ├─ Feature importances from model                                         │
│  ├─ Recent macro data (last 6 months avg)                                  │
│  └─ Sentiment analysis results                                             │
│                                                                              │
│  LLM Prompting (No Hardcoded Templates):                                   │
│  ┌────────────────────────────────────────────────────────────┐           │
│  │ SYSTEM PROMPT 1: Government Impact Analysis               │           │
│  │ "You are macroeconomic advisor for Indonesian government" │           │
│  │ "Analyze predicted inflation trajectory"                  │           │
│  │ "Assess: fiscal stability, purchasing power, BI corridor" │           │
│  │ Output: 400-600 word professional analysis               │           │
│  ├────────────────────────────────────────────────────────────┤           │
│  │ SYSTEM PROMPT 2: Policy Recommendations                  │           │
│  │ "Generate strategic recommendations across 3 timelines"   │           │
│  │ "Immediate (0-30d), Intermediate (30-90d), Long-term"   │           │
│  │ "Ensure feasibility within legal/institutional framework"│           │
│  │ Output: 9-15 actionable recommendations                 │           │
│  └────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  LLM Response Handling:                                                     │
│  ├─ Parse structured output (JSON where applicable)                       │
│  ├─ Extract key themes and recommendations                                 │
│  └─ Format for human consumption                                           │
│                                                                              │
│  Output: Government Report                                                 │
│  ├─ government_report.json (structured)                                    │
│  └─ government_report.txt (human-readable)                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 5: FRONTEND - STANDALONE HTML DASHBOARD WITH SIMULATION              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Single HTML File (24 KB) Contains:                                        │
│  ├─ Structure (semantic HTML5)                                             │
│  ├─ Styling (Tailwind CSS via CDN)                                         │
│  ├─ Charts (Chart.js via CDN)                                              │
│  ├─ Embedded Data:                                                         │
│  │  ├─ Historical inflation time series (12 months)                       │
│  │  ├─ Model coefficients (JavaScript formula)                            │
│  │  ├─ Feature importances                                                │
│  │  ├─ Government analysis text                                           │
│  │  └─ Feature ranges (for slider limits)                                │
│  └─ Client-side JavaScript Engine:                                         │
│     ├─ Slider event listeners                                              │
│     ├─ Real-time prediction calculation                                    │
│     └─ Dynamic badge color updates                                         │
│                                                                              │
│  JavaScript Prediction Engine:                                             │
│  ┌────────────────────────────────────────────────────────────┐           │
│  │ 1. User drags slider → triggers onInput event             │           │
│  │ 2. Collect all slider values into features object         │           │
│  │ 3. Execute linear approximation formula:                  │           │
│  │    prediction = intercept +                               │           │
│  │    Σ(coefficient_i × feature_i)                          │           │
│  │ 4. Clip result to [0, 10%] range                         │           │
│  │ 5. Update badge text & color based on value              │           │
│  │ 6. NO SERVER CALLS - 100% client-side                    │           │
│  └────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  Interactive Simulation Panel:                                             │
│  ├─ Slider 1: BI Rate (0-10%, default 6.0%)                             │
│  ├─ Slider 2: USD/IDR (14k-18k, default 15.5k)                          │
│  ├─ Slider 3: News Sentiment (-1 to +1, default 0)                       │
│  └─ Slider 4: Social Sentiment (-1 to +1, default 0)                     │
│                                                                              │
│  Color Coding System:                                                      │
│  ├─ Inflation < 2.5%:  🟢 Green (#ecfdf5 bg, #065f46 text)               │
│  ├─ Inflation 2.5-4%:  🟡 Yellow (#fefce8 bg, #78350f text)              │
│  └─ Inflation > 4%:    🔴 Red (#fef2f2 bg, #7f1d1d text)                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ DATA FLOW SUMMARY                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Web Scraping → Data Alignment → LLM Sentiment → Random Forest Model       │
│       ↓              ↓                 ↓                ↓                   │
│  unified_dataset   enriched_df     sentiment scores   prediction (3.08%)   │
│       ↓              ↓                 ↓                ↓                   │
│                     ├──────────────────→ LLM Analysis ──→ Policy Report    │
│                                                           ↓                │
│                     ←────────────────← HTML Factory ←────┘                │
│                                         ↓                                  │
│                                    index.html (Dashboard)                  │
│                                         ↓                                  │
│                                   [Browser] ←→ [JavaScript Simulator]      │
│                                   (no server calls)                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Class Architecture

### Layer 1: Data Ingestion
```python
data_ingestion.py
├── BIInflationScraper
│   └── scrape_inflation_table() → DataFrame
├── ExchangeRateCollector (static methods)
│   └── fetch_monthly_usd_idr() → DataFrame
├── MacroeconomicDataCollector (static methods)
│   ├── fetch_bi_rate() → DataFrame
│   ├── fetch_ihk_index() → DataFrame
│   ├── generate_news_text_batches() → DataFrame
│   └── generate_social_media_text_batches() → DataFrame
└── DataPipeline
    └── build_unified_dataset() → (unified_df, news_df, social_df)
```

### Layer 2: LLM Sentiment
```python
llm_sentiment_pipeline.py
├── LLMSentimentAnalyzer
│   ├── analyze_batch() → (news_score, social_score, metadata)
│   ├── _analyze_openai() → Dict
│   ├── _analyze_anthropic() → Dict
│   ├── _analyze_huggingface() → Dict
│   └── _analyze_mock() → Dict
└── SentimentPipeline
    └── process_dataset() → enriched_df with sentiment columns
```

### Layer 3: ML Model
```python
model_training.py
├── RandomForestInflationModel
│   ├── train_with_time_series_split() → metrics Dict
│   ├── export_linear_approximation() → formula Dict
│   ├── export_for_javascript() → js_export Dict
│   └── predict() → ndarray
└── ModelTrainingPipeline
    └── train_and_export() → (model, export_dict)
```

### Layer 4: LLM Analysis
```python
llm_government_insights.py
├── GovernmentInsightGenerator
│   ├── generate_insights() → Dict (impact + recommendations)
│   ├── _generate_openai_insights() → Dict
│   ├── _generate_anthropic_insights() → Dict
│   ├── _generate_huggingface_insights() → Dict
│   └── _generate_mock_insights() → Dict
└── InsightsPipeline
    └── generate_report() → full report Dict
```

### Layer 5: Frontend
```python
html_factory.py
├── HTMLFactory
│   ├── generate_html() → HTML string
│   ├── _render_importance_list() → HTML
│   ├── _render_js_coefficients() → JS string
│   └── _format_text_for_html() → HTML
└── HTMLFactoryPipeline
    └── generate_dashboard() → index.html file
```

### Master Orchestrator
```python
main_orchestrator.py
├── InflationPredictionOrchestrator
│   ├── execute() → execution result Dict
│   ├── _execute_phase_1() → (unified_df, news_df, social_df)
│   ├── _execute_phase_2() → enriched_df
│   ├── _execute_phase_3() → (model, export_dict)
│   ├── _execute_phase_4() → report Dict
│   ├── _execute_phase_5() → index.html path
│   └── _save_execution_log() → None
└── main() → exit_code
```

---

## Data Structures

### Unified DataFrame Schema
```
index: DatetimeIndex (monthly, 36 rows)
Columns:
├─ inflation_rate: float64 [2.7-5.2]
├─ bi_rate: float64 [4.6-7.3]
├─ exchange_rate_usd_idr: float64 [15k-16.5k]
├─ ihk_index: float64 [105-115]
├─ news_text: object (string, 1-5k chars)
├─ social_media_text: object (string, 2-8k chars)
├─ news_sentiment_llm_score: float64 [-1.0 to +1.0]
├─ social_media_sentiment_llm_score: float64 [-1.0 to +1.0]
└─ [metadata columns for tracing]
```

### Model Export JSON Schema
```json
{
  "model_type": "string",
  "n_estimators": int,
  "feature_names": ["string", ...],
  "feature_count": int,
  "feature_importances": {
    "feature_name": float,
    ...
  },
  "feature_importance_ranking": [
    {"feature": "string", "importance": float},
    ...
  ],
  "linear_approximation": {
    "intercept": float,
    "coefficients": {
      "feature_name": float,
      ...
    }
  },
  "training_metrics": {
    "mae": float,
    "rmse": float,
    "r2": float,
    "n_samples": int,
    "n_features": int
  },
  "prediction_formula": "string (JavaScript)",
  "feature_ranges": {
    "feature_name": {
      "min": float,
      "max": float,
      "mean": float,
      "std": float
    },
    ...
  }
}
```

### Government Report JSON Schema
```json
{
  "prediction": float,
  "generated_at": "string (ISO timestamp)",
  "government_impact_analysis": "string (markdown)",
  "policy_recommendations": "string (markdown)",
  "backend": "string (openai|anthropic|huggingface|mock)",
  "supporting_data": {
    "feature_importances": {...},
    "recent_average_sentiment": {
      "news_sentiment": float,
      "social_sentiment": float
    }
  }
}
```

---

## Error Handling Strategy

### Graceful Degradation
```
Phase 1: Web scraping fails
  └─> Use synthetic data (no system failure)

Phase 2: LLM API unavailable
  └─> Fall back to mock sentiment (continue pipeline)
  └─> Mark data quality in metadata

Phase 3: Model training issue
  └─> Alert but continue (use fallback model or abort)

Phase 4: LLM generation fails
  └─> Use template-based report (no system failure)

Phase 5: HTML generation error
  └─> Return error message (critical - user-facing)
```

### Logging
```
- All operations logged to INFO level
- Failures logged to ERROR/WARNING with context
- Execution trace saved to execution_log.json
- User gets detailed error messages for debugging
```

---

## Performance Characteristics

| Operation | Time | Memory | Notes |
|-----------|------|--------|-------|
| Data Ingestion | 2-5s | 50 MB | Network dependent |
| LLM Sentiment | 5-15s | 100 MB | API latency dominant |
| Model Training | 3-5s | 200 MB | TimeSeriesSplit overhead |
| LLM Insights | 10-20s | 100 MB | Multiple LLM calls |
| HTML Generation | 1-2s | 50 MB | I/O bound |
| **Total Pipeline** | **~30s** | **200 MB** | Single-threaded |

---

## Security Considerations

1. **API Keys**: Not hardcoded in source; use environment variables
2. **Data**: All processed locally; no PII sent to external services
3. **HTML Output**: No executable code injection risks (all data sanitized)
4. **JavaScript**: Client-side only, no external calls
5. **File Permissions**: Output files readable by user only

---

## Extension Points

### Add New Data Source
```python
# In data_ingestion.py
class NewDataCollector:
    @staticmethod
    def fetch_data(months: int) -> pd.DataFrame:
        # Implementation
        pass

# In DataPipeline.build_unified_dataset()
new_data = NewDataCollector.fetch_data(self.months)
unified_df = pd.concat([unified_df, new_data], axis=1)
```

### Add New LLM Backend
```python
# In llm_sentiment_pipeline.py
def _analyze_gemini(self, news_text, social_text, date_label):
    # Implementation using Google Gemini API
    pass
```

### Add New Visualization
```python
# In html_factory.py
# Add new chart container to HTML
# Add Chart.js chart initialization in JavaScript
```

---

## Testing Strategy

### Unit Test Template
```python
def test_data_ingestion():
    pipeline = DataPipeline(months=12)
    unified_df, _, _ = pipeline.build_unified_dataset()
    assert len(unified_df) == 12
    assert 'inflation_rate' in unified_df.columns

def test_sentiment_scoring():
    analyzer = LLMSentimentAnalyzer(backend="mock")
    score_news, score_social, _ = analyzer.analyze_batch(
        "Test news text", "Test social text"
    )
    assert -1.0 <= score_news <= 1.0
    assert -1.0 <= score_social <= 1.0
```

---

## Deployment Notes

### Local Deployment
- ✅ Fully self-contained
- ✅ No database required
- ✅ No server infrastructure needed
- ✅ Cross-platform compatible

### Production Deployment (Future)
- Consider moving to containerized environment (Docker)
- Add persistent storage layer (PostgreSQL)
- Implement scheduling (Apache Airflow/Celery)
- Add authentication/authorization layer
- Separate frontend from backend API

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.12+ |
| **Data Processing** | pandas | 2.0+ |
| **ML Framework** | scikit-learn | 1.3+ |
| **Finance Data** | yfinance | Latest |
| **Web Scraping** | BeautifulSoup4 | Latest |
| **Frontend** | Tailwind CSS | v3 (CDN) |
| **Charts** | Chart.js | v4 (CDN) |
| **LLM APIs** | OpenAI/Anthropic | Latest |
| **Local LLM** | HuggingFace transformers | Latest |

---

*Technical Architecture V3.0*
