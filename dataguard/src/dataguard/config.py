from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

@dataclass
class Config:
    input_dir: Path = BASE_DIR / "data"
    db_path: Path = BASE_DIR / "data" / "warehouse" / "dataguard.db"
    log_dir: Path = BASE_DIR / "data" / "logs"
    zscore_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    contamination: float = 0.05
    random_state: int = 42

config = Config()
