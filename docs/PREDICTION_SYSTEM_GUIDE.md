# 🔮 ML-Based Prediction System Guide

## Overview
This system uses **Machine Learning** to predict tomorrow's profitable trades based on historical scanner data.

## 📂 Files Created

### 1. **prediction_engine.py**
- Core ML engine
- Collects historical performance data
- Trains Random Forest classifier
- Generates predictions with confidence scores

### 2. **prediction_view.py**
- Flask web interface on port 5001
- Shows side-by-side comparison:
  - Today's signals (from scanner)
  - Tomorrow's ML predictions

## 🚀 Quick Start

### Step 1: Install Requirements
```bash
pip install scikit-learn joblib
```
(Already done if you ran the install command above)

### Step 2: Collect Historical Data & Train Model
```bash
python prediction_engine.py
```

**What this does:**
- Scans `eod_scanner_output/` for historical signal files
- For each signal, fetches next-day actual performance
- Builds training dataset
- Trains ML model (Random Forest)
- Saves model to `ml_models/` folder

**Requirements:**
- Minimum **50 historical records** (signals from multiple days)
- If you don't have enough data, run your EOD scanner for more days first

### Step 3: View Predictions on Web Interface
```bash
# Terminal 1: Run current signals view (port 5000)
python live_view_new.py

# Terminal 2: Run predictions view (port 5001)
python prediction_view.py
```

**Access:**
- Current Signals: http://127.0.0.1:5000/
- **Predictions**: http://127.0.0.1:5001/

## 📊 How It Works

### Data Collection
1. Reads historical scanner output files
2. For each signal, fetches next trading day's actual price data
3. Labels as "Profitable" (1) or "Loss" (0) based on next-day close

### Features Used for Prediction
- **Technical Scores**: score_long, score_short
- **Indicators**: RSI, ATR, Volume Ratio, MACD, Bollinger Bands
- **Patterns**: NR7, CPR, IBS, Breakouts
- **Flags**: trend_long, trend_short, volume surge, etc.

### Model Training
- **Algorithm**: Random Forest Classifier (100 trees)
- **Features**: 19 technical indicators + pattern flags
- **Target**: Next day profitable (yes/no)
- **Validation**: 80/20 train/test split

### Prediction Output
For each stock signal:
- **Prediction Score**: 0-100% confidence of profit
- **Recommendation**: STRONG BUY / BUY / HOLD / AVOID
- **Expected Return**: Estimated % return based on historical avg
- **Confidence Level**: High (≥75%) / Medium (≥60%) / Low

## 📈 Understanding Predictions

### Confidence Levels
- **75%+**: STRONG BUY - Very high confidence
- **60-75%**: BUY - Good confidence
- **Below 60%**: HOLD/AVOID - Lower confidence

### Recommendation Actions
- **STRONG BUY**: Take full position
- **BUY**: Take 50-75% position
- **HOLD**: Small position or wait
- **AVOID**: Skip this trade

### Expected Return
- Based on average return of historically profitable signals
- Typical range: 1-3% for next day
- Not guaranteed, just historical average

## 📁 Output Files

### Generated Files
1. **performance_history.csv**: Historical signals + next-day performance
2. **ml_models/prediction_model.pkl**: Trained ML model
3. **ml_models/scaler.pkl**: Feature scaler
4. **tomorrow_predictions.csv**: Latest predictions
5. **top_predictions_YYYY-MM-DD_HHMM.csv**: High-confidence picks only

### Logs
- **prediction_engine.log**: Training and prediction logs

## 🔄 Workflow

### Daily Usage (After Initial Training)
1. **3:30 PM**: Run EOD scanner
   ```bash
   python eod_scanner_nse_improved.py
   ```

2. **3:35 PM**: Generate predictions
   ```bash
   python prediction_engine.py
   ```

3. **View on Web**: 
   - Open http://127.0.0.1:5001/
   - See tomorrow's top picks with confidence scores

4. **Next Day**: Track performance, data auto-collected for retraining

### Weekly Retraining (Recommended)
```bash
# Retrain with latest week's data
python prediction_engine.py
```

## 📊 Model Performance Metrics

When you train, you'll see:
```
Model Accuracy: 68.5%
Classification Report:
              precision    recall  f1-score   support
        Loss       0.65      0.62      0.63       120
      Profit       0.71      0.74      0.73       145

Top Important Features:
1. score_long        0.15
2. rsi14            0.12
3. vol_ratio        0.11
4. macd_value       0.09
5. ibs              0.08
```

**What's Good:**
- Accuracy > 65%: Decent predictive power
- Profit recall > 70%: Catches most profitable setups
- Feature importance shows which indicators matter most

## ⚠️ Important Notes

### Limitations
1. **Requires Historical Data**: Need 50+ past signals
2. **Market Dependent**: Model trained on past market conditions
3. **Not 100% Accurate**: Typical accuracy 60-70%
4. **Next Day Only**: Predicts only tomorrow, not longer term

### Best Practices
1. **Combine with Analysis**: Don't rely solely on ML predictions
2. **Use Stop Losses**: Always protect capital
3. **Check Confidence**: Higher confidence = better odds
4. **Retrain Regularly**: Update model weekly with new data
5. **Verify Signals**: Cross-check with current view

### Risk Management
- Even 75% confidence means 25% chance of loss
- Use proper position sizing
- Diversify across multiple picks
- Set stop losses based on risk framework

## 🛠️ Troubleshooting

### "Insufficient data for training"
**Solution**: Run EOD scanner for more days to collect historical data
```bash
# Run scanner daily for 10+ days
python eod_scanner_nse_improved.py
```

### "No ML model found"
**Solution**: Train the model first
```bash
python prediction_engine.py
```

### "Error fetching next day data"
**Cause**: Yahoo Finance API issues or market closed
**Solution**: 
- Check internet connection
- Try again after a few minutes
- Some symbols may be delisted

### Web interface shows "Model Not Trained"
**Solution**: Run `python prediction_engine.py` first

## 📚 Advanced Usage

### Custom Watchlist Predictions
Edit `scanner_config.json` to use custom symbols, then:
```bash
python eod_scanner_nse_improved.py  # Scan custom list
python prediction_engine.py          # Generate predictions
```

### Analyze Historical Performance
```python
from prediction_engine import PredictionEngine

engine = PredictionEngine()
engine.collect_historical_data(days_back=30)  # Last 30 days

# Check performance_history.csv for analysis
```

### Model Tuning
Edit `prediction_engine.py` to adjust:
- `MIN_TRAINING_SAMPLES`: Default 50
- `CONFIDENCE_THRESHOLD`: Default 0.6 (60%)
- `TARGET_RETURN_PCT`: Default 2.0 (2%)

## 🎯 Success Tips

1. **Start Small**: Test with small positions while model learns
2. **Track Results**: Keep a trading journal
3. **Improve Over Time**: More historical data = better predictions
4. **Combine Signals**: Use both scanner scores AND ML confidence
5. **Market Awareness**: ML doesn't know news/events, you should!

## 📞 Support

Check logs:
- `prediction_engine.log`: ML engine logs
- `scanner.log`: Scanner logs

## 🚀 Next Steps

1. ✅ Train model with historical data
2. ✅ Generate first predictions
3. ✅ View on web interface (port 5001)
4. 📊 Paper trade for a week to validate
5. 💰 Go live with proper risk management

---

**Remember**: ML predictions are probabilities, not certainties. Always use proper risk management! 🎲📈
