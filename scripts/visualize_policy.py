import sys
from pathlib import Path

# Add V3_0/scripts to sys.path to import the real implementation
sys.path.insert(0, str(Path(__file__).parent.parent / "V3_0" / "scripts"))

from visualize_policy import main

if __name__ == "__main__":
    main() 