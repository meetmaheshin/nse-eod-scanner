# ML Models Directory

This directory will contain trained machine learning models.

## Current Status: Empty (Not Trained Yet)

### Why Empty?
- ML training requires 10+ days of historical scanner data
- Currently have only 2 days of data
- Using simple score-based predictions for now

### What Will Be Here:
- `prediction_model.pkl` - Trained Random Forest model
- `scaler.pkl` - Feature scaler for normalization
- `model_metadata.json` - Training information

### When to Train:
After accumulating 10+ days of scanner output, run:
```bash
python ml_prediction/prediction_engine.py
```

This will train the model and save it here.
