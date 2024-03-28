import json
from dataclasses import dataclass
import codecs

@dataclass
class HyperParams:
    """
    Simple wrapper to store hyperparameters for Python-based rewriting methods.
    """

    @classmethod
    def from_json(cls, fpath):
        with codecs.open(fpath, "r", "utf-8-sig") as f:
            data = json.load(f)

        return cls(**data)
