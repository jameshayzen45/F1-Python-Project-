"""
Live Timing Board Display
=========================
Creates a rich terminal display mimicking F1 TV timing graphics.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.style import Style
from typing import Optional, List, Dict
import fastf1
import pandas as pd

from .teams import get_driver_color, get_team_by_driver, TEAMS_2024


console = Console()


class TimingBoard:
    """Creates F1-style timing board displays."""

    def __init__(self, session: fastf1.core.Session):
        self.session = session
        self.laps = session.laps
        self.results = session.results

    def create_timing_table(
        self,
        lap_number: Optional[int] = None,
        show_gaps: bool = True,
        show_sectors: bool = True
    ) -> Table:
        """
        Create a timing tower table similar to F1 TV graphics.

        Args:
            lap_number: Show standings at specific lap (latest if not provided)
            show_gaps: Show gap to leader
            show_sectors: Show sector times
        """
        table = Table(
            title=f"[bold white]{self.session.event['EventName']} - {self.session.name}[/]",
            title_style="bold white on #1E1E1E",
            header_style="bold white",
            border_style="dim white",
            show_lines=True,
            padding=(0, 1)
        )

        # Add columns
        table.add_column("P", justify="center", style="bold", width=3)
        table.add_column("Driver", justify="left", width=20)
        table.add_column("Team", justify="left", width=15)
        table.add_column("Time/Gap", justify="right", width=14)

        if show_sectors:
            table.add_column("S1", justify="right", width=10)
            table.add_column("S2", justify="right", width=10)
            table.add_column("S3", justify="right", width=10)

        table.add_column("Last Lap", justify="right", width=12)
        table.add_column("Best Lap", justify="right", width=12)

        # Get standings
        standings = self._get_standings(lap_number)

        for pos, row in standings.iterrows():
            driver = row['Abbreviation'] if 'Abbreviation' in row else row.get('Driver', 'UNK')
            team = get_team_by_driver(driver)
            team_color = team.primary_color if team else '#FFFFFF'
            team_name = team.name if team else "Unknown"

            # Format gap
            if pos == 0:
                gap_str = self._format_time(row.get('Time', row.get('LapTime', '')))
            else:
                gap = row.get('Gap', row.get('GapToLeader', ''))
                if pd.notna(gap):
                    gap_str = f"+{gap}" if isinstance(gap, str) else f"+{gap:.3f}"
                else:
                    gap_str = "---"

            # Create colored driver name
            driver_text = Text()
            driver_text.append("█ ", style=Style(color=team_color))
            driver_text.append(f"{driver}", style="bold white")

            row_data = [
                f"[bold]{pos + 1}[/]",
                driver_text,
                f"[{team_color}]{team_name}[/]",
                gap_str,
            ]

            if show_sectors:
                s1 = self._format_sector(row.get('Sector1Time', ''))
                s2 = self._format_sector(row.get('Sector2Time', ''))
                s3 = self._format_sector(row.get('Sector3Time', ''))
                row_data.extend([s1, s2, s3])

            # Last and best lap times
            last_lap = self._format_time(row.get('LastLapTime', ''))
            best_lap = self._format_time(row.get('BestLapTime', row.get('FastestLap', '')))
            row_data.extend([last_lap, best_lap])

            table.add_row(*row_data)

        return table

    def create_driver_card(self, driver: str) -> Panel:
        """Create a detailed driver information card."""
        team = get_team_by_driver(driver)
        team_color = team.primary_color if team else '#FFFFFF'

        driver_laps = self.laps.pick_driver(driver)
        fastest_lap = driver_laps.pick_fastest() if len(driver_laps) > 0 else None

        # Get driver info from team data
        driver_info = None
        if team:
            for d in team.drivers:
                if d.abbreviation == driver:
                    driver_info = d
                    break

        content = Text()
        content.append(f"#{driver_info.number if driver_info else '?'} ", style=f"bold {team_color}")
        content.append(f"{driver_info.name if driver_info else driver}\n", style="bold white")
        content.append(f"{team.full_name if team else 'Unknown Team'}\n\n", style=f"{team_color}")

        if fastest_lap is not None:
            content.append("Fastest Lap: ", style="dim white")
            content.append(f"{fastest_lap['LapTime']}\n", style="bold green")
            content.append("On Lap: ", style="dim white")
            content.append(f"{fastest_lap['LapNumber']}\n", style="white")

            if pd.notna(fastest_lap.get('SpeedST')):
                content.append("Speed Trap: ", style="dim white")
                content.append(f"{fastest_lap['SpeedST']:.1f} km/h\n", style="cyan")

        content.append(f"\nTotal Laps: {len(driver_laps)}", style="dim white")

        return Panel(
            content,
            title=f"[{team_color}]{driver}[/]",
            border_style=team_color,
            padding=(1, 2)
        )

    def create_championship_standings(self) -> Table:
        """Create a championship standings table."""
        table = Table(
            title="[bold white]2024 Driver Championship[/]",
            header_style="bold white",
            border_style="dim white"
        )

        table.add_column("Pos", justify="center", width=4)
        table.add_column("Driver", justify="left", width=20)
        table.add_column("Team", justify="left", width=15)
        table.add_column("Points", justify="right", width=8)

        # Note: This would need to pull from actual championship data
        # For now using results from current session
        for idx, (_, row) in enumerate(self.results.iterrows()):
            if idx >= 20:  # Only top 20
                break

            driver = row.get('Abbreviation', 'UNK')
            team = get_team_by_driver(driver)
            team_color = team.primary_color if team else '#FFFFFF'
            points = row.get('Points', 0)

            table.add_row(
                f"{idx + 1}",
                f"[{team_color}]{driver}[/]",
                team.name if team else "Unknown",
                f"{points:.0f}" if pd.notna(points) else "0"
            )

        return table

    def create_fastest_laps_table(self) -> Table:
        """Create a table showing fastest laps for all drivers."""
        table = Table(
            title=f"[bold white]Fastest Laps - {self.session.event['EventName']}[/]",
            header_style="bold white",
            border_style="dim white"
        )

        table.add_column("Pos", justify="center", width=4)
        table.add_column("Driver", justify="left", width=8)
        table.add_column("Lap Time", justify="right", width=12)
        table.add_column("Lap #", justify="center", width=6)
        table.add_column("Gap", justify="right", width=10)

        # Get fastest laps
        fastest_laps = []
        for driver in self.laps['Driver'].unique():
            driver_laps = self.laps.pick_driver(driver)
            fastest = driver_laps.pick_fastest()
            if fastest is not None and pd.notna(fastest['LapTime']):
                fastest_laps.append({
                    'Driver': driver,
                    'LapTime': fastest['LapTime'],
                    'LapNumber': fastest['LapNumber']
                })

        fastest_laps.sort(key=lambda x: x['LapTime'])

        leader_time = fastest_laps[0]['LapTime'] if fastest_laps else None

        for idx, lap in enumerate(fastest_laps[:20]):
            driver = lap['Driver']
            team = get_team_by_driver(driver)
            team_color = team.primary_color if team else '#FFFFFF'

            if idx == 0:
                gap_str = "[green]LEADER[/]"
            else:
                gap = lap['LapTime'] - leader_time
                gap_str = f"+{gap.total_seconds():.3f}s"

            time_style = "bold green" if idx == 0 else "white"

            table.add_row(
                f"{idx + 1}",
                f"[{team_color}]{driver}[/]",
                f"[{time_style}]{lap['LapTime']}[/]",
                f"{lap['LapNumber']}",
                gap_str
            )

        return table

    def print_timing_tower(self):
        """Print the full timing tower to the console."""
        console.print("\n")
        console.print(self.create_timing_table())
        console.print("\n")

    def print_fastest_laps(self):
        """Print the fastest laps table."""
        console.print("\n")
        console.print(self.create_fastest_laps_table())
        console.print("\n")

    def _get_standings(self, lap_number: Optional[int] = None) -> pd.DataFrame:
        """Get race standings at a specific lap or final results."""
        if lap_number is None:
            return self.results.sort_values('Position').reset_index(drop=True)

        # Get positions at specific lap
        lap_data = self.laps[self.laps['LapNumber'] == lap_number]
        if len(lap_data) == 0:
            return self.results.sort_values('Position').reset_index(drop=True)

        return lap_data.sort_values('Position').reset_index(drop=True)

    def _format_time(self, time_val) -> str:
        """Format a lap time for display."""
        if pd.isna(time_val) or time_val == '':
            return "---"
        return str(time_val).split(' ')[-1] if ' ' in str(time_val) else str(time_val)

    def _format_sector(self, sector_time) -> str:
        """Format a sector time with color coding."""
        if pd.isna(sector_time) or sector_time == '':
            return "[dim]---[/]"
        return f"[white]{sector_time}[/]"


def display_race_summary(session: fastf1.core.Session):
    """Display a comprehensive race summary."""
    board = TimingBoard(session)

    console.print(Panel(
        f"[bold white]{session.event['EventName']}[/]\n"
        f"[dim]{session.event['EventDate']} - {session.name}[/]",
        title="F1 Session Summary",
        border_style="red"
    ))

    board.print_timing_tower()
    board.print_fastest_laps()


if __name__ == "__main__":
    console.print("[bold red]F1 Timing Board[/]")
    console.print("Example usage:")
    console.print("  from f1_tracker.data import quick_load")
    console.print("  session = quick_load(2024, 'Bahrain', 'R')")
    console.print("  from f1_tracker.timing_board import display_race_summary")
    console.print("  display_race_summary(session)")
