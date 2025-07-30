import yaml
from pathlib import Path
import logging

SUPPORTED_FRAMEWORKS = {"huggingface", "torchvision", "sklearn"}

def load_pimfile(pimfile_path):
    pimfile = Path(pimfile_path)

    if not pimfile.exists():
        raise FileNotFoundError(f"Pimfile not found at {pimfile.resolve()}")

    with open(pimfile, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Pimfile must be a YAML mapping (framework -> list of models)")

    parsed = {}
    for framework, models in data.items():
        if framework not in SUPPORTED_FRAMEWORKS:
            logging.warning(f"Skipping unsupported framework: {framework}")
            continue

        if not isinstance(models, list):
            raise ValueError(f"Expected list of models under '{framework}'")

        parsed[framework] = models

    return parsed
