
# 2048lite 🎮

**2048lite** is a lightweight Python package that launches the classic 2048 game directly from a local HTML file or a Pygame interface.

No dependencies beyond `pygame`, no frameworks, no internet — just install and play.

---

## 🚀 Features

- 🕹️ Play 2048 instantly from Python
- 💡 HTML version included (offline play)
- 🎮 Optional Pygame version for retro style
- 📦 Simple install, simple launcher

---

## 📦 Installation

```bash
pip install 2048lite
```

---

## 🎮 How to Play

```python
from 2048lite import launch_game

launch_game()  # Launch HTML game in your browser
```

Optional:

```python
from 2048lite import play_pygame

play_pygame()  # Launch the Pygame version
```

---

## 🧱 Requirements

- Python >= 3.7  
- Pygame >= 2.1.0 (installed automatically)

---

## 📄 License

Released under the MIT License.
