import typer
from rich.console import Console
from rich.table import Table
import pyfiglet
from datetime import datetime
import pytz
from typing_extensions import Annotated
from typing import List
from dateutil.parser import parse, ParserError

# --- Reusable Annotated Type for the --am-pm option ---
# This avoids repeating the long definition and ensures consistency.
AmPmOption = Annotated[
    bool, typer.Option("--am-pm", help="Display time in 12-hour AM/PM format.")
]

# Initialize Typer app
app = typer.Typer(
    name="chrononav",
    add_completion=False,
    rich_markup_mode="rich",
    help="A cool CLI to navigate through timezones.",
)

console = Console()

# --- Data and Helper Functions (No Changes Here) ---
CITY_TIMEZONES = {
    "utc": "UTC",
    "gmt": "GMT",
    "new_york": "America/New_York",
    "nyc": "America/New_York",
    "london": "Europe/London",
    "ist": "Europe/Dublin",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "dubai": "Asia/Dubai",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "los_angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "moscow": "Europe/Moscow",
    "cairo": "Africa/Cairo",
    "kolkata": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
}
POPULAR_CITIES = ["new_york", "london", "tokyo", "dubai", "sydney", "kolkata"]


def resolve_timezone_str(tz_or_city: str) -> str:
    key = tz_or_city.lower().replace(" ", "_")
    return CITY_TIMEZONES.get(key, tz_or_city)


def format_time(dt_object, use_am_pm: bool) -> str:
    if use_am_pm:
        return dt_object.strftime("%I:%M:%S %p")
    else:
        return dt_object.strftime("%H:%M:%S")


def create_time_table(title: str) -> Table:
    table = Table(
        title=title,
        title_style="bold cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Timezone", style="white")
    table.add_column("Time", justify="center", style="green")
    table.add_column("Date", justify="center", style="yellow")
    return table


# --- CLI Commands (Updated and Corrected) ---


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    am_pm: AmPmOption = False,  # Add the option here for the default command
):
    """
    ChronoNav: A CLI for easy timezone conversions.
    By default, shows current time in popular world cities.
    """
    # This block runs only if no subcommand (like 'now' or 'convert') is invoked.
    if ctx.invoked_subcommand is None:
        banner = pyfiglet.figlet_format("ChronoNav", font="starwars")
        console.print(f"[bold yellow]{banner}[/bold yellow]")

        table = create_time_table("Live World Clocks")
        now_utc = datetime.now(pytz.utc)

        # We use the 'am_pm' parameter directly from this function's signature
        table.add_row(
            "UTC", "Etc/UTC", format_time(now_utc, am_pm), now_utc.strftime("%Y-%m-%d")
        )
        table.add_section()

        for city in POPULAR_CITIES:
            tz_str = resolve_timezone_str(city)
            try:
                dt_object = now_utc.astimezone(pytz.timezone(tz_str))
                table.add_row(
                    city.replace("_", " ").title(),
                    tz_str,
                    format_time(dt_object, am_pm),
                    dt_object.strftime("%Y-%m-%d"),
                )
            except pytz.UnknownTimeZoneError:
                console.print(
                    f"[bold red]Error: Default city timezone '{tz_str}' is invalid.[/bold red]"
                )

        console.print(table)


@app.command()
def now(
    zones: Annotated[
        List[str], typer.Argument(help="List of cities (e.g., 'london') or timezones.")
    ],
    am_pm: AmPmOption = False,  # The option is now specific and local to this command
):
    """
    Shows the CURRENT time in one or more specified timezones or cities.
    """
    table = create_time_table("Current Time")
    now_utc = datetime.now(pytz.utc)
    for zone_input in zones:
        tz_str = resolve_timezone_str(zone_input)
        try:
            dt_object = now_utc.astimezone(pytz.timezone(tz_str))
            table.add_row(
                zone_input.title(),
                tz_str,
                format_time(dt_object, am_pm),
                dt_object.strftime("%Y-%m-%d"),
            )
        except pytz.UnknownTimeZoneError:
            console.print(f"[bold red]Error: Unknown timezone '{tz_str}'.[/bold red]")
            continue
    console.print(table)


@app.command()
def convert(
    time_str: Annotated[
        str,
        typer.Argument(
            help="The time to convert (e.g., '10:30pm', '2025-01-01 14:00')."
        ),
    ],
    frm: Annotated[
        str,
        typer.Option(
            "--from", help="The source timezone or city of the provided time."
        ),
    ],
    to: Annotated[
        List[str], typer.Option("--to", help="Target timezone(s) or city/cities.")
    ],
    am_pm: AmPmOption = False,  # The option is also specific and local to this command
):
    """
    Converts a SPECIFIC time from a source timezone to target timezones.
    """
    from_tz_str = resolve_timezone_str(frm)
    try:
        parsed_time = parse(time_str)
        source_tz_obj = pytz.timezone(from_tz_str)
        if parsed_time.tzinfo is None:
            source_dt = source_tz_obj.localize(parsed_time)
        else:
            source_dt = parsed_time.astimezone(source_tz_obj)
    except (ParserError, pytz.UnknownTimeZoneError, ValueError) as e:
        console.print(f"[bold red]Error processing source time/zone: {e}[/bold red]")
        raise typer.Exit(1)

    table_title = f"Conversion from [bold magenta]{source_dt.strftime('%H:%M')} on {source_dt.strftime('%Y-%m-%d')} in {frm}[/bold magenta]"
    table = create_time_table(table_title)

    for target_input in to:
        target_tz_str = resolve_timezone_str(target_input)
        try:
            target_tz_obj = pytz.timezone(target_tz_str)
            target_dt = source_dt.astimezone(target_tz_obj)
            table.add_row(
                target_input.title(),
                target_tz_str,
                format_time(target_dt, am_pm),
                target_dt.strftime("%Y-%m-%d"),
            )
        except pytz.UnknownTimeZoneError:
            console.print(
                f"[bold red]Error: Unknown target timezone '{target_input}'.[/bold red]"
            )
    console.print(table)


if __name__ == "__main__":
    app()
