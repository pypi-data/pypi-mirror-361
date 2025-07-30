
# decitobin 🧒🔢

**decitobin** is a versatile Python tool that converts between number systems and text — now with a web-style user interface and enhanced features.

Whether you're converting decimal to binary, exploring ASCII encoding, or transforming hexadecimal strings, `decitobin` offers an interactive and beginner-friendly experience.

---

## 🌟 Features

- 🧠 Support for multiple conversions:
  - `Decimal → Binary`
  - `Binary → Decimal`
  - `ASCII → Binary`
  - `Binary → ASCII`
  - `Hex → Binary`
  - `Binary → Hex`

- 🖥️ Graphical interface with dropdown selection (Tkinter-based)
- 🚀 Instant results with detailed formatting
- 📦 Easy to install and run on any platform

---

## 💻 Installation

```bash
pip install decitobin
```

---

## 🎮 Launching the App

Run the converter using:

```bash
python -m decitobin
```

Or run your own launcher script using:

```python
from decitobin import launch_ui
launch_ui()
```

---

## ✨ Example Conversions

| Input | Mode | Output |
|-------|------|--------|
| `13` | Decimal → Binary | `1101`  
| `1101` | Binary → Decimal | `13`  
| `Hi` | ASCII → Binary | `01001000 01101001`  
| `01001000 01101001` | Binary → ASCII | `Hi`  
| `F0` | Hex → Binary | `11110000`  
| `11110000` | Binary → Hex | `F0`  

---

## 📁 Project Structure

```plaintext
decitobin/
├── __init__.py
├── ui_webstyle.py     # Web-style interface
├── converters.py      # Core logic
├── __main__.py        # CLI launcher
```

---

## 📄 License

Licensed under the MIT License.

---