import sys
import os

# Add the project root directory to sys.path so that imports like 'from models import ...' work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
