"""Check Python version compatibility for TensorFlow"""
import sys

print(f"Python version: {sys.version}")
print(f"Python version info: {sys.version_info}")

major, minor = sys.version_info[:2]
print(f"\nMajor: {major}, Minor: {minor}")

if major == 3 and minor in [11, 12]:
    print("✅ Python version is compatible with TensorFlow!")
    print("You can proceed with: pip install -r requirements.txt")
elif major == 3 and minor >= 13:
    print("❌ Python 3.13+ is not supported by TensorFlow.")
    print("Please install Python 3.11 or 3.12 from https://www.python.org/downloads/")
else:
    print(f"⚠️  Python {major}.{minor} may not be compatible with TensorFlow.")
    print("TensorFlow supports Python 3.8-3.12")

