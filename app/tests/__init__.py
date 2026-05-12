import sys
from pathlib import Path

# Add the app directory to sys.path so relative imports work
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
