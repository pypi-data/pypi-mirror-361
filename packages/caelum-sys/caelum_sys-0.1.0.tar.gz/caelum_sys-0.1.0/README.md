# caelum-sys

**caelum-sys** is a human-friendly system automation toolkit for Python.  
It allows natural language commands to control local system behavior — perfect for scripting, AI agents, or personal assistants like Caelum.

---

## ✨ Features

- 🔌 Plugin-based architecture for easy command extension
- 🧠 `do("open notepad")` style control
- 🧪 Fully tested with `pytest`
- 🧩 Built-in plugins: file ops, browser control, Spotify, system stats, screenshots
- 💬 Designed for LLM integration (text in, result out)

---

## 📦 Installation
pip install caelum-sys

Or for local development:
git clone https://github.com/blackbeardjw/caelum-sys.git
cd caelum-sys
pip install -e .

🚀 Usage
Python:
    from caelum_sys import do

    do("open notepad")
    do("play spotify chill vibes")
    do("list files in Downloads")

CLI:
    caelum-sys "get cpu usage"
    caelum-sys "open browser"

| Plugin       | Example Command                              |
| ------------ | -------------------------------------------- |
| Spotify      | `play spotify chill vibes`                   |
| Filesystem   | `list files in .`, `delete file example.txt` |
| Browser      | `open browser`, `open url github.com`        |
| Screenshot   | `take screenshot`                            |
| System Stats | `get cpu usage`, `get memory stats`          |


🧩 Adding Your Own Plugin
Create a .py file in caelum_sys/plugins/ and use the decorator:
    from caelum_sys.registry import register_command

    @register_command("run my task")
    def my_command(command: str):
        return "Command executed!"

🧪 Running Tests
    pytest tests

    All plugins are safely mocked (no system damage during testing).