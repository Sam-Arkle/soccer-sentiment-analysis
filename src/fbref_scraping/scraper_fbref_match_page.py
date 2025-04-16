import requests
from bs4 import BeautifulSoup

def get_team_blocks(scorebox):
    """Extract team blocks from the scorebox."""
    return [
        div for div in scorebox.find_all('div', recursive=False)
        if div.find('strong') and div.find('strong').find('a')
    ]

def get_team_name_and_score(team_block):
    """Extract team name and score from a team block."""
    name = team_block.find('strong').find('a').get_text(strip=True)
    score_div = team_block.find('div', class_='score')
    try:
        score = int(score_div.get_text(strip=True)) if score_div else None
    except Exception:
        score = None
    return name, score

def assign_sheffield_and_opponent(team1, score1, team2, score2):
    """Assign Sheffield United and opponent names and scores."""
    if team1 == "Sheffield United":
        return team1, score1, team2, score2
    else:
        return team2, score2, team1, score1

def extract_stats_from_caption(caption):
    """Extract summary stats from a player stats table caption."""
    table = caption.find_parent('table')
    tfoot = table.find('tfoot')
    if not tfoot:
        return None
    summary_row = tfoot.find('tr')
    if not summary_row:
        return None

    stats = {}
    stat_keys = [
        ('Yellow Cards', 'cards_yellow'),
        ('Red Cards', 'cards_red'),
        ('Fouls Committed', 'fouls'),
        ('Tackles Won', 'tackles_won'),
        ('Penalties Conceded', 'pens_conceded')
    ]
    for label, data_stat in stat_keys:
        td = summary_row.find('td', {'data-stat': data_stat})
        stats[label] = td.get_text(strip=True) if td else "N/A"
    return stats

def find_player_stats_captions(soup):
    """Find captions for Sheffield Utd and opponent player stats tables."""
    captions = soup.find_all('caption')
    sheff_caption = None
    opp_caption = None
    for caption in captions:
        text = caption.get_text(strip=True)
        if text == "Sheffield Utd Player Stats Table":
            sheff_caption = caption
        elif text.endswith("Player Stats Table") and text != "Sheffield Utd Player Stats Table":
            opp_caption = caption
    return sheff_caption, opp_caption

def scrape_fbref_match_page(url, session=None, html=None):
    """Print match info to the console (manual/interactive use)."""
    if html is None:
        if session is None:
            session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0"}
        response = session.get(url, headers=headers, timeout=50)
        if response.status_code != 200:
            print(f"Failed to retrieve {url} with status code {response.status_code}")
            return
        soup = BeautifulSoup(response.content, 'html.parser')
    else:
        soup = BeautifulSoup(html, 'html.parser')

    scorebox = soup.find('div', class_='scorebox')
    if not scorebox:
        print("Scorebox not found.")
        return

    team_blocks = get_team_blocks(scorebox)
    if len(team_blocks) < 2:
        print("Could not find both teams in scorebox.")
        return

    team1_name, team1_score = get_team_name_and_score(team_blocks[0])
    team2_name, team2_score = get_team_name_and_score(team_blocks[1])

    sheff_name, sheff_goals, opp_name, opp_goals = assign_sheffield_and_opponent(
        team1_name, team1_score, team2_name, team2_score
    )

    # Determine winner
    if sheff_goals is not None and opp_goals is not None:
        if sheff_goals > opp_goals:
            winner = sheff_name
        elif opp_goals > sheff_goals:
            winner = opp_name
        else:
            winner = "Draw"
    else:
        winner = "Unknown"

    print(f"{sheff_name} {sheff_goals} - {opp_goals} {opp_name}")
    print(f"Winner: {winner}")

    # Extract summary stats from the correct tables
    sheff_caption, opp_caption = find_player_stats_captions(soup)

    if sheff_caption:
        sheff_stats = extract_stats_from_caption(sheff_caption)
        print(f"\nStats for {sheff_name}:")
        print(f"  Goals: {sheff_goals}")
        for k, v in sheff_stats.items():
            print(f"  {k}: {v}")
    else:
        print(f"{sheff_name} Player Stats Table not found.")

    if opp_caption:
        opp_stats = extract_stats_from_caption(opp_caption)
        print(f"\nStats for {opp_name}:")
        print(f"  Goals: {opp_goals}")
        for k, v in opp_stats.items():
            print(f"  {k}: {v}")
    else:
        print(f"{opp_name} Player Stats Table not found.")

def get_fbref_match_data(url, session=None):
    """Return match data as a dictionary for use in other scripts."""
    if session is None:
        session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.get(url, headers=headers, timeout=50)
    if response.status_code != 200:
        print(f"Failed to retrieve {url} with status code {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    scorebox = soup.find('div', class_='scorebox')
    if not scorebox:
        print("Scorebox not found.")
        return None

    team_blocks = get_team_blocks(scorebox)
    if len(team_blocks) < 2:
        print("Could not find both teams in scorebox.")
        return None

    team1_name, team1_score = get_team_name_and_score(team_blocks[0])
    team2_name, team2_score = get_team_name_and_score(team_blocks[1])

    sheff_name, sheff_goals, opp_name, opp_goals = assign_sheffield_and_opponent(
        team1_name, team1_score, team2_name, team2_score
    )

    # Determine winner
    if sheff_goals is not None and opp_goals is not None:
        if sheff_goals > opp_goals:
            winner = sheff_name
        elif opp_goals > sheff_goals:
            winner = opp_name
        else:
            winner = "Draw"
    else:
        winner = "Unknown"

    sheff_caption, opp_caption = find_player_stats_captions(soup)
    sheff_stats = extract_stats_from_caption(sheff_caption) if sheff_caption else {}
    opp_stats = extract_stats_from_caption(opp_caption) if opp_caption else {}

    return {
        "sheffield_united": {
            "team": sheff_name,
            "goals": sheff_goals,
            **(sheff_stats if sheff_stats else {})
        },
        "opponent": {
            "team": opp_name,
            "goals": opp_goals,
            **(opp_stats if opp_stats else {})
        },
        "winner": winner
    }

if __name__ == "__main__":
    # For local HTML testing:
    with open(r"c:\Coding\soccer_scrape\mathref.html", encoding="utf-8") as f:
        html = f.read()
        scrape_fbref_match_page("local", html=html)