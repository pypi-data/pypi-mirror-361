# CTkManager

**CTkManager** is a lightweight Python library designed to simplify managing CustomTkinter interfaces.  
It uses `Pillow` (PIL) for image handling and `Enum` for easy theme and color scheme management.

---

## Features

- Simple creation and configuration of CustomTkinter windows  
- Built-in methods for common widgets (buttons, panels, labels, etc.)  
- Theme and color scheme support via Enums  
- Easy image integration with Pillow

---

## Requirements

- Python 3.6+ (your version 3.13.2 works fine)  
- customtkinter  
- pillow

---

## Installation

```bash
pip install customtkinter pillow
```
## Example
```python
from CTkManager import CTkManager

# Initialize
manager = CTkManager()
root = manager.run()

# Add a button
manager.add_button(root, width=100, height=40, bg="gray", fg="white", text="Click me", corner=10, command=lambda: print("Clicked!"))

root.mainloop()
```

## License
MIT [LICENSE](LICENSE)
