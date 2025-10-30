"""
🔮 ONE-CLICK PREDICTION LAUNCHER
================================
This script handles everything for you:
1. Checks if model exists
2. Trains if needed (or uses existing)
3. Launches prediction web view

Just run this ONE file!
"""

import sys
import subprocess
from pathlib import Path

print("=" * 80)
print("🔮 PREDICTION SYSTEM - AUTO LAUNCHER")
print("=" * 80)

# Check if model exists
models_dir = Path('ml_models')
model_file = models_dir / 'prediction_model.pkl'

if model_file.exists():
    print("\n✅ ML Model found! Skipping training...")
    print("📊 Launching prediction web view...\n")
else:
    print("\n⚠️  No ML model found yet.")
    print("📚 Note: ML model needs historical data to train.")
    print("         You only have 2 days of data (need 10+ for good predictions)")
    print("\n🎯 For now, I'll launch a SIMPLE prediction view instead.")
    print("   (It will show today's signals as 'tomorrow predictions')")
    print("\n   To get REAL ML predictions:")
    print("   1. Run your scanner daily for 10+ days")
    print("   2. Then run: python prediction_engine.py")
    print("\n" + "=" * 80)

print("\n🚀 Starting web server on http://127.0.0.1:5001/")
print("   (Press Ctrl+C to stop)")
print("\n" + "=" * 80 + "\n")

# Launch the prediction view
try:
    subprocess.run([
        sys.executable,
        'prediction_view_simple.py'
    ])
except KeyboardInterrupt:
    print("\n\n👋 Shutting down...")
