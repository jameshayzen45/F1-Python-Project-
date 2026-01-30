"""
F1 Teams and Drivers Database
=============================
Contains all 2024 F1 teams with official colors and driver information.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Driver:
    """Represents an F1 driver."""
    name: str
    abbreviation: str
    number: int
    nationality: str


@dataclass
class Team:
    """Represents an F1 team with colors and drivers."""
    name: str
    full_name: str
    primary_color: str      # Hex color
    secondary_color: str    # Hex color
    drivers: List[Driver]


# Official 2024 F1 Team Colors (from F1 brand guidelines)
TEAMS_2024: Dict[str, Team] = {
    "red_bull": Team(
        name="Red Bull",
        full_name="Oracle Red Bull Racing",
        primary_color="#3671C6",
        secondary_color="#FFD700",
        drivers=[
            Driver("Max Verstappen", "VER", 1, "Dutch"),
            Driver("Sergio Perez", "PER", 11, "Mexican"),
        ]
    ),
    "ferrari": Team(
        name="Ferrari",
        full_name="Scuderia Ferrari",
        primary_color="#E80020",
        secondary_color="#FFEB00",
        drivers=[
            Driver("Charles Leclerc", "LEC", 16, "Monegasque"),
            Driver("Carlos Sainz", "SAI", 55, "Spanish"),
        ]
    ),
    "mercedes": Team(
        name="Mercedes",
        full_name="Mercedes-AMG PETRONAS F1 Team",
        primary_color="#27F4D2",
        secondary_color="#000000",
        drivers=[
            Driver("Lewis Hamilton", "HAM", 44, "British"),
            Driver("George Russell", "RUS", 63, "British"),
        ]
    ),
    "mclaren": Team(
        name="McLaren",
        full_name="McLaren F1 Team",
        primary_color="#FF8000",
        secondary_color="#47C7FC",
        drivers=[
            Driver("Lando Norris", "NOR", 4, "British"),
            Driver("Oscar Piastri", "PIA", 81, "Australian"),
        ]
    ),
    "aston_martin": Team(
        name="Aston Martin",
        full_name="Aston Martin Aramco F1 Team",
        primary_color="#229971",
        secondary_color="#CEDC00",
        drivers=[
            Driver("Fernando Alonso", "ALO", 14, "Spanish"),
            Driver("Lance Stroll", "STR", 18, "Canadian"),
        ]
    ),
    "alpine": Team(
        name="Alpine",
        full_name="BWT Alpine F1 Team",
        primary_color="#FF87BC",
        secondary_color="#0093CC",
        drivers=[
            Driver("Pierre Gasly", "GAS", 10, "French"),
            Driver("Esteban Ocon", "OCO", 31, "French"),
        ]
    ),
    "williams": Team(
        name="Williams",
        full_name="Williams Racing",
        primary_color="#64C4FF",
        secondary_color="#041E42",
        drivers=[
            Driver("Alexander Albon", "ALB", 23, "Thai"),
            Driver("Logan Sargeant", "SAR", 2, "American"),
        ]
    ),
    "rb": Team(
        name="RB",
        full_name="Visa Cash App RB F1 Team",
        primary_color="#6692FF",
        secondary_color="#FFFFFF",
        drivers=[
            Driver("Yuki Tsunoda", "TSU", 22, "Japanese"),
            Driver("Daniel Ricciardo", "RIC", 3, "Australian"),
        ]
    ),
    "kick_sauber": Team(
        name="Kick Sauber",
        full_name="Stake F1 Team Kick Sauber",
        primary_color="#52E252",
        secondary_color="#000000",
        drivers=[
            Driver("Valtteri Bottas", "BOT", 77, "Finnish"),
            Driver("Zhou Guanyu", "ZHO", 24, "Chinese"),
        ]
    ),
    "haas": Team(
        name="Haas",
        full_name="MoneyGram Haas F1 Team",
        primary_color="#B6BABD",
        secondary_color="#DA291C",
        drivers=[
            Driver("Kevin Magnussen", "MAG", 20, "Danish"),
            Driver("Nico Hulkenberg", "HUL", 27, "German"),
        ]
    ),
}


def get_driver_color(driver_abbreviation: str) -> str:
    """Get the team color for a driver by their abbreviation."""
    for team in TEAMS_2024.values():
        for driver in team.drivers:
            if driver.abbreviation == driver_abbreviation:
                return team.primary_color
    return "#FFFFFF"  # Default white


def get_all_drivers() -> List[Driver]:
    """Get a flat list of all drivers."""
    drivers = []
    for team in TEAMS_2024.values():
        drivers.extend(team.drivers)
    return drivers


def get_driver_by_abbreviation(abbrev: str) -> Driver | None:
    """Find a driver by their 3-letter abbreviation."""
    for team in TEAMS_2024.values():
        for driver in team.drivers:
            if driver.abbreviation == abbrev:
                return driver
    return None


def get_team_by_driver(driver_abbreviation: str) -> Team | None:
    """Get the team for a given driver abbreviation."""
    for team in TEAMS_2024.values():
        for driver in team.drivers:
            if driver.abbreviation == driver_abbreviation:
                return team
    return None


# Driver abbreviation to FastF1 color mapping (for consistency)
DRIVER_COLORS: Dict[str, str] = {
    driver.abbreviation: get_driver_color(driver.abbreviation)
    for driver in get_all_drivers()
}


if __name__ == "__main__":
    # Quick test
    print("F1 2024 Teams and Drivers")
    print("=" * 50)
    for team_key, team in TEAMS_2024.items():
        print(f"\n{team.full_name}")
        print(f"  Color: {team.primary_color}")
        for driver in team.drivers:
            print(f"  #{driver.number} {driver.name} ({driver.abbreviation})")
