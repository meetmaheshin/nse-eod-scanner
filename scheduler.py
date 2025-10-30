"""
Daily EOD Scanner Scheduler
Automatically runs the scanner at 3:35 PM every day
"""

import schedule
import time
import subprocess
from pathlib import Path
from datetime import datetime

def run_scanner():
    """Execute the EOD scanner"""
    print(f"\n{'='*60}")
    print(f"🚀 Running EOD Scanner at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    base_dir = Path(__file__).parent.absolute()
    python_exe = base_dir.parent / '.venv' / 'Scripts' / 'python.exe'
    scanner = base_dir / 'eod_scanner_nse_improved.py'
    
    try:
        result = subprocess.run(
            [str(python_exe), str(scanner)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("Scanner Output:")
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n✅ Scanner completed successfully!")
        else:
            print(f"\n❌ Scanner failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Scanner timed out (took more than 5 minutes)")
    except Exception as e:
        print(f"❌ Error running scanner: {e}")
    
    print(f"\n{'='*60}\n")

def main():
    """Main scheduler loop"""
    # Schedule for 3:35 PM daily (after market close at 3:30 PM)
    schedule.every().day.at("15:35").do(run_scanner)
    
    print("📅 EOD Scanner Scheduler Started")
    print("⏰ Scanner will run daily at 3:35 PM")
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPress Ctrl+C to stop...\n")
    
    # Optional: Run immediately on start for testing
    # Uncomment below line to test:
    # run_scanner()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Scheduler stopped by user")
