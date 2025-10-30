"""
🚀 ONE-CLICK LAUNCHER - Runs Both Views Together!
==================================================
This starts BOTH web servers at the same time:
- Port 5000: Today's Live Signals
- Port 5001: Tomorrow's Predictions

Just run this ONE file and access both URLs!
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    print("=" * 80)
    print("🚀 STARTING BOTH WEB VIEWS")
    print("=" * 80)
    print()
    print("📊 Port 5000: Today's Live Signals")
    print("🔮 Port 5001: Tomorrow's Predictions")
    print()
    print("=" * 80)
    
    # Python executable and base directory
    python_exe = sys.executable
    base_dir = Path(__file__).parent.absolute()
    
    # Start live view (port 5000) in background
    print("\n🔄 Starting Live View (Port 5000)...")
    live_view = subprocess.Popen(
        [python_exe, str(base_dir / 'web_views' / 'live_view_new.py')],
        cwd=str(base_dir)
    )
    
    time.sleep(2)  # Wait a bit for first server to start
    
    # Start prediction view (port 5001) in background
    print("🔄 Starting Prediction View (Port 5001)...")
    pred_view = subprocess.Popen(
        [python_exe, str(base_dir / 'web_views' / 'prediction_view_simple.py')],
        cwd=str(base_dir)
    )
    
    time.sleep(2)
    
    print()
    print("=" * 80)
    print("✅ BOTH SERVERS RUNNING!")
    print("=" * 80)
    print()
    print("🌐 Access URLs:")
    print("   📊 Today's Signals:      http://127.0.0.1:5000/")
    print("   🔮 Tomorrow's Predictions: http://127.0.0.1:5001/")
    print()
    print("💡 TIP: Open both URLs in separate browser tabs!")
    print()
    print("=" * 80)
    print("⏸️  Press Ctrl+C to stop both servers")
    print("=" * 80)
    
    try:
        # Keep running until user presses Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        live_view.terminate()
        pred_view.terminate()
        print("👋 Servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
