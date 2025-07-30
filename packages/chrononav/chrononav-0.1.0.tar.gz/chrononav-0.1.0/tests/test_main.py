from typer.testing import CliRunner
from chrononav.main import app

# CliRunner is Typer's way to test command-line applications
runner = CliRunner()


def test_default_view():
    """Tests if the default command runs successfully."""
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Live World Clocks" in result.stdout
    assert "London" in result.stdout
    assert "Tokyo" in result.stdout


def test_default_view_am_pm():
    """Tests the --am-pm flag on the default view."""
    result = runner.invoke(app, ["--am-pm"])
    assert result.exit_code == 0
    # Check for AM or PM in the output, which indicates 12-hour format
    assert "AM" in result.stdout or "PM" in result.stdout


def test_now_command():
    """Tests the 'now' command with specific cities."""
    result = runner.invoke(app, ["now", "paris", "chicago"])
    assert result.exit_code == 0
    assert "Europe/Paris" in result.stdout
    assert "America/Chicago" in result.stdout


def test_now_command_invalid_timezone():
    """Tests that 'now' handles an invalid timezone gracefully."""
    result = runner.invoke(app, ["now", "faketown"])
    assert result.exit_code == 0  # It should not crash
    assert "Error: Unknown timezone 'faketown'" in result.stdout


def test_convert_command_basic():
    """Tests a basic conversion."""
    result = runner.invoke(
        app, ["convert", "10:30am", "--from", "new_york", "--to", "berlin"]
    )
    assert result.exit_code == 0
    assert "Europe/Berlin" in result.stdout


def test_convert_command_am_pm():
    """Tests a conversion with the --am-pm flag."""
    result = runner.invoke(
        app, ["convert", "8:00pm", "--from", "dubai", "--to", "sydney", "--am-pm"]
    )
    assert result.exit_code == 0
    assert "Australia/Sydney" in result.stdout
    assert "AM" in result.stdout or "PM" in result.stdout


def test_convert_command_date_change():
    """Tests a conversion that crosses the international date line."""
    # A time in LA on Dec 31st should be Jan 1st in Sydney
    source_date = "2025-12-31"
    next_date = "2026-01-01"

    result = runner.invoke(
        app, ["convert", f"{source_date} 10:00pm", "--from", "la", "--to", "sydney"]
    )
    assert result.exit_code == 0
    assert next_date in result.stdout


def test_convert_command_invalid_time():
    """Tests that 'convert' fails with a bad time string."""
    result = runner.invoke(
        app, ["convert", "not a real time", "--from", "london", "--to", "paris"]
    )
    # Should exit with a non-zero code to indicate an error
    assert result.exit_code == 1
    assert "Error processing source time/zone" in result.stdout


def test_help_menus():
    """Ensures help menus are accessible."""
    result_main = runner.invoke(app, ["--help"])
    assert result_main.exit_code == 0
    assert "Usage: chrononav [OPTIONS] COMMAND [ARGS]..." in result_main.stdout

    result_convert = runner.invoke(app, ["convert", "--help"])
    assert result_convert.exit_code == 0
    assert "Converts a SPECIFIC time" in result_convert.stdout
    assert "--am-pm" in result_convert.stdout  # Crucially, the option is documented
