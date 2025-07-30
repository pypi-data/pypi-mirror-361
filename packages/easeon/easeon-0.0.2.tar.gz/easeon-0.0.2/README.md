# 📦 easeon

A lightweight CLI + Python module to manage Python packages via `pip`.  
Easily **install**, **uninstall**, or **update** packages from `.txt`, `.csv`, or Python lists — with built-in virtual environment support.

---

## 🚀 Features

- 📂 Supports `.txt`, `.csv`, and Python `list[str]` inputs  
- ✅ Install, uninstall, or update pip packages  
- 🧪 Auto-create `.venv` (optional)  
- 🖥️ Works on Windows, Linux, and macOS  
- 📊 Verbose, UTF-8 friendly logging & CLI output  
- 🔁 Smart handling of already-installed or up-to-date packages  

---

## 📦 Installation

```bash
pip install easeon
```

> 💡 For test.pypi installs:  
> `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ easeon`

---

## 🧰 CLI Usage

```bash
python -m easeon.cli --install packages.txt
python -m easeon.cli --uninstall packages.csv
python -m easeon.cli --update outdated.txt
python -m easeon.cli --install packages.txt --venv
```

### 🔧 CLI Options

| Flag           | Description                                      |
|----------------|--------------------------------------------------|
| `--install`    | Install packages from `.txt` or `.csv` file      |
| `--uninstall`  | Uninstall packages from `.txt` or `.csv` file    |
| `--update`     | Update only if outdated                          |
| `--venv`       | Auto-create `.venv` if not using a virtualenv    |
| `--verbose`    | Show pip subprocess output                       |

---

## 🐍 Python API Usage

```python
from easeon.core import PythonLibInstaller

manager = PythonLibInstaller(auto_create_venv=True)

# From a list
manager.get_list(["numpy==1.24.0", "requests"])
manager.install()

# From a text file
manager.get_list_from_txt("packages.txt")
manager.update()
```

---

## 🔓 Public API Methods

| Method                  | Description                                          |
|-------------------------|------------------------------------------------------|
| `get_list(packages)`    | Load packages from a Python list                     |
| `get_list_from_txt()`   | Load packages from `.txt` (ignores `#` comments)     |
| `get_list_from_csv()`   | Load packages from `.csv` (uses first column)        |
| `install()`             | Installs all packages in `package_list`              |
| `uninstall()`           | Uninstalls listed packages                           |
| `update()`              | Updates packages only if outdated                    |
| `run_cli()`             | Used internally to power CLI                         |

---

## 📁 File Format Examples

### `packages.txt`

```txt
# Commented line
requests
numpy==1.24.0
pandas
```

### `packages.csv`

```csv
requests
flask
beautifulsoup4
```

---

## 🧪 Testing

To run unit tests:

```bash
python -m unittest discover tests
```

---

## 👤 Author

**Kiran Soorya R.S**  
📧 hemalathakiransoorya2099@gmail.com

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🌐 Links

- 📦 [PyPI Package](https://pypi.org/project/pipmanage/)
- 🧪 [Test PyPI](https://test.pypi.org/project/pipmanage/)

---

> Contributions, feedback, and stars 🌟 are welcome!
