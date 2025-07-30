# mooch

[![PyPI](https://img.shields.io/pypi/v/mooch?label=mooch)](https://pypi.org/project/mooch/)
![Python Versions](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mooch)](https://pypistats.org/packages/mooch)
[![GitHub issues](https://img.shields.io/github/issues/nickstuer/mooch.svg)](https://github.com/nickstuer/mooch/issues)

![Lines Of Code](https://tokei.rs/b1/github/nickstuer/mooch)
[![Codecov](https://img.shields.io/codecov/c/github/nickstuer/mooch)](https://app.codecov.io/gh/nickstuer/mooch)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nickstuer/mooch/run_tests.yml)](https://github.com/nickstuer/mooch/actions/workflows/run_tests.yml)

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![license](https://img.shields.io/github/license/nickstuer/mooch.svg)](LICENSE)

mooch is a lightweight Python utility library designed to streamline common development tasks needed for every python project — file handling, path operations, logging decorators, and more — all in one convenient minimum package.

## Table of Contents

- [Features](https://github.com/nickstuer/mooch?tab=readme-ov-file#features)
- [Install](https://github.com/nickstuer/mooch?tab=readme-ov-file#install)
- [Usage](https://github.com/nickstuer/mooch?tab=readme-ov-file#usage)
- [Contributing](https://github.com/nickstuer/mooch?tab=readme-ov-file#contributing)
- [License](https://github.com/nickstuer/mooch?tab=readme-ov-file#license)

## Features

### Settings
 Seperate package named [zettings](https://pypi.org/project/zettings/)
 
 Lightweight, TOML-backed configuration/settings utility that that exposes project settings as standard Python dictionaries — allowing you to work with settings in a familiar, Pythonic way.

- TOML-powered: Uses TOML under the hood for modern, human-friendly settings files.
- Dictionary-like interface: Access and manipulate settings with regular dictionary operations.
- Nested access: Supports nested keys with dotted key notation.
- Optional `defaults`: Provide default values for initializing the settings file or for when a key is missing in the settings file.
- Optional `always_reload`: Reload the setting file everytime a key is read. (Enabled by default)

### Progress Bar
Seperate package named [BarNone](https://pypi.org/project/barnone/)

A lightweight, eye-friendly, and feature-rich terminal progress bar.

 - Clean, minimal visual output
 - Smooth gradient color transition (Red → Gold → Green)
 - ETA and step tracking
 - Fast render speed of ~200ns per iteration

### Location
Uses the https://api.zippopotam.us API to retrieve location information from a zip code or a city and state. U.S. only for now.
- Input options:
  - `zipcode` (int)
  - `city` (str)
  - `state` (star)
- Retrieves:
  - ZIP Code
  - City
  - State
  - Latitude & Longitude

### Validators
 - Raise a RuntimeError if the current python version is not compatible with your project.
 - Raise a RuntimeError if the current operating system is not compatible with your project.
 - Raise a RuntimeError if system commands like `git` are not in system's `PATH`
 - Raise a RuntimeError if a list of environmental variables are not set.

### Logging Decorators
**`@log_entry_exit`**
  - Logs the entry and exit of the function, including the arguments.
  - Useful for debugging and tracing.

### Function Decorators
**`@silent(fallback="fallback value")`**
  - Suppresses exceptions raised within the decorated function.
  - Returns `fallback` if an exception is caught.

**`@retry(3)`**
  - Retries the decorated function if an exception is raised.
  - Returns the last exception on final retry attempt. Optional `fallback` returned instead if desired.
  - Set delay time between tries with `delay` argument.

**`@deprecated`**
  - Emits a DeprecationWarning when the function is called.
  - Accepts a custom reason string to explain the deprecation.
  - Supports Python 3.9+ (`@deprecated` was added to Python 3.13)

**`@timeit`**
  - Logs execution time of a function using the Python `logging` module.

**`@with_lock(threading.Lock or asyncio.Lock)`**
 - Prevents concurrent execution using provided threading.Lock or asyncio.Lock
 - Lock object is created if not provided, but doing this only prevents concurrent execution of same function.

## Install

```
pip install mooch
```
or
```
uv add mooch
```

###  Dependencies
Python 3.9 or greater

## Usage

Browse the examples folder for more examples.

### Settings

```python
from zettings import Settings

defaults = {}
defaults["settings.mood"] = "happy"
defaults["settings.volume"] = 50

settings = Settings(".mooch/settings.toml", defaults)  # Change 'mooch' to your project's name

print("Current Settings:")
print(f"Mood: {settings['settings.mood']}")
print(f"Volume: {settings['settings.volume']}") # prints 50

settings["settings.volume"] = 75

print("Updated Settings:")
print(f"Mood: {settings['settings.mood']}")
print(f"Volume: {settings['settings.volume']}") # prints 75
```

### Progress Bar ###
```python
from barnone import ColoredProgressBar
pb = ColoredProgressBar(5)
#pb = ProgressBar(total=5)

for _ in range(5):
    time.sleep(0.1)
    pb.update()
```

Terminal Output:
![ColoredProgressBar Example](screenshots/ColoredProgressBar.png "ColoredProgressBar Example")

### Logging Decorator

```python
from mooch.decorators import log_entry_exit

@log_entry_exit
def random_function(arg1, arg2):
    print(arg1)
    print(arg2)
```
Log File Output:
```
DEBUG:__main__:Entering random_function() with args=('Hello', 'World'), kwargs={}
DEBUG:__main__:Exiting random_function()
```

### Retry Decorator

```python
from mooch.decorators import retry

@retry(3)
def get_age(name="random_person"):
    age = ...some other task...
    return age
```

### Location
```python
from mooch import Location
location = Location(zipcode=62704)

print(location.city)                # "Springfield"
print(location.state)               # "Illinois"
print(location.state_abbreviation)  # "IL"
print(location.latitude)            # "39.7725"
print(location.longitude)           # "-89.6889"
```

### Validators
Raise an RuntimeError if the requirement isn't satisified.
```python
from mooch.validators import command, operating_system, python_version

python_version.check("3.13")
operating_system.check("Windows")
command.check("python", "ls", "echo")
```

## Development
Steps for setting up this project for development in VS Code.

<details><summary><b>Show Instructions</b></summary>

1. Clone the Repository
```bash
git clone https://github.com/nickstuer/mooch
```

2. Install [`uv`](https://github.com/astral-sh/uv) (skip if already installed)
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

3. Install Project Dependencies
```bash
uv sync
```

4. Activate Virtual Environment
```bash
source .venv/bin/activate  # On Windows: .venv/Scripts/activate
```

5. Install pre-commit hooks
```bash
pre-commit install

# Verify
pre-commit run --all-files
```

6. Setup Python Interpreter in VS Code
```
Press CMD + Shift + P   # On Windows: CTRL + Shift + P
Select `Python: Select Interpreter'
Choose `.\.venv\Scripts\python.exe`
```
</details>

## Contributing

PRs accepted.

If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

#### Bug Reports and Feature Requests
Please use the [issue tracker](https://github.com/nickstuer/mooch/issues) to report any bugs or request new features.

#### Contributors

<a href = "https://github.com/nickstuer/mooch/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=nickstuer/mooch"/>
</a>

## License

[MIT © Nick Stuer](LICENSE)
