# ChronoNav

> A sleek and powerful CLI for navigating timezones with ease, right from your terminal.

ChronoNav is a command-line tool that makes dealing with timezones simple and intuitive. Whether you need a quick glance at world clocks, want to know the current time for a colleague overseas, or need to schedule a meeting across multiple timezones, ChronoNav has you covered.

![Demo Screenshot](https://raw.githubusercontent.com/vivek378521/chrononav/refs/heads/main/assets/demo.png)

## Key Features

- **Live World Clocks:** Run `chrononav` with no arguments for a beautiful dashboard of current times in major world cities.
- **Specific Time Conversion:** Convert any time from a source timezone to multiple destination timezones.
- **"Now" Command:** Instantly check the current time in any list of cities or timezones.
- **12/24 Hour Format:** Use the `--am-pm` flag to toggle between 12-hour and 24-hour clock formats.
- **Smart Aliases:** Use common city names and aliases (like `nyc`, `la`, `kolkata`) instead of formal timezone identifiers.
- **Polished Interface:** Features ASCII art and rich, colorful tables for excellent readability.

## Installation

The recommended way to install ChronoNav is using `pipx`, which installs Python CLI tools in isolated environments, preventing dependency conflicts.

### Recommended Method: `pipx`

1.  **First, install pipx (you only need to do this once):**
    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```
    *(You may need to restart your terminal after this step for the `PATH` change to take effect.)*

2.  **Install ChronoNav:**
    ```bash
    pipx install chrononav
    ```

### Alternative Method: `pip`

If you prefer, you can install with `pip`. The `--user` flag is crucial to avoid modifying system packages.

1.  **Install ChronoNav for your user:**
    ```bash
    python3 -m pip install --user chrononav
    ```

2.  **Verify your PATH (Important!):** This method may install the `chrononav` command to a directory not in your shell's `PATH`. If you get a "command not found" error, you must add it. Open your `~/.bashrc`, `~/.zshrc`, or equivalent shell configuration file and add one of the following lines:
    ```bash
    # For Linux:
    export PATH="$HOME/.local/bin:$PATH"

    # For macOS (path may vary depending on Python version):
    export PATH="$HOME/Library/Python/3.9/bin:$PATH"
    ```
    Restart your terminal for the change to take effect.

## Usage Examples

### 1. Default View (Live World Clocks)
Simply run the command by itself. Use `--am-pm` for 12-hour format.

```bash
chrononav --am-pm
```