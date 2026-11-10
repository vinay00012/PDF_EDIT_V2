import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_editor import app

if __name__ == "__main__":
    app.run(debug=True)

