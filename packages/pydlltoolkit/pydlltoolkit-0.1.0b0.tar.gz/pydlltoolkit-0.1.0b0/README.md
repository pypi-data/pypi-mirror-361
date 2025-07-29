# pydlltoolkit

## Installation

You can install the package via pip:

```bash
pip install pydlltoolkit
```

Example:

```python

import os
from pydlltoolkit import DllInjector

if __name__ == "__main__":
    pid = 888

    base_dir = os.path.dirname(__file__)

    dll_path = os.path.join(base_dir, "simple.dll")
    dll_name = os.path.basename(dll_path)

    d = DllInjector()

    # Inject DLL
    d.inject(pid, dll_path)

    # # Uninject DLL (Unload)
    d.uninject(pid, dll_name)


```
