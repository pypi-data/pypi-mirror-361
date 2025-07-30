# twlog

A lightweight and colorful logging utility for Python, designed to enhance your console output for debugging and general information. `twlog` provides an intuitive interface similar to Python's standard `logging` module, with a focus on immediate, human-readable, and visually engaging console messages.

---

## Features

* **Direct to Standard Output**: Unlike Python's standard `logging` module, `twlog` defaults to `sys.stdout` for all messages, making console log management straightforward and compatible with typical shell redirection.
* **Automatic Array Disassembly**: Seamlessly handles and converts numerical array objects (like NumPy `ndarray`, PyTorch `Tensor`, JAX `Array`, etc.) into readable string representations for clearer debugging in data science and machine learning workflows.
* **Built-in ANSI Color Support**: Achieve rich, colorful, and styled console output without needing external libraries like `Rich`. `twlog` leverages direct ANSI escape codes for enhanced readability.
* **Fun Print Functions**: A collection of unique, emoji-enhanced, and color-coded print-like functions (`pixie`, `prain`, `prank`, and more) to make your debugging experience more interactive and enjoyable.

---

## Installation

You can install `twlog` directly from PyPI:

```bash
pip install twlog
````

-----

## Quick Start

Get started with `twlog` in just a few lines of code:

```python
import twlog
import numpy as np # Example for array disassembly

# Get a logger instance
logger = twlog.getLogger("MyApplication")

# Output a simple info message
logger.info("Application started successfully!")

# Output a debug message with a custom title
logger.debug("Debug mode is ON", title="Configuration")

# Demonstrate array disassembly
my_array = np.array([[1.23, 4.56], [7.89, 0.12]])
logger.info(my_array, title="Metrics")

# Use a fun print function
twlog.pixie("Status", "Data processing complete!")
```

-----

## Basic Usage

### Obtaining a Logger

Use `twlog.getLogger()` to obtain a `Logger` instance. If no name is provided, the root logger is returned.

```python
import twlog

# Get the root logger
root_logger = twlog.getLogger()
root_logger.info("This is a message from the root logger.")

# Get a named logger
my_specific_logger = twlog.getLogger("DataProcessor")
my_specific_logger.debug("Starting data ingestion...", level=twlog.DEBUG) # Using imported level constant
```

### Setting Log Levels

You can set the minimum log level for your logger using `setLevel()`. `twlog` follows standard logging levels. The level constants (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) are directly importable from the `twlog` package.

```python
import twlog

logger = twlog.getLogger("MyLogger")
logger.setLevel(twlog.DEBUG)
logger.debug("This debug message will now appear.")
logger.info("This info message will also appear.")

logger.setLevel(twlog.INFO)
logger.debug("This debug message will NOT appear now.")
logger.info("This info message WILL appear.")
```

### Logging Messages

The primary logging method is `logger.logging()`, but `twlog` also provides convenience methods like `info()`, `debug()`, `warning()`, `error()`, and `critical()` which automatically set the `level` argument.

```python
logger = twlog.getLogger("ExampleLogger")

logger.info("A standard information message.")
logger.warning("This is a warning about something.")
logger.error("An error occurred during file operation.")

# Logging with a custom title
# The title will default to the uppercase version of the logger's name if not provided.
logger.info("User 'admin' logged in.", title="Security")
logger.debug("Variable X: 123", title="Debugger")
logger.info("This message's title will be 'EXAMPLELOGGER'.") # Example without title argument
```

### Handling Numerical Arrays

`twlog` automatically converts common numerical array types (`numpy.ndarray`, `torch.Tensor`, etc.) into readable Python list or scalar strings.

```python
import twlog
import numpy as np
# import torch # Uncomment if you use PyTorch

logger = twlog.getLogger("ArrayLogger")

# NumPy array example
numpy_array = np.array([[1.0, 2.0], [3.0, 4.0]])
logger.info(numpy_array, title="Numpy Data")

# Single element array (converts to scalar)
single_element_array = np.array([5.0])
logger.info(single_element_array, title="Single Element")

# PyTorch Tensor example (if torch is installed)
# pytorch_tensor = torch.tensor([[10, 20], [30, 40]])
# logger.info(pytorch_tensor, title="PyTorch Data")
```

### Using Fun Print Functions (Top-Level)

`twlog` provides a set of highly visual, emoji-enhanced functions directly accessible from the `twlog` package. These are ideal for making specific debug messages or status updates stand out in your console.

```python
import twlog

