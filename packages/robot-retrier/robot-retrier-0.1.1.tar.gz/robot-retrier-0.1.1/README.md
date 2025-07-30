# RobotRetrier

**RobotRetrier** is an interactive GUI-based retry debugger for [Robot Framework](https://robotframework.org/).  
It automatically opens a lightweight GUI whenever a keyword fails, allowing users to inspect, modify arguments, and retry the keyword — continuing the test if it succeeds.

---

## 🚀 Features

- 🖥️ GUI pops up on failure with keyword details
- ✏️ Edit and retry failed keyword arguments
- 🔁 Continue execution if retry succeeds
- ❌ Skip retry for known "wrapper" keywords (e.g. `Run Keyword And Ignore Error`)
- 📦 Supports `--listener RobotRetrier` out-of-the-box
- ✅ Compatible with Robot Framework 7.0+
- ⚙️ Configurable behavior (e.g. auto-pass muted keywords)

---

## 📦 Installation

```bash
pip install robot-retrier
```

---

## 🧪 Usage

### Run Robot Framework with the listener:

```bash
robot --listener RobotRetrier path/to/your/tests.robot
```

✅ That's it!  
Whenever a keyword fails, a GUI will open to let you retry or skip it on the spot.

---

## 🧰 Muted Keywords

The following keywords are "muted" by default (GUI will not open if failure occurs inside them):

- `Run Keyword And Ignore Error`
- `Run Keyword And Expect Error`
- `Run Keyword And Return Status`
- `Run Keyword And Warn On Failure`
- `Wait Until Keyword Succeeds`
- `Run Keyword If`
- `Run Keywords`
- `Run Keyword Unless`
- `Continue For Loop If`
- `Exit For Loop If`

These can be customized later.

---

## 💻 Requirements

- Python 3.8+
- [Robot Framework](https://robotframework.org/) >= 7.0+

---

## 🧑‍💻 Author

**Suriya**  
GitHub: [@Suriya](https://github.com/suri-53/)  
License: MIT

---

