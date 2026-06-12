# Quick Start Guide - Inflation Prediction System

## 🚀 60-Second Startup

### Step 1: Verify Setup
```bash
cd ./
ls -la index.html  # Should exist
```

### Step 2: Open Dashboard
**Option A: Direct File (Recommended)**
```bash
# Linux/Mac
open index.html

# Or copy this path to your browser:
file://./index.html
```

**Option B: Python HTTP Server**
```bash
cd ./
python -m http.server 8000

# Then visit: http://localhost:8000/index.html
```

---

## 🎮 Interactive Dashboard Walkthrough

### What You'll See:

1. **Top Section**: Prediction metrics
   - **Predicted Inflation**: 3.08% (color-coded badge)
   - **Model Accuracy**: 89.2% (R² score)
   - **Error Range**: ±0.25% (RMSE confidence)

2. **Charts Section**: 
   - Historical inflation (blue line) + predicted point (red dashed)
   - Feature importance breakdown (which factors matter most)

3. **Simulator Panel** ⭐ (Main Interactive Feature)
   - **4 Sliders**: BI Rate, Exchange Rate, News Sentiment, Social Sentiment
   - **Real-time Output**: Simulated inflation badge updates as you move sliders
   - **Color Feedback**: Green (stable) → Yellow → Red (high inflation)

4. **Government Analysis**:
   - Impact Assessment (scroll down)
   - Policy Recommendations (scroll further)

---

## 🔄 Re-running the Full Pipeline

### To Update Predictions with New Data:

```bash
cd ./

# Activate environment (if needed)
source ./.venv/bin/activate

# Run complete pipeline
./.venv/bin/python main_orchestrator.py

# Results will be in: inflation_prediction_output/
# Latest dashboard: index.html (copied to main dir)
```

**Expected Duration**: ~30 seconds

---

## 📊 File Structure & Outputs

```
inflation-prediction/
├── index.html ⭐ MAIN OUTPUT (open in browser)
│
├── inflation_prediction_output/ (all generated files)
│   ├── index.html (same as above)
│   ├── unified_dataset.csv (36 months of raw features)
│   ├── enriched_dataset.csv (with sentiment scores)
│   ├── model_export.json (model coefficients for JS)
│   ├── government_report.json (structured analysis)
│   ├── government_report.txt (human-readable)
│   └── execution_log.json (pipeline trace)
│
├── main_orchestrator.py (main entry point)
├── data_ingestion.py (Phase 1: data collection)
├── llm_sentiment_pipeline.py (Phase 2: NLP analysis)
├── model_training.py (Phase 3: Random Forest)
├── llm_government_insights.py (Phase 4: reports)
└── html_factory.py (Phase 5: dashboard generation)
```

---

## 🎛️ Using the Simulator: 3 Example Scenarios

### Scenario 1: "What if BI Raises Rates?"
```
Action: Drag BI Rate slider from 6.0% → 8.0%
Result: Simulated inflation badge shows prediction drops
Why: Higher rates cool demand, reduce inflation pressure
```

### Scenario 2: "What if Rupiah Weakens?"
```
Action: Drag Exchange Rate slider from 15,500 → 17,000 IDR/USD
Result: Simulated inflation badge shows prediction increases  
Why: Weak rupiah → import costs rise → inflation rises
```

### Scenario 3: "Positive Sentiment Shock"
```
Actions:
- Drag News Sentiment: 0.0 → +0.7
- Drag Social Sentiment: 0.0 → +0.5
Result: Simulated inflation badge shows prediction DROPS
Why: Public optimism reduces precautionary spending, lowers inflation pressure
```

---

## 🔍 Interpreting Results

### **Color Codes for Inflation Badge:**
- 🟢 **GREEN** (< 2.5%): Excellent, below BI target
- 🟡 **YELLOW** (2.5-4.0%): Good, within BI target band
- 🔴 **RED** (> 4.0%): Alert, near ceiling or above

### **Feature Importance Rankings:**
Shows which inputs drive the prediction most:
- **78.4%**: Historical inflation (past predictor of future)
- **16.4%**: Social media sentiment (public expectations)
- **2.7%**: News sentiment
- **0.9%**: Consumer Price Index (IHK)
- Others: < 1% each

### **Model Accuracy (R² = 0.89):**
- 89% of inflation variation explained by model
- Very reliable for policy simulation
- Remaining 11% from unpredicted shocks

---

## 🛠️ Customization Quick Tips

### Change LLM Backend (Sentiment Analysis)

Edit `main_orchestrator.py` line ~305:
```python
# From:
orchestrator = InflationPredictionOrchestrator(llm_backend="mock", ...)

# To:
orchestrator = InflationPredictionOrchestrator(llm_backend="openai", ...)
# or: "anthropic", "huggingface"
```

### Change Historical Data Window

Edit `main_orchestrator.py` line ~304:
```python
# From:
orchestrator = InflationPredictionOrchestrator(months=36, ...)

# To:
orchestrator = InflationPredictionOrchestrator(months=60, ...)  # 5 years
```

### Change Dashboard Theme Color

Edit `html_factory.py` line ~44:
```python
# From:
self.theme_color = "#1e3a8a"  # Deep corporate blue

# To:
self.theme_color = "#059669"  # Green
self.theme_color = "#0891b2"  # Cyan
self.theme_color = "#7c3aed"  # Purple
```

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Dashboard won't open | Copy full path to browser or use Python HTTP server |
| Sliders not responsive | Clear browser cache (Ctrl+Shift+Delete) |
| Pipeline fails with NumPy error | `pip install "numpy<2"` |
| No internet (API timeouts) | System uses synthetic data automatically |
| Want API-driven sentiment | Set env var: `export OPENAI_API_KEY="sk-..."` |

---

## 📋 System Specs Summary

| Component | Spec |
|-----------|------|
| **Historical Data** | 36 months (3 years) |
| **Features** | 6 predictors + sentiment |
| **Model** | Random Forest (100 trees) |
| **Validation** | TimeSeriesSplit (prevents look-ahead bias) |
| **Accuracy** | R² = 0.89, RMSE = ±0.25% |
| **Dashboard** | Standalone HTML (24 KB) |
| **Simulation** | Real-time JavaScript engine |
| **Execution Time** | ~30 seconds full pipeline |

---

## 📞 Need Help?

1. **Dashboard not showing**: Check browser console (F12) for JS errors
2. **Data not updating**: Re-run pipeline: `python main_orchestrator.py`
3. **Slider values wrong**: Check feature ranges in `model_export.json`
4. **Reports missing**: Verify `government_report.txt` generated successfully
5. **Still stuck**: Check `execution_log.json` for detailed error trace

---

## ✅ System Status

**Status**: ✓ Fully Operational  
**Last Run**: [Generated Date]  
**Prediction**: 3.08% (within target)  
**Dashboard**: Ready to use  
**Simulation Engine**: Active

**→ Open `index.html` now to begin exploring!**

---

*AI-Driven Inflation Prediction System V3 | Production Release*
