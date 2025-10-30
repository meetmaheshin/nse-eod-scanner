"""Quick test script to verify prediction system setup"""
import sys
from pathlib import Path

print("=" * 80)
print("PREDICTION SYSTEM - SETUP CHECK")
print("=" * 80)

# Check 1: Required libraries
print("\n1. Checking required libraries...")
try:
    import sklearn
    print("   ✅ scikit-learn installed:", sklearn.__version__)
except ImportError:
    print("   ❌ scikit-learn NOT installed")
    sys.exit(1)

try:
    import joblib
    print("   ✅ joblib installed")
except ImportError:
    print("   ❌ joblib NOT installed")
    sys.exit(1)

try:
    import pandas as pd
    print("   ✅ pandas installed:", pd.__version__)
except ImportError:
    print("   ❌ pandas NOT installed")
    sys.exit(1)

try:
    import yfinance as yf
    print("   ✅ yfinance installed:", yf.__version__)
except ImportError:
    print("   ❌ yfinance NOT installed")
    sys.exit(1)

# Check 2: Historical data availability
print("\n2. Checking historical scanner data...")
output_dir = Path('eod_scanner_output')
if not output_dir.exists():
    print("   ❌ eod_scanner_output directory not found!")
    sys.exit(1)

signal_files = list(output_dir.glob('all_signals_*.csv'))
print(f"   ✅ Found {len(signal_files)} signal files")

if len(signal_files) == 0:
    print("   ⚠️  No historical data yet. Run scanner first.")
else:
    print(f"   📅 Latest: {signal_files[-1].name}")

# Check 3: Load scanner data
print("\n3. Testing scanner data loading...")
if signal_files:
    try:
        import pandas as pd
        df = pd.read_csv(signal_files[-1])
        print(f"   ✅ Loaded {len(df)} signals from latest file")
        print(f"   📊 Columns: {', '.join(df.columns[:10])}...")
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        sys.exit(1)

# Check 4: ML model status
print("\n4. Checking ML model status...")
models_dir = Path('ml_models')
model_file = models_dir / 'prediction_model.pkl'
scaler_file = models_dir / 'scaler.pkl'

if model_file.exists():
    print(f"   ✅ Model found: {model_file}")
    print(f"   ✅ Scaler found: {scaler_file}")
    print("   🎯 Model is trained and ready!")
else:
    print("   ⚠️  No trained model found")
    print("   ℹ️  Run: python prediction_engine.py (to train)")

# Check 5: Quick prediction test
print("\n5. Testing prediction engine import...")
try:
    from prediction_engine import PredictionEngine
    print("   ✅ PredictionEngine imported successfully")
    
    engine = PredictionEngine()
    print("   ✅ Engine initialized")
    
    if model_file.exists():
        if engine.load_model():
            print("   ✅ Model loaded successfully")
        else:
            print("   ⚠️  Model file exists but failed to load")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("SETUP CHECK COMPLETE")
print("=" * 80)

if len(signal_files) >= 2:
    print("\n✅ READY TO TRAIN MODEL")
    print("   Run: python prediction_engine.py")
else:
    print("\n⚠️  NEED MORE DATA")
    print("   Run EOD scanner for a few more days to collect data")
    print("   Command: python eod_scanner_nse_improved.py")

print("\n📖 See PREDICTION_SYSTEM_GUIDE.md for detailed instructions")
print("=" * 80)
