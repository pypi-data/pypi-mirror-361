# EasWin

EasWin is a simple and lightweight Python module for building GUIs using Tkinter and Pygame with easy keyboard and mouse support.

## Installation

```bash
pip install easwin
```

## Example

```python
import easwin

counter = 0

def setup():
    global counter, lab
    lab = easwin.soft.label(text=f"Count: {counter}", x=50, y=30, size=24)
    easwin.soft.button(text="Click", x=50, y=100, size=16, height=3, width=7, fonc=increment)

def increment():
    global counter, lab
    counter += 1
    lab.config(text=f"Count: {counter}")

easwin.Window.soft(title="Counter", width=400, height=200, setup=setup, resizable=True)
```