# Prints options as key-value pairs
twlog.popts("Settings", "verbose=True", "cache_enabled=False")

# Prints a message without a newline (useful for progress bars)
import time
twlog.psolo("Progress: ")
for i in range(5):
    twlog.psolo(f"{i*20}% ")
    time.sleep(0.1)
twlog.psolo("\n") # Add a newline at the end

# Free-style message with a star emoji and blue bold title
twlog.priny("System Boot", "Checking dependencies", "Loading modules")

# Magic-like message with fairy emojis, cyan color, and blinking effect
twlog.pixie("Success!", "Model training complete!", "Accuracy: 99.1%")

# Rainbow-themed message with a rainbow emoji and yellow bold title
twlog.prain("Result", "Training Loss: 0.005", "Validation Loss: 0.007")

# Message with paint brush emojis and magenta bold title for colorful output
twlog.paint("Color Palette", "Primary: Red", "Secondary: Green", "Tertiary: Blue")

# Light, flowing message with wind emojis and white bold title
twlog.plume("Stream", "Reading data stream from sensor.", "Filtering noise...")

# Playful message with clown emojis, green and red bold text (great for playful debugging)
twlog.prank("Heads Up!", "This feature is still experimental.", "Use with caution!")

# Message with shrimp emoji and red bold title
twlog.prown("Fatal Error", "Database connection lost!", "Please restart the server.")

