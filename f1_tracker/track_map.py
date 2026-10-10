"""
Track Map Visualization
=======================
Creates visual circuit maps with car positions and racing lines.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Optional, List, Dict
import fastf1
import fastf1.plotting

from .teams import get_driver_color, get_team_by_driver


# Enable FastF1's plotting features
fastf1.plotting.setup_mpl(misc_mpl_mods=False)


class TrackMapVisualizer:
    """Creates visual representations of F1 circuits."""

    def __init__(self, session: fastf1.core.Session):
        self.session = session
        self.circuit_info = session.get_circuit_info()

    def plot_circuit(
        self,
        ax: Optional[plt.Axes] = None,
        color: str = '#FFFFFF',
        linewidth: float = 4.0,
        show_corners: bool = True
    ) -> plt.Axes:
        """
        Plot the circuit layout.

        Args:
            ax: Matplotlib axes (creates new if not provided)
            color: Track outline color
            linewidth: Track line width
            show_corners: Whether to annotate corner numbers

        Returns:
            Matplotlib axes with circuit plotted
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        # Get track coordinates from a reference lap
        lap = self.session.laps.pick_fastest()
        pos_data = lap.get_pos_data()

        # Plot the track
        ax.plot(pos_data['X'], pos_data['Y'], color=color, linewidth=linewidth)

        # Plot corner markers if available
        if show_corners and hasattr(self.circuit_info, 'corners'):
            corners = self.circuit_info.corners
            for _, corner in corners.iterrows():
                ax.annotate(
                    f"T{int(corner['Number'])}",
                    xy=(corner['X'], corner['Y']),
                    fontsize=8,
                    color='#FFD700',
                    ha='center',
                    va='center',
                    weight='bold'
                )

        # Mark start/finish line
        if hasattr(self.circuit_info, 'rotation'):
            # Add start/finish indicator
            ax.annotate(
                'START/FINISH',
                xy=(pos_data['X'].iloc[0], pos_data['Y'].iloc[0]),
                fontsize=10,
                color='#00FF00',
                weight='bold'
            )

        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(
            f"{self.session.event['EventName']} - {self.circuit_info.corners['Letter'].iloc[0] if hasattr(self.circuit_info, 'corners') and len(self.circuit_info.corners) > 0 else 'Circuit'}",
            color='white',
            fontsize=16,
            weight='bold'
        )

        return ax

    def plot_driver_lap(
        self,
        driver: str,
        lap_number: Optional[int] = None,
        ax: Optional[plt.Axes] = None,
        color: Optional[str] = None,
        show_speed: bool = True
    ) -> plt.Axes:
        """
        Plot a driver's racing line with optional speed coloring.

        Args:
            driver: Driver abbreviation
            lap_number: Specific lap (uses fastest if not provided)
            ax: Matplotlib axes
            color: Override color (uses team color if not provided)
            show_speed: Color the line by speed
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        # Get driver color
        line_color = color or get_driver_color(driver)

        # Get lap data
        driver_laps = self.session.laps.pick_driver(driver)
        if lap_number:
            lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
        else:
            lap = driver_laps.pick_fastest()

        telemetry = lap.get_telemetry()

        if show_speed:
            # Color by speed
            points = np.array([telemetry['X'], telemetry['Y']]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            from matplotlib.collections import LineCollection
            norm = plt.Normalize(telemetry['Speed'].min(), telemetry['Speed'].max())
            lc = LineCollection(segments, cmap='plasma', norm=norm)
            lc.set_array(telemetry['Speed'])
            lc.set_linewidth(3)
            ax.add_collection(lc)

            # Add colorbar
            cbar = plt.colorbar(lc, ax=ax, shrink=0.5)
            cbar.set_label('Speed (km/h)', color='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        else:
            ax.plot(telemetry['X'], telemetry['Y'], color=line_color, linewidth=3)

        ax.set_aspect('equal')
        ax.axis('off')

        team = get_team_by_driver(driver)
        team_name = team.name if team else "Unknown"
        ax.set_title(
            f"{driver} - {team_name}\nLap {lap['LapNumber']} - {lap['LapTime']}",
            color='white',
            fontsize=14,
            weight='bold'
        )

        return ax

    def plot_comparison(
        self,
        drivers: List[str],
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot multiple drivers' racing lines overlaid for comparison.

        Args:
            drivers: List of driver abbreviations
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        legend_handles = []

        for driver in drivers:
            color = get_driver_color(driver)
            lap = self.session.laps.pick_driver(driver).pick_fastest()
            telemetry = lap.get_telemetry()

            ax.plot(
                telemetry['X'], telemetry['Y'],
                color=color,
                linewidth=2.5,
                label=driver,
                alpha=0.8
            )

            team = get_team_by_driver(driver)
            label = f"{driver} ({team.name if team else 'Unknown'})"
            legend_handles.append(mpatches.Patch(color=color, label=label))

        ax.legend(
            handles=legend_handles,
            loc='upper right',
            facecolor='#2E2E2E',
            edgecolor='white',
            labelcolor='white'
        )
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(
            f"Racing Line Comparison - {self.session.event['EventName']}",
            color='white',
            fontsize=16,
            weight='bold'
        )

        return ax

    def plot_positions_at_distance(
        self,
        lap_number: int,
        distance: float,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot all car positions at a specific distance into a lap.
        Useful for visualizing track position battles.

        Args:
            lap_number: The lap to analyze
            distance: Distance in meters from start line
            ax: Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor('#1E1E1E')
            ax.set_facecolor('#1E1E1E')

        # First plot the circuit
        self.plot_circuit(ax=ax, color='#404040', linewidth=8, show_corners=False)

        # Get all drivers' positions
        for driver in self.session.laps['Driver'].unique():
            try:
                driver_lap = self.session.laps.pick_driver(driver)
                lap_data = driver_lap[driver_lap['LapNumber'] == lap_number]
                if len(lap_data) == 0:
                    continue

                telemetry = lap_data.iloc[0].get_telemetry()

                # Find position at specified distance
                idx = (telemetry['Distance'] - distance).abs().idxmin()
                pos = telemetry.loc[idx]

                color = get_driver_color(driver)
                ax.scatter(
                    pos['X'], pos['Y'],
                    color=color,
                    s=200,
                    zorder=5,
                    edgecolors='white',
                    linewidths=2
                )
                ax.annotate(
                    driver,
                    xy=(pos['X'], pos['Y']),
                    xytext=(10, 10),
                    textcoords='offset points',
                    color='white',
                    fontsize=10,
                    weight='bold'
                )
            except Exception:
                continue  # Skip if data not available for this driver

        ax.set_title(
            f"Car Positions - Lap {lap_number} at {distance}m",
            color='white',
            fontsize=16,
            weight='bold'
        )

        return ax


def create_track_visualization(session: fastf1.core.Session, driver: str = "VER"):
    """Quick helper to create a track visualization."""
    viz = TrackMapVisualizer(session)

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    fig.patch.set_facecolor('#1E1E1E')

    # Circuit outline
    viz.plot_circuit(ax=axes[0])

    # Driver's fastest lap with speed coloring
    viz.plot_driver_lap(driver, ax=axes[1], show_speed=True)

    plt.tight_layout()
    return fig, axes


if __name__ == "__main__":
    print("Track Map Visualizer - Run with a loaded session")
    print("Example usage:")
    print("  from f1_tracker.data import quick_load")
    print("  session = quick_load(2024, 'Bahrain', 'R')")
    print("  from f1_tracker.track_map import create_track_visualization")
    print("  fig, axes = create_track_visualization(session, 'VER')")
    print("  plt.show()")
