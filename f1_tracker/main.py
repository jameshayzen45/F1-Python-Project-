"""
F1 Live Timings Tracker - Main Application
==========================================
Interactive command-line application for viewing F1 timing data.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import matplotlib.pyplot as plt

from .data import F1DataLoader, CALENDAR_2024
from .teams import TEAMS_2024, get_all_drivers
from .timing_board import TimingBoard, display_race_summary
from .telemetry import TelemetryVisualizer, create_telemetry_dashboard
from .track_map import TrackMapVisualizer, create_track_visualization


console = Console()


def print_banner():
    """Print the application banner."""
    banner = """
    ███████╗ ██╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
    ██╔════╝███║    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    █████╗  ╚██║       ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
    ██╔══╝   ██║       ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║      ██║       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝      ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    console.print(Panel(banner, style="bold red", subtitle="Mercedes HPP Practice Project"))


def show_calendar():
    """Display the F1 calendar."""
    table = Table(title="2024 F1 Calendar", header_style="bold white", border_style="red")
    table.add_column("Round", justify="center", width=6)
    table.add_column("Grand Prix", justify="left", width=30)
    table.add_column("Circuit", justify="left", width=40)
    table.add_column("Country", justify="left", width=15)

    for round_num, info in CALENDAR_2024.items():
        table.add_row(
            str(round_num),
            info['name'],
            info['circuit'],
            info['country']
        )

    console.print(table)


def show_teams():
    """Display all teams and drivers."""
    console.print("\n[bold white]2024 F1 Teams & Drivers[/]\n")

    for team_key, team in TEAMS_2024.items():
        console.print(Panel(
            f"[bold white]{team.full_name}[/]\n\n" +
            "\n".join([
                f"  #{d.number} {d.name} ({d.abbreviation}) - {d.nationality}"
                for d in team.drivers
            ]),
            title=f"[{team.primary_color}]{team.name}[/]",
            border_style=team.primary_color
        ))


def select_session(loader: F1DataLoader):
    """Interactive session selection."""
    console.print("\n[bold]Select a session to load:[/]\n")

    # Show calendar first
    show_calendar()

    # Get race selection
    race_num = IntPrompt.ask(
        "\nEnter round number (1-24)",
        default=1
    )

    if race_num not in CALENDAR_2024:
        console.print("[red]Invalid round number![/]")
        return None

    console.print(f"\n[green]Selected: {CALENDAR_2024[race_num]['name']}[/]")

    # Session type selection
    session_types = {
        "1": ("FP1", "Free Practice 1"),
        "2": ("FP2", "Free Practice 2"),
        "3": ("FP3", "Free Practice 3"),
        "4": ("Q", "Qualifying"),
        "5": ("S", "Sprint"),
        "6": ("R", "Race"),
    }

    console.print("\n[bold]Session types:[/]")
    for key, (_, name) in session_types.items():
        console.print(f"  {key}. {name}")

    session_choice = Prompt.ask("Select session type", default="6")
    session_type = session_types.get(session_choice, ("R", "Race"))[0]

    # Load the session with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task(
            f"Loading {CALENDAR_2024[race_num]['name']} - {session_type}...",
            total=None
        )
        try:
            session = loader.load_session(2024, race_num, session_type)
            console.print(f"[green]Session loaded successfully![/]")
            return session
        except Exception as e:
            console.print(f"[red]Error loading session: {e}[/]")
            return None


def timing_menu(session):
    """Timing data submenu."""
    board = TimingBoard(session)

    while True:
        console.print("\n[bold]Timing Data Options:[/]")
        console.print("  1. Show Race Results / Timing Tower")
        console.print("  2. Show Fastest Laps")
        console.print("  3. Driver Card")
        console.print("  4. Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")

        if choice == "1":
            board.print_timing_tower()
        elif choice == "2":
            board.print_fastest_laps()
        elif choice == "3":
            drivers = [d.abbreviation for d in get_all_drivers()]
            console.print(f"Available drivers: {', '.join(drivers)}")
            driver = Prompt.ask("Enter driver code", default="VER").upper()
            console.print(board.create_driver_card(driver))
        elif choice == "4":
            break