# Multi-line, structured message with a disco ball emoji (ideal for summaries)
twlog.prism("Summary Report", "Total Users: 5000", "New Signups: 150", "Active Sessions: 1200")
```

-----

## Command Line Usage

`twlog` includes a simple command-line interface for testing its console output capabilities.

To run the test, simply execute:

```bash
python -m twlog
```

![sample](https://raw.githubusercontent.com/ScrapWareOrg/twlog/refs/heads/main/sample1.png)

This will output a series of test messages demonstrating various logging levels and fun print functions.

-----

## Why `twlog` instead of standard `logging`?

Python's built-in `logging` module is powerful and highly configurable, but it often defaults to `sys.stderr` for console output, which can be less convenient for general application logs that are not strictly error-related. `twlog` addresses this by:

  * **Defaulting to `sys.stdout`**: This aligns with the common practice of sending general application output to standard output, making it easier to pipe logs to other tools, redirect to files, or display directly in the console without mixing with separate error streams.
  * **Simplifying Console Output**: For many scripts and applications, the full complexity of the standard `logging` module (multiple handlers, formatters, filters, etc.) can be an overkill. `twlog` streamlines the process, focusing on clear, immediate, and visually appealing console output.
  * **Enhancing Debugging Experience**: The automatic handling of numerical array types eliminates the need for manual `str()` or `.tolist()` conversions, providing cleaner debug logs for scientific computing. The unique **ANSI color support without `Rich` dependency** and the collection of **emoji-enhanced "fun print" functions** further make `twlog` a delightful tool for development and debugging, adding a layer of personality and clarity to your console.

-----

## API Reference

### `twlog.getLogger(name: str = None) -> Logger`

Returns a `Logger` instance.

  * `name` (str, optional): The name of the logger. If `None`, the root logger is returned.

### `Logger` Class

The `Logger` class provides methods for logging messages at different severity levels and controlling their presentation.

#### `Logger.logging(message: Any, level: int = 20, title: str = None, datefmt: str = None, msgfmt: str = None)`

The core method for emitting a log message.

  * `message` (Any): The message to be logged. It can be a string, a number, or a numerical array-like object (e.g., `numpy.ndarray`, `torch.Tensor`), which will be automatically converted to a string.
  * `level` (int, optional): The severity level of the message.
      * `twlog.DEBUG` (10): Detailed information, typically of interest only when diagnosing problems.
      * `twlog.INFO` (20): Confirmation that things are working as expected. (Default)
      * `twlog.WARNING` (30): An indication that something unexpected happened, or indicative of some problem in the near future (e.g. 'disk space low'). The software is still working as expected.
      * `twlog.ERROR` (40): Due to a more serious problem, the software has not been able to perform some function.
      * `twlog.CRITICAL` (50): A serious error, indicating that the program itself may be unable to continue running.
  * `title` (str, optional): A custom title displayed before the message. If `None`, the logger's name (in uppercase) is used as the default.
  * `datefmt` (str, optional): A format string for the timestamp (e.g., `"%Y-%m-%d %H:%M:%S"`). If `None`, a default format is used.
  * `msgfmt` (str, optional): A format string for the entire log message (e.g., `"{date} [{level}] {title}: {message}"`). If `None`, a default format is used.

#### Convenience Methods (e.g., `Logger.info()`, `Logger.debug()`)

These methods are shortcuts for `logging()` with the `level` argument pre-set.

  * `Logger.debug(message: Any, title: str = None, datefmt: str = None, msgfmt: str = None)`
  * `Logger.info(message: Any, title: str = None, datefmt: str = None, msgfmt: str = None)`
  * `Logger.warning(message: Any, title: str = None, datefmt: str = None, msgfmt: str = None)`
  * `Logger.error(message: Any, title: str = None, datefmt: str = None, msgfmt: str = None)`
  * `Logger.critical(message: Any, title: str = None, datefmt: str = None, msgfmt: str = None)`

#### `Logger.setLevel(level: int)`

Sets the threshold for the logger. Messages with a level lower than this will be ignored.

  * `level` (int): The minimum severity level to log.

### Fun Print Functions (Top-Level)

These functions are designed for visually distinct console output, leveraging ANSI escape codes and emojis for enhanced readability and fun during development/debugging. They are directly importable from the `twlog` package.

  * `popts(b: Any, *t: Any)`

      * **Description**: Prints options as key-value pairs, with a bold key.
      * **Usage**: `popts("Options", "verbose=True", "debug_mode=False")`

  * `psolo(m: Any)`

      * **Description**: Prints a single value without including a line break at the end. Useful for building progress indicators on a single line.
      * **Usage**: `psolo("Progress: "); for i in range(5): psolo(f"{i*20}% "); time.sleep(0.1)`

  * `priny(b: Any, *t: Any)`

      * **Description**: Prints a free-style message with a leading star emoji (`🌠`), blue bold title, and a customizable structure.
      * **Usage**: `priny("System Boot", "Checking dependencies", "Loading modules")`

  * `pixie(b: Any, *t: Any)`

      * **Description**: Prints a magic-like message with fairy emojis (`🧚✨✨✨`), cyan color, and a blinking effect. Ideal for highlighting magical or important events.
      * **Usage**: `pixie("Success!", "Model training complete!", "Accuracy: 99.1%")`

  * `prain(b: Any, *t: Any)`

      * **Description**: Prints a rainbow-themed message with a rainbow emoji (`🌈`) and yellow bold title.
      * **Usage**: `prain("Result", "Training Loss: 0.005", "Validation Loss: 0.007")`

  * `paint(b: Any, *t: Any)`

      * **Description**: Prints a message with paint brush emojis (`🎨🖌️`) and magenta bold title, for colorful output. Uses a brush stroke (`🖌️`) as a separator between `*t` arguments.
      * **Usage**: `paint("Color Palette", "Primary: Red", "Secondary: Green", "Tertiary: Blue")`

  * `plume(b: Any, *t: Any)`

      * **Description**: Prints a light, flowing message with wind emojis (`🌬️`) and white bold title. The body text is italic and cyan.
      * **Usage**: `plume("Stream", "Reading data stream from sensor.", "Filtering noise...")`

  * `prank(b: Any, *t: Any)`

      * **Description**: Prints a playful message with clown emojis (`🤡`), green and red bold text. Useful for lighthearted debugging or temporary messages.
      * **Usage**: `prank("Heads Up!", "This feature is still experimental.", "Use with caution!")`

  * `prown(b: Any, *t: Any)`

      * **Description**: Prints a message with a shrimp emoji (`🍤`) and red bold title.
      * **Usage**: `prown("Fatal Error", "Database connection lost!", "Please restart the server.")`

  * `prism(b: Any, *t: Any)`

      * **Description**: Prints a multi-line, structured message with a disco ball emoji (`🪩`) and cyan bold title. Ideal for displaying summaries or structured data that benefits from line breaks. Each `*t` argument appears on a new line, indented.
      * **Usage**: `prism("Summary Report", "Total Users: 5000", "New Signups: 150", "Active Sessions: 1200")`

    *Note: All `b` and `t` arguments are automatically converted to strings internally before being printed.*

-----

## Contributing

We welcome contributions to `twlog`\! If you find a bug, have a feature request, or would like to contribute code, please check out our GitHub repository and open an issue or pull request.

-----

## License

`twlog` is licensed under the GPLv3 AND LicenseRef-RPTv1.
