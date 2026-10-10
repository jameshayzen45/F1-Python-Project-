"""
F1 Data Loading Module
======================
Handles loading session data from FastF1 with caching.
"""

import fastf1
from pathlib import Path
from typing import Optional
import pandas as pd


# Set up cache directory for faster subsequent loads
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


# 2024 F1 Calendar with circuit information
CALENDAR_2024 = {
    1: {"name": "Bahrain Grand Prix", "circuit": "Bahrain International Circuit", "country": "Bahrain"},
    2: {"name": "Saudi Arabian Grand Prix", "circuit": "Jeddah Corniche Circuit", "country": "Saudi Arabia"},
    3: {"name": "Australian Grand Prix", "circuit": "Albert Park Circuit", "country": "Australia"},
    4: {"name": "Japanese Grand Prix", "circuit": "Suzuka International Racing Course", "country": "Japan"},
    5: {"name": "Chinese Grand Prix", "circuit": "Shanghai International Circuit", "country": "China"},
    6: {"name": "Miami Grand Prix", "circuit": "Miami International Autodrome", "country": "USA"},
    7: {"name": "Emilia Romagna Grand Prix", "circuit": "Autodromo Enzo e Dino Ferrari", "country": "Italy"},
    8: {"name": "Monaco Grand Prix", "circuit": "Circuit de Monaco", "country": "Monaco"},
    9: {"name": "Canadian Grand Prix", "circuit": "Circuit Gilles Villeneuve", "country": "Canada"},
    10: {"name": "Spanish Grand Prix", "circuit": "Circuit de Barcelona-Catalunya", "country": "Spain"},
    11: {"name": "Austrian Grand Prix", "circuit": "Red Bull Ring", "country": "Austria"},
    12: {"name": "British Grand Prix", "circuit": "Silverstone Circuit", "country": "Great Britain"},
    13: {"name": "Hungarian Grand Prix", "circuit": "Hungaroring", "country": "Hungary"},
    14: {"name": "Belgian Grand Prix", "circuit": "Circuit de Spa-Francorchamps", "country": "Belgium"},
    15: {"name": "Dutch Grand Prix", "circuit": "Circuit Zandvoort", "country": "Netherlands"},
    16: {"name": "Italian Grand Prix", "circuit": "Autodromo Nazionale Monza", "country": "Italy"},
    17: {"name": "Azerbaijan Grand Prix", "circuit": "Baku City Circuit", "country": "Azerbaijan"},
    18: {"name": "Singapore Grand Prix", "circuit": "Marina Bay Street Circuit", "country": "Singapore"},
    19: {"name": "United States Grand Prix", "circuit": "Circuit of the Americas", "country": "USA"},
    20: {"name": "Mexico City Grand Prix", "circuit": "Autodromo Hermanos Rodriguez", "country": "Mexico"},
    21: {"name": "Sao Paulo Grand Prix", "circuit": "Autodromo Jose Carlos Pace", "country": "Brazil"},
    22: {"name": "Las Vegas Grand Prix", "circuit": "Las Vegas Strip Circuit", "country": "USA"},
    23: {"name": "Qatar Grand Prix", "circuit": "Lusail International Circuit", "country": "Qatar"},
    24: {"name": "Abu Dhabi Grand Prix", "circuit": "Yas Marina Circuit", "country": "UAE"},
}


class F1DataLoader:
    """Handles loading and caching F1 session data."""

    def __init__(self):
        self.current_session = None
        self.current_year = 2024

    def load_session(
        self,
        year: int,
        race: int | str,
        session_type: str = "R"
    ) -> fastf1.core.Session:
        """
        Load an F1 session.

        Args:
            year: The season year (e.g., 2024)
            race: Race number or Grand Prix name
            session_type: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S' (Sprint), 'R' (Race)

        Returns:
            FastF1 Session object with loaded data
        """
        print(f"Loading {year} {race} - {session_type}...")
        session = fastf1.get_session(year, race, session_type)
        session.load()
        self.current_session = session
        return session

    def get_race_results(self, session: Optional[fastf1.core.Session] = None) -> pd.DataFrame:
        """Get the final race results/classification."""
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")
        return session.results

    def get_lap_times(
        self,
        session: Optional[fastf1.core.Session] = None,
        driver: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get lap times for the session.

        Args:
            session: FastF1 session (uses current if not provided)
            driver: Optional driver abbreviation to filter

        Returns:
            DataFrame with lap times
        """
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")

        laps = session.laps
        if driver:
            laps = laps.pick_driver(driver)
        return laps

    def get_fastest_laps(
        self,
        session: Optional[fastf1.core.Session] = None
    ) -> pd.DataFrame:
        """Get the fastest lap for each driver."""
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")

        laps = session.laps
        fastest_laps = laps.groupby('Driver').apply(
            lambda x: x.loc[x['LapTime'].idxmin()] if not x['LapTime'].isna().all() else None
        ).dropna()
        return fastest_laps.sort_values('LapTime')

    def get_telemetry(
        self,
        driver: str,
        lap_number: Optional[int] = None,
        session: Optional[fastf1.core.Session] = None
    ) -> pd.DataFrame:
        """
        Get telemetry data for a driver's lap.

        Args:
            driver: Driver abbreviation (e.g., 'VER', 'HAM')
            lap_number: Specific lap number (uses fastest if not provided)
            session: FastF1 session

        Returns:
            DataFrame with telemetry (Speed, Throttle, Brake, Gear, DRS, etc.)
        """
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")

        driver_laps = session.laps.pick_driver(driver)

        if lap_number:
            lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
        else:
            lap = driver_laps.pick_fastest()

        return lap.get_telemetry()

    def get_driver_position_data(
        self,
        driver: str,
        session: Optional[fastf1.core.Session] = None
    ) -> pd.DataFrame:
        """Get position data for track visualization."""
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")

        lap = session.laps.pick_driver(driver).pick_fastest()
        return lap.get_pos_data()

    def get_circuit_info(
        self,
        session: Optional[fastf1.core.Session] = None
    ):
        """Get circuit information including track layout."""
        session = session or self.current_session
        if session is None:
            raise ValueError("No session loaded. Call load_session first.")
        return session.get_circuit_info()


# Singleton instance for convenience
loader = F1DataLoader()


def quick_load(year: int = 2024, race: int | str = 1, session: str = "R"):
    """Quick helper to load a session."""
    return loader.load_session(year, race, session)


if __name__ == "__main__":
    # Test loading
    print("Testing F1 Data Loader...")
    print("\n2024 F1 Calendar:")
    for round_num, info in CALENDAR_2024.items():
        print(f"  Round {round_num}: {info['name']} - {info['circuit']}")
