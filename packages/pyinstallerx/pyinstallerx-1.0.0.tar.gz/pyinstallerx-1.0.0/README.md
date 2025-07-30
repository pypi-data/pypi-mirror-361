# pyinstallerx

**pyinstallerx** is a Python utility that helps you **install, uninstall, and update Python packages** programmatically — with built-in support for virtual environments and smart CLI launching across platforms.

---

## 🚀 Features

- ✅ Install packages from `.txt`, `.csv`, or Python list
- 🔄 Update outdated packages with version checks
- 🧹 Uninstall packages in bulk
- 🛠 Auto-detect and optionally create a virtual environment
- 💻 Opens system terminal (Windows, macOS, Linux) to run pip commands
- ✨ Simple API, also usable via CLI

---

## 📦 Installation

```bash
pip install pyinstallerx
```

---

## 🧠 Basic Usage

```python
from pyinstallerx import PythonLibInstaller

manager = PythonLibInstaller(auto_create_venv=True)
manager.get_list(['requests', 'pandas'])
manager.install()
```

---

## 🛠 CLI Usage

```bash
pyinstallerx --install requirements.txt
pyinstallerx --uninstall packages.csv
pyinstallerx --update packages.txt
pyinstallerx --venv
```

> You can pass `.txt` or `.csv` files as input.

---

## 💡 Example CSV / TXT Format

**packages.txt**:
```
requests
numpy==1.25.0
```

**packages.csv**:
```
requests
flask==2.3.0
```

---

## 🧪 Cross-Platform Terminal Support

- **Windows:** Opens `cmd`
- **Linux:** Opens `x-terminal-emulator`
- **macOS:** Uses AppleScript to launch Terminal

---

## 🪪 License

MIT License © 2025 [Kiran Soorya R.S](mailto:hemalathakiransoorya2099@gmail.com)
