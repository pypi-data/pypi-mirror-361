# Logita

**Logita** is a lightweight and customizable Python logging utility designed to enhance console and file-based logging with optional colorized output.

## Features

- Print log messages with timestamps to the console.
- Support for multiple log levels: `info`, `success`, `error`, `warning`, `debug`, `critical`, and `exception`.
- Optional color-coded output using `colorama`.
- Optional file logging with configurable filename and format.
- Dynamic log level control.

## Installation

```bash
pip install logita
```

Make sure you have `colorama` installed:

```bash
pip install colorama
```

## Usage

```python
from logita import Logita

log = Logita(log_to_file=True, log_filename="myapp.log", print_to_console=True, use_colors=True)

log.info("This is an info message")
log.success("This indicates success")
log.warning("This is a warning")
log.error("This is an error")
log.debug("Debugging details")
log.critical("Critical issue")
log.exception("Exception occurred")
```

## Constructor Parameters

- `log_to_file` (bool): Save logs to file (default `False`).
- `log_filename` (str): Filename for log output (default `"app.log"`).
- `print_to_console` (bool): Print logs to the console (default `True`).
- `use_colors` (bool): Use colorized output (default `True`).

## License

MIT License