def telemetry_menu(session):
    """Telemetry visualization submenu."""
    viz = TelemetryVisualizer(session)

    while True:
        console.print("\n[bold]Telemetry Options:[/]")
        console.print("  1. Full Telemetry Dashboard (Speed, Throttle, Brake, Gear)")
        console.print("  2. Speed Comparison (2 drivers)")
        console.print("  3. Speed Delta Analysis")
        console.print("  4. Mini-Sector Analysis")
        console.print("  5. Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")

        if choice == "1":
            driver = Prompt.ask("Enter driver code", default="VER").upper()
            console.print(f"[dim]Generating telemetry for {driver}...[/]")
            fig, _ = viz.plot_full_telemetry(driver)
            plt.show()

        elif choice == "2":
            driver1 = Prompt.ask("Enter first driver code", default="VER").upper()
            driver2 = Prompt.ask("Enter second driver code", default="HAM").upper()
            console.print(f"[dim]Comparing {driver1} vs {driver2}...[/]")

            fig, ax = plt.subplots(figsize=(16, 8))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')
            viz.plot_comparison([driver1, driver2], metric='Speed', ax=ax)
            plt.tight_layout()
            plt.show()

        elif choice == "3":
            driver1 = Prompt.ask("Enter first driver code", default="VER").upper()
            driver2 = Prompt.ask("Enter second driver code", default="HAM").upper()
            console.print(f"[dim]Analyzing speed delta...[/]")
            fig, ax = plt.subplots(figsize=(16, 6))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')
            viz.plot_speed_delta(driver1, driver2, ax=ax)
            plt.tight_layout()
            plt.show()

        elif choice == "4":
            driver = Prompt.ask("Enter driver code", default="VER").upper()
            fig, ax = plt.subplots(figsize=(16, 6))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')
            viz.plot_mini_sectors(driver, ax=ax)
            plt.tight_layout()
            plt.show()

        elif choice == "5":
            break


def track_menu(session):
    """Track visualization submenu."""
    viz = TrackMapVisualizer(session)

    while True:
        console.print("\n[bold]Track Map Options:[/]")
        console.print("  1. Circuit Overview with Driver Lap (Speed colored)")
        console.print("  2. Racing Line Comparison (multiple drivers)")
        console.print("  3. Car Positions at Distance")
        console.print("  4. Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")

        if choice == "1":
            driver = Prompt.ask("Enter driver code", default="VER").upper()
            console.print(f"[dim]Creating track visualization for {driver}...[/]")
            fig, _ = create_track_visualization(session, driver)
            plt.show()

        elif choice == "2":
            drivers_input = Prompt.ask(
                "Enter driver codes (comma-separated)",
                default="VER,HAM,LEC"
            )
            drivers = [d.strip().upper() for d in drivers_input.split(',')]
            console.print(f"[dim]Comparing racing lines: {', '.join(drivers)}...[/]")

            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')
            viz.plot_comparison(drivers, ax=ax)
            plt.tight_layout()
            plt.show()

        elif choice == "3":
            lap = IntPrompt.ask("Enter lap number", default=1)
            distance = IntPrompt.ask("Enter distance from start (meters)", default=1000)
            console.print(f"[dim]Plotting car positions at lap {lap}, {distance}m...[/]")

            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')
            viz.plot_positions_at_distance(lap, distance, ax=ax)
            plt.tight_layout()
            plt.show()

        elif choice == "4":
            break


def main():
    """Main application entry point."""
    print_banner()

    loader = F1DataLoader()
    current_session = None

    while True:
        console.print("\n[bold red]═══ MAIN MENU ═══[/]\n")

        if current_session:
            console.print(
                f"[green]Loaded: {current_session.event['EventName']} - {current_session.name}[/]\n"
            )

        console.print("  1. Load Session")
        console.print("  2. View Calendar")
        console.print("  3. View Teams & Drivers")

        if current_session:
            console.print("  4. [cyan]Timing Data[/]")
            console.print("  5. [cyan]Telemetry Visualization[/]")
            console.print("  6. [cyan]Track Map[/]")
            console.print("  7. [cyan]Full Race Summary[/]")

        console.print("  0. Exit")

        choice = Prompt.ask("\nSelect option", default="1")

        if choice == "1":
            current_session = select_session(loader)
        elif choice == "2":
            show_calendar()
        elif choice == "3":
            show_teams()
        elif choice == "4" and current_session:
            timing_menu(current_session)
        elif choice == "5" and current_session:
            telemetry_menu(current_session)
        elif choice == "6" and current_session:
            track_menu(current_session)
        elif choice == "7" and current_session:
            display_race_summary(current_session)
        elif choice == "0":
            console.print("\n[bold red]Thanks for using F1 Tracker! Good luck with Mercedes HPP![/]\n")
            break
        else:
            console.print("[yellow]Invalid option or no session loaded[/]")


if __name__ == "__main__":
    main()
