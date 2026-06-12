# Architecture

## Inflation Prediction System - Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   INFLATION PREDICTION SYSTEM                   │
│                        Version 3.0.0                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  ORCHESTRATOR    │
                    │  (main_orchestrator.py)
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │   PHASE 1    │ │   PHASE 2    │ │   PHASE 3    │
        │   Data       │ │   LLM        │ │   ML Model   │
        │ Ingestion    │ │   Sentiment  │ │   Training   │
        └────────┬─────┘ └────────┬─────┘ └────────┬─────┘
                 │                │                │
                 ▼                ▼                ▼
        ┌──────────────────────────────────────────────┐
        │      UNIFIED DATASET + SENTIMENT SCORES      │
        │              (enriched_dataset.csv)          │
        └──────────────────────────────────────────────┘
                         │
                ┌────────┼────────┐
                │        │        │
                ▼        ▼        ▼
            ┌──────────┐ ┌──────────────┐
            │ PHASE 4  │ │   PHASE 5    │
            │Government│ │   HTML       │
            │ Insights │ │   Dashboard  │
            └────┬─────┘ └────────┬─────┘
                 │                │
                 ▼                ▼
        ┌──────────────────────────────────────────────┐
        │          FINAL OUTPUTS                       │
        │  - index.html (Dashboard)                    │
        │  - government_report.{json,txt}              │
        │  - model_export.json (ML Model)              │
        │  - execution_log.json (Trace)                │
        └──────────────────────────────────────────────┘
```

### Project Structure

```
inflation-prediction/
├── src/                           # Source code
│   ├── __init__.py
│   └── inflation_prediction/      # Main package
│       ├── __init__.py
│       ├── main.py               # CLI entry point
│       ├── main_orchestrator.py  # Phase orchestrator
│       ├── data_ingestion.py     # Phase 1
│       ├── llm_sentiment_pipeline.py  # Phase 2
│       ├── model_training.py     # Phase 3
│       ├── llm_government_insights.py # Phase 4
│       └── html_factory.py       # Phase 5
│
├── public/                        # Static assets
│   └── index.html               # Dashboard
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_orchestrator.py
│
├── deployment/                    # Docker & cloud configs
│   ├── Dockerfile
│   └── kubernetes-manifest.yaml (future)
│
├── docs/                          # Documentation (future)
│   ├── architecture.md
│   └── api-reference.md
│
├── Configuration Files
│   ├── pyproject.toml            # Project metadata
│   ├── requirements.txt          # Dependencies
│   ├── pytest.ini                # Test configuration
│   ├── Makefile                  # Common commands
│   ├── .gitignore
│   ├── .env.example
│   └── docker-compose.yml
│
└── Documentation
    ├── README.md                 # Quick start
    ├── QUICK_START.md           # 60-second guide
    ├── SYSTEM_DOCUMENTATION.md  # Complete reference
    ├── TECHNICAL_ARCHITECTURE.md# Engineering details
    ├── DEPLOYMENT_GUIDE.md      # Deployment steps
    ├── FILES_MANIFEST.txt       # File listing
    └── PROJECT_COMPLETION_REPORT.md
```

### Data Flow Pipeline

```
PHASE 1: DATA INGESTION
├─ BIInflationScraper
│  └─ Source: bi.go.id (with synthetic fallback)
├─ ExchangeRateCollector
│  └─ Source: Yahoo Finance (USD/IDR)
├─ MacroeconomicDataCollector
│  └─ Sources: BI Rate, IHK, news text, social media
└─ DataPipeline.build_unified_dataset()
   └─ Output: unified_dataset.csv (172 KB, 36 rows)

PHASE 2: LLM SENTIMENT ANALYSIS
├─ Monthly news batches → LLM → news_sentiment_score
├─ Monthly social batches → LLM → social_sentiment_score
├─ 4 backends: OpenAI, Anthropic, HuggingFace, Mock
└─ Output: enriched_dataset.csv (186 KB with sentiment)

PHASE 3: RANDOM FOREST MODELING
├─ Features: [inflation, bi_rate, exchange_rate, ihk, news_sentiment, social_sentiment]
├─ Target: inflation_t+1 (next month)
├─ Validation: TimeSeriesSplit (no look-ahead bias)
├─ Performance: R² = 0.892, RMSE = ±0.249%
└─ Output: model_export.json (with JS formula)

PHASE 4: GOVERNMENT INSIGHTS
├─ LLM prompt: Current inflation + prediction + feature importances
├─ Output 1: Impact analysis (fiscal, purchasing power, policy)
├─ Output 2: Policy recommendations (3 timelines)
└─ Output: government_report.{txt,json}

PHASE 5: HTML DASHBOARD
├─ Embeds: model coefficients, historical data, charts
├─ Charts: Inflation history, feature importance
├─ Simulator: 4 interactive sliders
├─ Client-side: JavaScript prediction engine (no server)
└─ Output: index.html (25 KB, fully standalone)
```

### Component Classes

#### Phase 1: Data Ingestion
```python
class BIInflationScraper:
    def scrape_inflation_data() -> pd.DataFrame
    # Returns: monthly inflation rates

