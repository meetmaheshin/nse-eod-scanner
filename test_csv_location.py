"""
Test script to verify CSV files are found in deployment
"""
from pathlib import Path
import glob

print("=" * 60)
print("CSV FILE LOCATION TEST")
print("=" * 60)

# Test current directory
print(f"\nCurrent working directory: {Path.cwd()}")

# Test different path approaches
print("\n--- Testing Path Approaches ---")

# Approach 1: Relative path
print("\n1. Relative path 'eod_scanner_output':")
path1 = Path('eod_scanner_output')
print(f"   Path: {path1.absolute()}")
print(f"   Exists: {path1.exists()}")
if path1.exists():
    files = list(path1.glob('*.csv'))
    print(f"   CSV files found: {len(files)}")
    for f in files:
        print(f"     - {f.name}")

# Approach 2: Parent directory
print("\n2. Using __file__ parent:")
base_dir = Path(__file__).parent
output_dir = base_dir / 'eod_scanner_output'
print(f"   Base dir: {base_dir.absolute()}")
print(f"   Output dir: {output_dir.absolute()}")
print(f"   Exists: {output_dir.exists()}")
if output_dir.exists():
    files = list(output_dir.glob('*.csv'))
    print(f"   CSV files found: {len(files)}")
    for f in files:
        print(f"     - {f.name}")

# Approach 3: Go up from web_views
print("\n3. Going up from web_views/:")
base_dir2 = Path(__file__).parent.parent
output_dir2 = base_dir2 / 'eod_scanner_output'
print(f"   Base dir: {base_dir2.absolute()}")
print(f"   Output dir: {output_dir2.absolute()}")
print(f"   Exists: {output_dir2.exists()}")
if output_dir2.exists():
    files = list(output_dir2.glob('*.csv'))
    print(f"   CSV files found: {len(files)}")
    for f in files:
        print(f"     - {f.name}")

# List all files in current directory
print("\n--- Files in current directory ---")
for item in Path('.').iterdir():
    print(f"  {item.name}{'/' if item.is_dir() else ''}")

# List files in parent directory
print("\n--- Files in parent directory ---")
for item in Path('..').iterdir():
    print(f"  {item.name}{'/' if item.is_dir() else ''}")

print("\n" + "=" * 60)
