"""
Telemetry Visualization Module
==============================
Creates detailed telemetry charts showing speed, throttle, brake, and gear data.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Optional, List, Tuple
import fastf1
import pandas as pd

from .teams import get_driver_color, get_team_by_driver


class TelemetryVisualizer:
    """Creates telemetry visualizations for F1 data analysis."""

    def __init__(self, session: fastf1.core.Session):
        self.session = session

    def plot_speed_trace(
        self,
        driver: str,
        lap_number: Optional[int] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot speed trace over distance for a lap.

        Args:
            driver: Driver abbreviation
            lap_number: Specific lap (uses fastest if not provided)
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 6))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        color = get_driver_color(driver)
        telemetry = self._get_telemetry(driver, lap_number)

        ax.plot(
            telemetry['Distance'],
            telemetry['Speed'],
            color=color,
            linewidth=2
        )

        self._style_axis(ax, 'Distance (m)', 'Speed (km/h)')
        lap_info = self._get_lap_info(driver, lap_number)
        ax.set_title(
            f"Speed Trace - {driver} | Lap {lap_info['LapNumber']} | {lap_info['LapTime']}",
            color='white',
            fontsize=14,
            weight='bold'
        )

        return ax

    def plot_full_telemetry(
        self,
        driver: str,
        lap_number: Optional[int] = None,
        figsize: Tuple[int, int] = (16, 12)
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        """
        Create a comprehensive telemetry view with speed, throttle, brake, and gear.

        Args:
            driver: Driver abbreviation
            lap_number: Specific lap number
            figsize: Figure size

        Returns:
            Figure and list of axes
        """
        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        fig.patch.set_facecolor('#1E1E1E')

        color = get_driver_color(driver)
        telemetry = self._get_telemetry(driver, lap_number)
        lap_info = self._get_lap_info(driver, lap_number)

        # Speed trace
        axes[0].plot(telemetry['Distance'], telemetry['Speed'], color=color, linewidth=2)
        self._style_axis(axes[0], '', 'Speed\n(km/h)')
        axes[0].fill_between(telemetry['Distance'], telemetry['Speed'], alpha=0.3, color=color)

        # Throttle
        axes[1].plot(telemetry['Distance'], telemetry['Throttle'], color='#00FF00', linewidth=2)
        self._style_axis(axes[1], '', 'Throttle\n(%)')
        axes[1].set_ylim(-5, 105)
        axes[1].fill_between(telemetry['Distance'], telemetry['Throttle'], alpha=0.3, color='#00FF00')

        # Brake
        axes[2].plot(telemetry['Distance'], telemetry['Brake'], color='#FF0000', linewidth=2)
        self._style_axis(axes[2], '', 'Brake')
        axes[2].set_ylim(-0.05, 1.05)
        axes[2].fill_between(telemetry['Distance'], telemetry['Brake'], alpha=0.3, color='#FF0000')

        # Gear
        axes[3].plot(telemetry['Distance'], telemetry['nGear'], color='#FFD700', linewidth=2, drawstyle='steps-post')
        self._style_axis(axes[3], 'Distance (m)', 'Gear')
        axes[3].set_ylim(0, 9)
        axes[3].set_yticks(range(1, 9))

        # Add DRS zones highlighting
        if 'DRS' in telemetry.columns:
            for ax in axes:
                drs_active = telemetry['DRS'] > 0
                ax.fill_between(
                    telemetry['Distance'],
                    ax.get_ylim()[0],
                    ax.get_ylim()[1],
                    where=drs_active,
                    alpha=0.1,
                    color='#00FFFF',
                    label='DRS Active'
                )

        team = get_team_by_driver(driver)
        team_name = team.full_name if team else "Unknown Team"
        fig.suptitle(
            f"Telemetry - {driver} | {team_name}\n"
            f"Lap {lap_info['LapNumber']} | {lap_info['LapTime']} | {self.session.event['EventName']}",
            color='white',
            fontsize=16,
            weight='bold'
        )

        plt.tight_layout()
        return fig, axes

    def plot_comparison(
        self,
        drivers: List[str],
        metric: str = 'Speed',
        lap_numbers: Optional[List[int]] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Compare telemetry between multiple drivers.

        Args:
            drivers: List of driver abbreviations
            metric: Telemetry metric to compare ('Speed', 'Throttle', 'Brake', 'nGear')
            lap_numbers: Optional list of lap numbers (same order as drivers)
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 8))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        legend_handles = []

        for i, driver in enumerate(drivers):
            lap_num = lap_numbers[i] if lap_numbers else None
            color = get_driver_color(driver)
            telemetry = self._get_telemetry(driver, lap_num)
            lap_info = self._get_lap_info(driver, lap_num)

            ax.plot(
                telemetry['Distance'],
                telemetry[metric],
                color=color,
                linewidth=2,
                label=f"{driver} - {lap_info['LapTime']}"
            )

            team = get_team_by_driver(driver)
            legend_handles.append(mpatches.Patch(
                color=color,
                label=f"{driver} ({team.name if team else 'Unknown'}) - {lap_info['LapTime']}"
            ))

        ax.legend(
            handles=legend_handles,
            loc='upper right',
            facecolor='#2E2E2E',
            edgecolor='white',
            labelcolor='white'
        )

        self._style_axis(ax, 'Distance (m)', metric)
        ax.set_title(
            f"{metric} Comparison - {self.session.event['EventName']}",
            color='white',
            fontsize=16,
            weight='bold'
        )

        return ax

    def plot_speed_delta(
        self,
        driver1: str,
        driver2: str,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot the speed difference between two drivers.
        Positive = driver1 faster, Negative = driver2 faster.

        Args:
            driver1: First driver abbreviation
            driver2: Second driver abbreviation
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 6))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        tel1 = self._get_telemetry(driver1)
        tel2 = self._get_telemetry(driver2)

        # Interpolate to common distance points
        common_distance = np.linspace(
            max(tel1['Distance'].min(), tel2['Distance'].min()),
            min(tel1['Distance'].max(), tel2['Distance'].max()),
            1000
        )

        speed1 = np.interp(common_distance, tel1['Distance'], tel1['Speed'])
        speed2 = np.interp(common_distance, tel2['Distance'], tel2['Speed'])
        delta = speed1 - speed2

        color1 = get_driver_color(driver1)
        color2 = get_driver_color(driver2)

        ax.fill_between(
            common_distance,
            delta,
            0,
            where=(delta > 0),
            interpolate=True,
            alpha=0.7,
            color=color1,
            label=f'{driver1} faster'
        )
        ax.fill_between(
            common_distance,
            delta,
            0,
            where=(delta <= 0),
            interpolate=True,
            alpha=0.7,
            color=color2,
            label=f'{driver2} faster'
        )

        ax.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        ax.legend(
            loc='upper right',
            facecolor='#2E2E2E',
            edgecolor='white',
            labelcolor='white'
        )

        self._style_axis(ax, 'Distance (m)', 'Speed Delta (km/h)')
        ax.set_title(
            f"Speed Delta: {driver1} vs {driver2} - {self.session.event['EventName']}",
            color='white',
            fontsize=16,
            weight='bold'
        )

        return ax

    def plot_mini_sectors(
        self,
        driver: str,
        lap_number: Optional[int] = None,
        num_sectors: int = 25,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Create a mini-sector analysis showing performance across track sections.

        Args:
            driver: Driver abbreviation
            lap_number: Specific lap
            num_sectors: Number of mini-sectors to divide the track into
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 6))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        telemetry = self._get_telemetry(driver, lap_number)
        color = get_driver_color(driver)

        max_distance = telemetry['Distance'].max()
        sector_length = max_distance / num_sectors
        sector_speeds = []

        for i in range(num_sectors):
            start = i * sector_length
            end = (i + 1) * sector_length
            sector_data = telemetry[
                (telemetry['Distance'] >= start) &
                (telemetry['Distance'] < end)
            ]
            avg_speed = sector_data['Speed'].mean() if len(sector_data) > 0 else 0
            sector_speeds.append(avg_speed)

        bars = ax.bar(
            range(num_sectors),
            sector_speeds,
            color=color,
            alpha=0.8,
            edgecolor='white',
            linewidth=0.5
        )

        # Highlight fastest and slowest sectors
        max_idx = np.argmax(sector_speeds)
        min_idx = np.argmin(sector_speeds)
        bars[max_idx].set_color('#00FF00')
        bars[min_idx].set_color('#FF0000')

        self._style_axis(ax, 'Mini-Sector', 'Avg Speed (km/h)')
        ax.set_xticks(range(0, num_sectors, 5))

        lap_info = self._get_lap_info(driver, lap_number)
        ax.set_title(
            f"Mini-Sector Analysis - {driver} | Lap {lap_info['LapNumber']}",
            color='white',
            fontsize=14,
            weight='bold'
        )

        return ax

    def _get_telemetry(self, driver: str, lap_number: Optional[int] = None) -> pd.DataFrame:
        """Helper to get telemetry data."""
        driver_laps = self.session.laps.pick_driver(driver)
        if lap_number:
            lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
        else:
            lap = driver_laps.pick_fastest()
        return lap.get_telemetry()

    def _get_lap_info(self, driver: str, lap_number: Optional[int] = None) -> dict:
        """Helper to get lap information."""
        driver_laps = self.session.laps.pick_driver(driver)
        if lap_number:
            lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
        else:
            lap = driver_laps.pick_fastest()
        return {'LapNumber': lap['LapNumber'], 'LapTime': lap['LapTime']}

    def _style_axis(self, ax: plt.Axes, xlabel: str, ylabel: str):
        """Apply consistent dark theme styling to axis."""
        ax.set_facecolor('#1E1E1E')
        ax.set_xlabel(xlabel, color='white')
        ax.set_ylabel(ylabel, color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('#1E1E1E')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('#1E1E1E')
        ax.grid(True, alpha=0.2, color='white')


def create_telemetry_dashboard(
    session: fastf1.core.Session,
    driver: str = "VER"
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Quick helper to create a full telemetry dashboard."""
    viz = TelemetryVisualizer(session)
    return viz.plot_full_telemetry(driver)


if __name__ == "__main__":
    print("Telemetry Visualizer - Run with a loaded session")
    print("Example usage:")
    print("  from f1_tracker.data import quick_load")
    print("  session = quick_load(2024, 'Bahrain', 'R')")
    print("  from f1_tracker.telemetry import create_telemetry_dashboard")
    print("  fig, axes = create_telemetry_dashboard(session, 'VER')")
    print("  plt.show()")