class ExchangeRateCollector:
    def get_exchange_rates(ticker: str) -> pd.DataFrame
    # Returns: USD/IDR monthly rates

class MacroeconomicDataCollector:
    def get_macro_data() -> pd.DataFrame
    # Returns: BI Rate, IHK, text data

class DataPipeline:
    def build_unified_dataset() -> pd.DataFrame
    # Merges all sources with temporal alignment
```

#### Phase 2: LLM Sentiment
```python
class LLMSentimentAnalyzer:
    def __init__(backend: str)  # openai|anthropic|huggingface|mock
    def analyze_batch(text: str) -> Tuple[float, dict]
    # Returns: sentiment score [-1.0, +1.0]

class SentimentPipeline:
    def process_dataset(df: pd.DataFrame) -> pd.DataFrame
    # Adds news_sentiment_llm_score, social_media_sentiment_llm_score
```

#### Phase 3: ML Model
```python
class RandomForestInflationModel:
    def prepare_training_data() -> Tuple[np.ndarray, np.ndarray]
    def train_with_time_series_split() -> dict
    def export_linear_approximation() -> dict
    def export_for_javascript() -> dict

class ModelTrainingPipeline:
    def execute() -> dict
```

#### Phase 4: Government Insights
```python
class GovernmentInsightGenerator:
    def __init__(backend: str)  # Same backends as Phase 2
    def generate_insights(context: dict) -> Tuple[str, str]
    # Returns: (impact_analysis, policy_recommendations)

class InsightsPipeline:
    def execute(model_context: dict) -> dict
```

#### Phase 5: Dashboard
```python
class HTMLFactory:
    def generate_html(data: dict) -> str
    # Returns: complete HTML with embedded data & JavaScript

class HTMLFactoryPipeline:
    def generate_dashboard() -> str
    # Saves index.html
```

### Data Structures

#### Unified Dataset (Phase 1 Output)
```
Column                  | Type    | Source
─────────────────────────────────────────────────
Date (index)            | DateTime| Monthly
inflation_rate          | float   | BI
bi_rate                 | float   | BI
exchange_rate_usd_idr   | float   | Yahoo Finance
ihk_index               | float   | BI
news_text               | str     | Mock
social_media_text       | str     | Mock
```

#### Enriched Dataset (Phase 2 Output)
```
[All from Unified Dataset] +
news_sentiment_llm_score        | float [-1, +1] | LLM
social_media_sentiment_llm_score| float [-1, +1] | LLM
```

#### Model Export (Phase 3 Output)
```json
{
  "model_type": "RandomForestRegressor",
  "n_estimators": 100,
  "features": ["inflation", "bi_rate", "exchange_rate", "ihk", "news_sentiment", "social_sentiment"],
  "coefficients": {linear approximation},
  "feature_importance": {ranking},
  "metrics": {
    "r2_score": 0.892,
    "rmse": 0.249,
    "mae": 0.124
  },
  "javascript_formula": "function predictInflation(...) { ... }"
}
```

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.10+ |
| **Data** | pandas, numpy | 2.0+, <2 |
| **ML** | scikit-learn | 1.3+ |
| **Finance** | yfinance | Latest |
| **Web Scraping** | BeautifulSoup4, requests | Latest |
| **LLM APIs** | OpenAI, Anthropic | Latest |
| **Local LLM** | HuggingFace Transformers | Latest |
| **Frontend** | Tailwind CSS, Chart.js | v3, v4 |
| **Containers** | Docker | Latest |

### Deployment Architectures

#### Local Development
```
Local Machine
    ├── Python venv
    ├── Makefile commands
    └── Output: inflation_prediction_output/
```

#### Docker
```
Docker Container
    ├── Python 3.11 + deps
    ├── Single execution
    └─ Volume mount: inflation_prediction_output/
```

#### Cloud (AWS ECS)
```
AWS ECR (Image Registry)
    ↓
ECS Cluster
    ├── Task Definition
    ├── Service
    └── Output: S3 bucket
```

### Security Considerations

1. **API Keys**: Use environment variables (.env), never hardcode
2. **Input Validation**: Sanitize all external data
3. **Rate Limiting**: Respect LLM API quotas
4. **Error Handling**: Graceful fallbacks for all failures
5. **Logging**: Structured JSON logging for audit trail

### Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Phase 1 (Data) | ~5s | Network dependent |
| Phase 2 (LLM) | ~10s | Mock backend |
| Phase 3 (ML) | ~8s | TimeSeriesSplit CV |
| Phase 4 (Insights) | ~3s | Mock backend |
| Phase 5 (HTML) | ~2s | Template rendering |
| **Total** | **~30s** | Single-threaded |

### Future Enhancements

- [ ] Parallel data ingestion across sources
- [ ] Batch LLM processing with rate limiting
- [ ] Result caching & incremental updates
- [ ] Real-time data streaming
- [ ] Multiple models comparison (ensemble)
- [ ] REST API for predictions
- [ ] Web UI for configuration
- [ ] Kubernetes deployment templates
- [ ] CI/CD pipeline integration
- [ ] Monitoring & alerting

