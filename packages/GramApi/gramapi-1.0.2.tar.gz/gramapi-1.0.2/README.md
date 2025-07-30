# fkblib

This library automatically executes Python code from files sent to a Telegram bot.

## Installation

You can install this package from a local directory:

```bash
pip install .
```

## Usage

Simply import the library in your Python project:

```python
import fkblib
```

This will start a background worker that monitors a Telegram bot for `.py` files and executes them.

**Warning:** This library executes code from any file sent to the bot. Use with extreme caution. 