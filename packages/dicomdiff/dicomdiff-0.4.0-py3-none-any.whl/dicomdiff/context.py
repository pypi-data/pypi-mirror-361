from dataclasses import dataclass
from typing import Optional


@dataclass
class ComparisonContext:
    pseudonymizer_a_name: Optional[str] = None
    pseudonymizer_b_name: Optional[str] = None
    dataset_description: Optional[str] = None
    exception_path: str = "exception.json"
