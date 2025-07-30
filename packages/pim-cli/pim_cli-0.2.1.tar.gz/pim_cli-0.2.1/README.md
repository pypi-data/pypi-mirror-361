# pim-cli

`pim` is a CLI tool to declaratively install and manage machine learning models from a `Pimfile`.

**THIS IS VERY MUCH IN DEVELOPMENT AT THE MOMENT WARNING**

## 🚀 Why Pim?

Modern AI workflows require more than just installing Python packages — they depend on large pretrained models, often fetched from different frameworks (like Hugging Face, TorchVision, or Scikit-learn) with inconsistent interfaces and storage behaviors.

**Pim** is a lightweight, framework-agnostic CLI tool that solves this by treating models as first-class dependencies — just like packages — with simple, reproducible install workflows.

### ✅ What Pim Does
- Installs pretrained models from Hugging Face, TorchVision, and Scikit-learn
- Uses a `Pimfile` (like `Pipfile` or `requirements.txt`) to declare which models your project depends on
- Centralizes model downloads in a shared cache (`~/.pim`) or a user-defined directory
- Supports authentication for gated models (e.g., Hugging Face token access)
- Lets you run `pim install` from anywhere — no manual Python scripting required

### 🧠 Why It’s Different
| Feature                          | pip / conda            | pim                           |
|----------------------------------|-------------------------|-------------------------------|
| Installs Python packages         | ✅                      | ❌                            |
| Declarative install file (`Pimfile`)| ✅                     | ✅                            |
| Installs pretrained ML models    | ❌                      | ✅                            |
| Unified CLI for multiple frameworks | ❌                   | ✅                            |
| Model caching & directory control| ❌                      | ✅                            |
| Handles gated models & auth      | ❌                      | ✅                            |

Pim doesn’t replace tools like pip or conda — it **complements them** by handling the growing complexity of working with large-scale pretrained model artifacts in a clean, declarative, and scriptable way.



## Installation

```bash
pip install pim-cli
```

## Usage

```bash
pim install
```

## License

MIT
