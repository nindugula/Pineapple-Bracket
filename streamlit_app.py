import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide")

BASE_DIR = Path(__file__).parent
try:
    df = pd.read_csv(BASE_DIR / "picks.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Game", "Name", "Winner"])@st.cache_data
def load_data():
    try:
        df = pd.read_csv(BASE_DIR / "picks.csv")
        return df.drop(columns=["Unnamed: 0"], errors="ignore")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Game", "Name", "Winner"])

df = load_data()

st.title("🏀 March Madness Communal Bracket")

# -------------------------
# Build game_dict
# -------------------------
raw_game_dict = {}
for _, row in df.iterrows():
    game = row["Game"]
    name = row["Name"]
    winner = row["Winner"]
    
    # Initialize the game dictionary if it doesn't exist
    if game not in raw_game_dict:
        raw_game_dict[game] = {}
    
    # Group names by the team they picked to win
    raw_game_dict[game].setdefault(winner, []).append(name)

# Format the grouped dictionary into HTML strings for the tooltip
game_dict = {}
for game, winners in raw_game_dict.items():
    # Example format: "Duke: Nikhil, Nik, Jack"
    lines = [f"<strong>{winner}</strong>: {', '.join(names)}" for winner, names in winners.items()]
    game_dict[game] = "<br>".join(lines)
# -------------------------
# Helpers
# -------------------------
def get_region(game):
    return game.split()[0]

def get_round(game):
    return game.split()[1].split("-")[0]

def get_games(region, round_):
    return sorted([g for g in game_dict.keys() if get_region(g) == region and get_round(g) == round_])

def game_box(game):
    picks = game_dict.get(game, "No picks")
    return f"""
    <div class="game-container">
        <div class="game">
            {game}
            <div class="tooltip">{picks}</div>
        </div>
    </div>
    """

# -------------------------
# Build side regions + F4 inclusion
# -------------------------
def build_side_bracket(top_region, bottom_region, f4_game_key, mirrored=False):
    """
    Builds a half-bracket (East/South or West/Midwest) 
    plus the corresponding Final Four game.
    """
    html = f'<div class="side-container {"mirrored" if mirrored else ""}">'
    
    # The four standard rounds for the two regions
    html += '<div class="regions-column">'
    html += build_region(top_region, mirrored)
    html += build_region(bottom_region, mirrored)
    html += '</div>'
    
    # The Final Four column (aligns horizontally with the end of the regions)
    f4_game = [g for g in game_dict if f4_game_key in g]
    html += f'<div class="round f4-round">'
    for g in f4_game:
        html += game_box(g)
    html += '</div>'
    
    html += '</div>'
    return html

def build_region(region, mirrored=False):
    rounds = ["R1", "R2", "S16", "E8"]
    region_html = f'<div class="region {"mirrored" if mirrored else ""}">'
    for r in rounds:
        games = get_games(region, r)
        if mirrored: games = games[::-1]
        round_html = f'<div class="round {r.lower()}">'
        for g in games:
            round_html += game_box(g)
        round_html += '</div>'
        region_html += round_html
    region_html += '</div>'
    return region_html

# -------------------------
# Build center (Champ Only)
# -------------------------
def build_center():
    champ_games = sorted([g for g in game_dict if "Champ" in g])
    html = '<div class="center-column">'
    for g in champ_games:
        html += game_box(g)
    html += '</div>'
    return html

# -------------------------
# HTML + CSS
# -------------------------
html_content = f"""
<html>
<head>
<style>
    body {{
        font-family: 'Segoe UI', sans-serif;
        background: #0e1117;
        color: white;
        margin: 0;
        padding: 10px;
    }}

    .bracket {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 950px;
        min-width: 1400px;
    }}

    .side-container {{
        display: flex;
        flex: 3;
        height: 100%;
    }}
    
    .side-container.mirrored {{
        flex-direction: row-reverse;
    }}

    .regions-column {{
        display: flex;
        flex-direction: column;
        flex: 4;
    }}

    .region {{
        display: flex;
        flex: 1;
        height: 50%;
    }}

    .region.mirrored {{
        flex-direction: row-reverse;
    }}

    .round {{
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        flex: 1;
    }}

    .round.r1 {{ padding: 10px 0; }}
    
    .f4-round {{
        flex: 0.8; /* Keeps F4 column slightly narrower */
    }}

    .center-column {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        flex: 0.8;
        padding: 0 20px;
    }}

    .game-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
    }}

    .game {{
        position: relative;
        padding: 5px;
        width: 100px;
        height: 40px;
        border: 1px solid #444;
        border-radius: 4px;
        background: #046994;
        cursor: pointer;
        text-align: center;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .game:hover {{
        background: #2c3440;
        border-color: #ff4b4b;
    }}

    .tooltip {{
        display: none;
        position: absolute;
        top: 0;
        left: 110%;
        background: white;
        color: black;
        padding: 8px;
        border-radius: 4px;
        min-width: 140px;
        z-index: 100;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}

    .mirrored .tooltip {{
        left: auto;
        right: 110%;
    }}

    .game:hover .tooltip {{
        display: block;
    }}
</style>
</head>
<body>
    <div class="bracket">
        {build_side_bracket("East", "South", "F4-1", mirrored=False)}

        {build_center()}

        {build_side_bracket("West", "Midwest", "F4-2", mirrored=True)}
    </div>
</body>
</html>
"""

components.html(html_content, height=1000, scrolling=True)