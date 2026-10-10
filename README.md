# F1 Live Timings Tracker

A Python application for viewing F1 timing data, telemetry, and track positions - built as a portfolio project for Mercedes HPP application.

## Features

- **Live Timing Board** - F1 TV-style timing tower with positions, gaps, and lap times
- **Telemetry Visualization** - Speed, throttle, brake, and gear traces
- **Track Maps** - Circuit layouts with racing lines colored by speed
- **Driver Comparisons** - Side-by-side telemetry and racing line analysis
- **All 2024 Teams & Drivers** - Complete with official team colors

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the interactive application
python -m f1_tracker.main
```

## Usage Examples

### Load a Session
```python
from f1_tracker.data import quick_load

# Load the 2024 Bahrain Grand Prix race
session = quick_load(2024, 'Bahrain', 'R')
```

### View Timing Data
```python
from f1_tracker.timing_board import display_race_summary

display_race_summary(session)
```

### Create Telemetry Dashboard
```python
from f1_tracker.telemetry import create_telemetry_dashboard
import matplotlib.pyplot as plt

fig, axes = create_telemetry_dashboard(session, 'VER')
plt.show()
```

### Visualize Track Map
```python
from f1_tracker.track_map import create_track_visualization
import matplotlib.pyplot as plt

fig, axes = create_track_visualization(session, 'HAM')
plt.show()
```

### Compare Drivers
```python
from f1_tracker.telemetry import TelemetryVisualizer
import matplotlib.pyplot as plt

viz = TelemetryVisualizer(session)

# Speed comparison
fig, ax = plt.subplots(figsize=(16, 8))
viz.plot_comparison(['VER', 'HAM', 'LEC'], metric='Speed', ax=ax)
plt.show()

# Speed delta analysis
fig, ax = plt.subplots(figsize=(16, 6))
viz.plot_speed_delta('VER', 'NOR', ax=ax)
plt.show()
```

## Project Structure

```
f1_tracker/
├── __init__.py       # Package initialization
├── main.py           # Interactive CLI application
├── data.py           # FastF1 data loading and caching
├── teams.py          # 2024 teams, drivers, and colors
├── timing_board.py   # Terminal-based timing displays
├── telemetry.py      # Telemetry visualization
└── track_map.py      # Circuit map visualization
```

## Tech Stack

- **FastF1** - Official F1 data library
- **Matplotlib** - Visualization
- **Rich** - Beautiful terminal output
- **Pandas/NumPy** - Data processing

## Skills Demonstrated

- Python data processing and visualization
- Working with motorsport telemetry data
- Object-oriented design
- CLI application development
- Understanding of F1 racing concepts

---

*Built with passion for Formula 1 and Mercedes HPP*
