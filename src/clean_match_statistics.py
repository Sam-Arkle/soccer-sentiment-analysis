import pandas as pd
import re
from datetime import datetime

def extract_match_info(details):
    # Regex to find the date in the string
    date_match = re.search(r'([A-Za-z]+-\d{1,2}-\d{4})', details)
    date = None
    if date_match:
        try:
            date = datetime.strptime(date_match.group(1), "%B-%d-%Y")
        except ValueError:
            try:
                date = datetime.strptime(date_match.group(1), "%b-%d-%Y")
            except:
                pass

    # Home or away and opponent extraction
    if details.startswith('Sheffield-United-'):
       # Home game: opponent is everything between 'Sheffield-United-' and the date
        pattern = r'Sheffield-United-(.+)-' + date_match.group(1)
        match = re.search(pattern, details)
        opponent = match.group(1) if match else ''
        home_away = 'home'
    else:
        # Away game
        opponent = details.split('-Sheffield-United-')[0]
        home_away = 'away'

    # Clean up opponent name (replace hyphens with spaces, strip)
    opponent = opponent.replace('-', ' ').strip()

    return pd.Series([date, opponent, home_away])

df = pd.read_csv('match_statistics.csv')
df[['date', 'opponent', 'home_away']] = df['Match Details'].apply(extract_match_info)
df.to_csv('match_statistics_cleaned.csv', index=False)