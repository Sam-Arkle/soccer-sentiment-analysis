# The function of this script is to take the aligned commments and match 
# data and to get it on a per match basis for running through the model.
import pandas as pd

df = pd.read_csv('aligned_data_v2.csv')

# Clean up any extra spaces in sentiment
df['sentiment'] = df['sentiment'].str.strip()

# Group and aggregate
grouped_df = df.groupby(['date', 'opposition_team']).agg(
    # sentiment_score_mean=('sentiment_score', 'mean'),
    # sentiment_score_std=('sentiment_score', 'std'),
    # sentiment_score_min=('sentiment_score', 'min'),
    # sentiment_score_max=('sentiment_score', 'max'),
    sentiment_dist=('sentiment', lambda x: x.value_counts(normalize=True).to_dict()),
    # comments=('comment_start', list), This takes up a lot of space
    comment_count=('comment_start', 'count'),
    Winner=('Winner', 'first'),
    sheff_utd_goals=('Sheffield United Goals', 'first'),
    opp_goals=('Opponent Goals', 'first'),
    sheff_utd_yellow=('Sheffield United Yellow Cards', 'first'),
    opp_yellow=('Opponent Yellow Cards', 'first'),
    sheff_utd_red=('Sheffield United Red Cards', 'first'),
    opp_red=('Opponent Red Cards', 'first'),
    sheff_utd_fouls=('Sheffield United Fouls Committed', 'first'),
    opp_fouls=('Opponent Fouls Committed', 'first')
)

# Flatten column names
grouped_df.columns = ['_'.join(col).strip() for col in grouped_df.columns]
grouped_df = grouped_df.reset_index()

# Save to CSV if needed
grouped_df.to_csv("grouped_match_data.csv", index=False)
