import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox, VPacker, HPacker, TextArea
import requests
import requests_cache
from io import BytesIO
from PIL import Image
from nba_api.stats.endpoints import leaguedashplayerstats

# Setup requests cache to avoid redownloading images repeatedly
requests_cache.install_cache('nba_image_cache', expire_after=86400)

def get_nba_data():
    """Fetch player stats for the current season."""
    print("Fetching NBA data...")
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26')
    df = player_stats.get_data_frames()[0]
    return df

def get_image(url, zoom=1.0):
    """Fetch an image from a URL and return an OffsetImage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.nba.com/'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Convert the image to RGBA to prevent matplotlib from applying
        # its default colormap (viridis) to grayscale or indexed palette images.
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return OffsetImage(img, zoom=zoom)
    except Exception as e:
        print(f"Error loading image {url}: {e}")
        return None

def plot_points_vs_assists(df):
    """Create an interactive scatter plot of Points vs Assists."""
    print("Generating plot...")
    
    top_players = df[df['PTS'] > 500].reset_index(drop=True)
    # Enable dark mode
    plt.style.use('dark_background')
    
    # Apply global font styling for the axes labels and ticks
    plt.rcParams['font.family'] = 'sans-serif'
    # Try generic sans-serif first to let 'Impact' fall back on Windows if needed, 
    # but explicitly request Impact/Arial Black for the actual labels.
    nba_fontprops = {'family': 'sans-serif', 'name': 'Impact'}
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set dark gray backgrounds
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#363636')
    
    # Create the scatter plot - Blue Plot Points, White edges
    scatter = ax.scatter(top_players['AST'], top_players['PTS'], 
                         color='deepskyblue', alpha=0.8, edgecolors='white', 
                         s=60, picker=5) # picker=5 allows interacting within 5 pixels
    
    # Apply font properties to titles and labels
    plt.title('NBA Players: Points vs. Assists (Current Season)', fontdict={**nba_fontprops, 'size': 18, 'color': 'white'}, pad=20)
    plt.xlabel('Total Assists', fontdict={**nba_fontprops, 'size': 14, 'color': 'white'})
    plt.ylabel('Total Points', fontdict={**nba_fontprops, 'size': 14, 'color': 'white'})
    
    # White Grid lines
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    
    # Make spines white
    for spine in ax.spines.values():
        spine.set_color('white')
        
    ax.tick_params(colors='white', labelsize=11)
    # Set tick labels to use the font as well
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname('Impact')
    plt.tight_layout()
    
    # Save base plot
    plt.savefig('pts_vs_ast.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print("Plot saved as 'pts_vs_ast.png'")
    
    # === Interactivity Logic ===
    
    # 1. Hover Annotation setup (simple text)
    annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.5", fc="#1e1e1e", ec="white", alpha=0.9),
                        color="white", zorder=5)
    annot.set_visible(False)
    
    # Track the active click annotation box
    active_details_ab = None
    
    def update_annot(ind):
        idx = ind["ind"][0]
        pos = scatter.get_offsets()[idx]
        annot.xy = pos
        player_name = top_players.iloc[idx]['PLAYER_NAME']
        annot.set_text(player_name)
        
        xlim = ax.get_xlim()
        if pos[0] > (xlim[0] + xlim[1]) / 2:
            annot.set_position((-10, 10))
            annot.set_ha('right')
        else:
            annot.set_position((10, 10))
            annot.set_ha('left')
        
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
                    
    # 2. Click Event Setup (Show rich details with images)
    def on_click(event):
        nonlocal active_details_ab
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            
            # Clear previous details box if it exists
            if active_details_ab:
                for item in active_details_ab:
                    try:
                        item.remove()
                    except (ValueError, AttributeError, NotImplementedError):
                        pass
                active_details_ab = [] # Reset the list
                fig.canvas.draw_idle()
                
            if cont:
                player_idx = ind["ind"][0]
                player_data = top_players.iloc[player_idx]
                
                player_id = player_data['PLAYER_ID']
                # team_id = player_data['TEAM_ID'] # Not used directly in the new UI
                
                # Image URLs pattern
                headshot_url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
                team_abbr = player_data.get('TEAM_ABBREVIATION', '').lower()
                logo_png_url = f"https://a.espncdn.com/i/teamlogos/nba/500/{team_abbr}.png"
                
                # Fetch images - ADJUST SIZES HERE
                headshot_img = get_image(headshot_url, zoom=0.5) 
                logo_img = get_image(logo_png_url, zoom=0.35) # Scaled down to fit behind text nicely
                
                if logo_img:
                    # Apply transparency directly to the logo image
                    logo_img.set_alpha(0.25)
                    
                # NBA Font Stying Setup
                # 'Impact' or 'Arial Black' often closely matches sports typography without requiring external OTF/TTF files.
                nba_fontprops = {'family': 'sans-serif', 'name': 'Impact', 'color': 'white'}
                stat_fontprops = {'family': 'sans-serif', 'weight': 'bold', 'color': 'white'}
                
                # 1. Overlay Background Logo
                # Positioned slightly offset to coordinate it behind the actual popup text
                # By using the exact same anchor point (0.02, 0.96) and a fixed point offset, 
                # it stays beautifully centered inside the box even when resizing the window
                bg_logo_ab = AnnotationBbox(
                    logo_img if logo_img else TextArea(""), 
                    (0.02, 0.96), xycoords='axes fraction', # Anchor to the exact same point as main box
                    xybox=(135, -95), boxcoords="offset points", # Fixed pixel push into the center of the UI box
                    box_alignment=(0.55, 0.45), # Center the logo at this visual offset
                    frameon=False, # No border
                    zorder=9     # Just behind the main content (zorder=10)
                )
                    
                # 2. Setup Player Name+Team (Rounded Container under image)
                name_str = f"{player_data.get('PLAYER_NAME', 'Unknown').upper()}"
                team_str = f"{player_data.get('TEAM_ABBREVIATION', 'N/A')}"
                
                name_area = TextArea(name_str, textprops={**nba_fontprops, 'fontsize': 14})
                team_area = TextArea(team_str, textprops={**nba_fontprops, 'fontsize': 12, 'color': 'lightgray'})
                
                # Wrap name and team inside a distinct vertical packer with a padded background
                title_box = VPacker(children=[name_area, team_area], align="center", pad=5, sep=2)
                
                # Wrap it all using AnnotationBbox-like styling (by using an actual drawing patch when rendered)
                # To simulate a rounded container in pure HPacker, we just assemble it vertically under the image column
                left_col_items = []
                if headshot_img:
                    left_col_items.append(headshot_img)
                left_col_items.append(title_box)
                
                left_col = VPacker(children=left_col_items, align="center", pad=0, sep=5)
                
                # 3. Setup Text Stats Column (Right side)
                stats_str = (
                    f"GP:   {player_data.get('GP', 0)}\n"
                    f"PTS:  {player_data.get('PTS', 0)}\n"
                    f"AST:  {player_data.get('AST', 0)}\n"
                    f"REB:  {player_data.get('REB', 0)}\n"
                    f"STL:  {player_data.get('STL', 0)}\n"
                    f"BLK:  {player_data.get('BLK', 0)}"
                )
                
                # Setup text field - ADJUST TEXT SIZE HERE
                text_box = TextArea(stats_str, textprops={**stat_fontprops, 'fontsize': 11, 'linespacing': 2.0})
                
                # 4. Final Layout Packing
                # Left Col (Image over Name container), Right Col (Stats)
                content = HPacker(children=[left_col, text_box], align="center", pad=15, sep=20)
                
                # Render the foreground content box
                # Force a semi-transparent black background so the logo barely bleeds through
                ab = AnnotationBbox(
                    content, 
                    (0.02, 0.96), xycoords='axes fraction',
                    box_alignment=(0, 1), 
                    bboxprops=dict(boxstyle="round,pad=0.8", fc="#111111", ec="deepskyblue", lw=1.5, alpha=0.85),
                    zorder=10
                )
                
                # Add background team logo FIRST, then the content box OVER it
                active_details_ab = [
                    ax.add_artist(bg_logo_ab),
                    ax.add_artist(ab)
                ]
                fig.canvas.draw_idle()

            else:
                # If clicked outside any dot, hide the details box
                if active_details_ab:
                    for item in active_details_ab:
                        try:
                            item.remove()
                        except ValueError:
                            pass
                    active_details_ab = [] # Reset the list
                    fig.canvas.draw_idle()

    # Register events
    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.canvas.mpl_connect("button_press_event", on_click)
    
    # Display the interactive plot
    plt.show()

if __name__ == "__main__":
    nba_df = get_nba_data()
    plot_points_vs_assists(nba_df)
