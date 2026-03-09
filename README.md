# Vibrante-Node

**Vibrante-Node** is a professional, Python-based desktop application designed for creating and executing complex visual workflows. Combining a powerful node-based canvas with an integrated professional code editor, it empowers users to build modular data pipelines with real-time feedback and high-performance execution.

---

## 📸 Screenshots

![Vibrante-Node UI 1](shots/01.PNG)
![Vibrante-Node UI 2](shots/02.PNG)
![Vibrante-Node UI 3](shots/03.PNG)

---

## 🌟 Latest Enhancements

### 💻 Professional Code Editor
The built-in Node Builder now features a specialized source code editor designed for Python development:
- **IntelliSense:** Smart code completion suggestions.
- **Real-time Linting:** Instant error detection as you type.
- **Advanced Editing:** Auto-indentation, bracket matching, and auto-closing.
- **Dracula Theme:** High-contrast syntax highlighting for maximum readability.

### 📁 Smart Node Library
- **Search & Categories:** Quickly find nodes using the real-time search bar or browse by organized categories (Math, Logic, IO, etc.).
- **Visual Feedback:** High-quality **SVG icons** for every node in the library and on the canvas.

### 🎭 Modern UI & Theming
- **Dynamic Themes:** Switch between sleek **Dark Mode** and standard **Light Mode** instantly.
- **Improved Canvas:** Nodes now feature clear port labels and integrated widgets for direct data interaction.
- **Interactive Toolbar:** Icon-based toolbar with tooltips for intuitive workflow control.

---

## 🚀 Key Features

- **Interactive Node Widgets:** Embed Text Boxes, Sliders, Dropdowns, and File Selectors directly into your nodes.
- **Advanced Connections:** Bidirectional wire dragging, single-input enforcement, and redrag-to-disconnect.
- **Asynchronous Engine:** Background execution via `asyncio` keeps the UI responsive during processing.
- **Fancy Event Log:** Color-coded dockable window for real-time execution tracking and error reporting.

---

## 📥 Installation & Setup

### Prerequisites
- Python 3.10+
- `pip`

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/KamalTD/Vibrante-Node.git
   cd Vibrante-Node
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App:**
   ```bash
   python ./src/main.py
   ```

---

## 📚 Documentation

Detailed documentation is available for both users and developers:
-   📖 **[User Guide](USER_GUIDE.md)**: How to use the interface, build workflows, and use the Node Builder.
-   🛠️ **[Developer Documentation](DEVELOPER.md)**: Technical architecture, data flow, and how to extend the system.
-   📄 **[Full Feature List](DOCUMENTATION.md)**: Detailed breakdown of all technical features.

---

## 📂 Project Structure

```text
├── icons/              # SVG icon set for the node library
├── nodes/              # JSON definitions for custom nodes
├── src/
│   ├── core/           # Engine, Registry, and Graph logic
│   ├── ui/             # PyQt components (Canvas, Editor, Library)
│   └── main.py         # Application entry point
├── workflows/          # Saved pipeline files (.json)
└── DOCUMENTATION.md    # Full technical feature list
```

---

## 📜 License
This project is provided for educational and developmental purposes. Feel free to fork and extend!
