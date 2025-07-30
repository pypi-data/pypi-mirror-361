# sessionstash

> **Save & restore your Python interpreter workspace in one command** - an R-style snapshotter powered by `dill`.

[![PyPI](https://img.shields.io/pypi/v/sessionstash.svg)](https://pypi.org/project/sessionstash/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ Key Features

* **One-liner snapshot & restore** of the current interpreter via `dill`
* Skips heavyweight / un-pickleable objects by default (customisable)
* **CLI included** - `python -m sessionstash save|load`
* Pure-Python implementation; only runtime dependency is **`dill`**

---

## 📦 Installation

```bash
pip install sessionstash
```

*(For development: `pip install -e .[dev]`)*

---

## 🚀 Quick Start

```python
import sessionstash as ss

counter = 42
message = "Hello, workspace!"

ss.save_workspace("snapshot.dill")   # Save everything

del counter, message

ss.load_workspace("snapshot.dill")   # Restore
print(counter, message)              # 42 Hello, workspace!
```

### CLI usage

```bash
# Save the current session
python -m sessionstash save my_session.dill

# Load it back and drop into an IPython shell
python -m sessionstash load my_session.dill --shell
```

---

## 🛠️ Public API

| Function         | Description                                             | Signature                              |
| ---------------- | ------------------------------------------------------- | -------------------------------------- |
| `save_workspace` | Serialize a namespace (default `globals()`) to disk     | `save_workspace(path, namespace=None)` |
| `load_workspace` | Inject a serialized namespace back into the current one | `load_workspace(path, namespace=None)` |

---

## 🔒 Security Notice

A dill/pickle file can execute **arbitrary code when loaded**.
Never run `load_workspace()` on data from an untrusted source.

---

## 🗺️ Roadmap

* [ ] Optional encryption / signature verification
* [ ] Size & timing report for each stored object
* [ ] VS Code / IPython extensions for automatic snapshots

---

## 🤝 Contributing

1. Clone: `git clone https://github.com/<yourname>/sessionstash`
2. Install dev deps: `pip install -e .[dev]`
3. Open a pull request - issues and PRs are welcome!

---

## 📄 License

`sessionstash` is released under the **MIT License** © 2025 Jiwoong Kim.
