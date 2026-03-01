# NBA Data Visualization: Points vs Assists

This project uses Python to fetch live NBA player statistics for the current season and plots an interactive, dark-mode scatter plot of Points vs. Assists using `matplotlib`.

## Features

- **Live Data Fetching**: Pulls up-to-date stats directly from the NBA API (`nba_api`).
- **Interactive Scatter Plot**:
  - Highlights top scorers filtering players with >500 points.
  - Hover over a point to quickly see the player's name.
  - **Click** on a player's dot to open a rich, interactive details box containing:
    - Automatically downloaded high-res **Player Headshots** (via NBA CDN).
    - Transparent **Team Logos** serving as a watermark background (via ESPN CDN).
    - Key player stats (Games Played, Points, Assists, Rebounds, Steals, Blocks).
- **Responsive NBA Aesthetic**:
  - Full dark-mode theme designed to emulate official NBA broadcast analytics.
  - Uses `Impact` (or fallback Sans-Serif) font styling across the entire chart.
  - Pop-up stats box automatically stays perfectly centered regardless of window resizing.
- **Smart Caching**: Utilizes `requests-cache` to save downloaded player images locally, drastically speeding up interaction times after the first click.

## Prerequisites

- Python 3.9+
- `pip` package manager

## Installation

1. Clone this repository:

   ```bash
   git clone <your-repo-url>
   cd nba-data-viz
   ```

2. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Simply run the main script from your terminal:

```bash
python main.py
```

1. The script will fetch the current season's data and briefly print status messages.
2. A Matplotlib window will open displaying the plot.
3. **Hover** over any blue dot to see the player's name.
4. **Click** on a dot to view the full detailed statistics card for that player. Click another dot, or click off into empty space to hide it.
5. Upon closing the window, the base plot without interactions will be saved locally as `pts_vs_ast.png`.

## Customization

You can easily adjust the size of the popup box, text, and images by modifying the arguments near the bottom of `main.py`:

- Locate the `get_image()` calls inside `on_click` and change the `zoom=0.5` parameters to resize the headshots and team logos.
- Adjust `fontsize=11` in the `TextArea()` calls to change the size of the text within the popup.
