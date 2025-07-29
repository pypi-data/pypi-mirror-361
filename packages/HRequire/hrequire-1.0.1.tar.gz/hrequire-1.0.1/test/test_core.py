import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from hrequire.core import cli 

if __name__ == "__main__":
    cli()
