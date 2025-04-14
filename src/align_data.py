# The purpose of this file is to combine the sentiment analysis/comment with the match data
import pandas as pd
from datetime import timedelta

# Load cleaned data
comments = pd.read_csv('comments_with_sentiment_cleaned.csv', parse_dates=['published_date'])
matches = pd.read_csv('match_statistics_cleaned.csv', parse_dates=['date'])

output_rows = []

TEAM_NAME_MAP = {
    'wolves': 'Wolverhampton Wanderers',
    'man city': 'Manchester City',
    'man utd': 'Manchester United',
    'spurs': 'Tottenham Hotspur',
    'qpr': 'Queens Park Rangers',
    'mk dons' : 'Milton Keynes Dons',
    'boro' : 'Middlesbrough',
    'crewe' : 'Crewe Alexandra'
    # Add more as needed
}

def normalize_team_name(comment):
    comment_lower = comment.lower().strip()
    return TEAM_NAME_MAP.get(comment_lower, comment)

for idx, comment in comments.iterrows():
    comment_date = comment['published_date']
    comment_team = normalize_team_name(str(comment['opponent']).lower())
    url = comment.get('url', 'N/A')
    sentiment = comment.get('sentiment', 'N/A')
    sentiment_score = comment.get('sentiment_score', 'N/A')
    comment_text = str(comment.get('comment', ''))[:20]

    # Find matches within 5 days after comment date
    mask = (matches['date'] >= comment_date) & (matches['date'] <= comment_date + timedelta(days=5))
    possible_matches = matches[mask]

    match_row = None
    team_flag = ''
    for _, match in possible_matches.iterrows():
        match_team = str(match['opponent']).lower().strip()
        comment_team_lc = comment_team.lower().strip()
        if comment_team_lc == match_team or comment_team_lc in match_team or match_team in comment_team_lc:
            match_row = match
            team_flag = ''
            break
    if match_row is None and not possible_matches.empty:
        # Debug print for mismatched teams
        print(f"CONFIRM TEAM: comment_team='{comment_team}' | match_team='{possible_matches.iloc[0]['opponent']}'")
        # Take the first match in range, but flag for confirmation
        match_row = possible_matches.iloc[0]
        team_flag = 'CONFIRM TEAM'
    elif match_row is None:
        # No match found at all
        match_row = pd.Series()
        team_flag = 'NO MATCH'

    output_rows.append({
        'url': url,
        'date': match_row.get('date', 'N/A'),
        'opposition_team': (match_row.get('opponent', 'N/A') if team_flag != 'NO MATCH' else 'N/A'),
        'comment_start': comment_text,
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'fouls_committed': match_row.get('Fouls Committed', 'N/A'),
        'yellow_cards': match_row.get('Yellow Cards', 'N/A'),
        'red_cards': match_row.get('Red Cards', 'N/A'),
        'tackles_won': match_row.get('Tackles Won', 'N/A'),
        'penalties_conceded': match_row.get('Penalties Conceded', 'N/A'),
        'team_flag': team_flag
    })

output_df = pd.DataFrame(output_rows)
output_df.to_csv('aligned_data.csv', index=False)

