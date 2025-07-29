# 📁 file-organizer-cli

A Python command-line utility to organize messy folders — clean up files by extension into neat subfolders like `Images`, `Documents`, `Code`, and more.

---

## 🚀 Features

- ✅ Organize files by extension (e.g. `.jpg`, `.pdf`, `.mp3`)
- ✅ Dry-run mode (simulate before actually moving files)
- ✅ Colored console output using `rich`
- ✅ Lightweight and easy to run
- ✅ Clean, readable CLI interface

---

## 📦 Installation

```bash
pip install rich
```

> No need for PyPI — just clone the repo and run via Python.

---

## 💻 Usage

```bash
python main.py --path /your/folder
```

### Example with dry-run mode:

```bash
python main.py --path ~/Downloads --dry-run
```

---

## 🧪 Command-Line Arguments

| Argument      | Description                            |
|---------------|----------------------------------------|
| `--path`      | Target folder to organize (**required**) |
| `--dry-run`   | Show what would move, without doing it |

---

## 🛠️ Extension Mapping (Default)

| Category   | Extensions                             |
|------------|----------------------------------------|
| Images     | `.jpg`, `.jpeg`, `.png`, `.gif`        |
| Documents  | `.pdf`, `.docx`, `.txt`, `.xlsx`       |
| Music      | `.mp3`, `.wav`                         |
| Code       | `.py`, `.js`, `.html`, `.css`          |
| Archives   | `.zip`, `.tar`, `.gz`                  |
| Videos     | `.mp4`, `.mov`, `.avi`                 |
| Others     | Everything else                        |

---

## 🧑‍💻 Developer Info

- **Author**: Qazi Arsalan  
- **GitHub**: [https://github.com/](https://github.com/)  
- **License**: MIT

---

## 📝 License

Licensed under the [MIT License](LICENSE).

---

## 🙌 Contributions

PRs and suggestions are welcome!  
This is just the beginning — more features coming soon:

- Recursive mode  
- Organize by date  
- Configurable mappings  
- Undo/rollback mode  
- Logging and summaries
