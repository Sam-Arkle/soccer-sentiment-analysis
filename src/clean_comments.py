import pandas as pd
import re

def extract_team(team_str):
    # Example: "Pre-Match View From Leeds"
    match = re.search(r'Pre-Match View From (.+)', team_str, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return team_str.strip()

df = pd.read_csv('comments_with_sentiment.csv')
df['opponent'] = df['team'].apply(extract_team)
df['published_date'] = pd.to_datetime(df['published_date'])
df.to_csv('comments_with_sentiment_cleaned.csv', index=False)