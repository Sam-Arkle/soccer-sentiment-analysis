# The function for analysing the fan sentiment on a per comment basis 

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd

# Load tokenizer and model
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Create sentiment pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    truncation=True,
    padding=True,
    max_length=512
)


label_map = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

#  Loading the comments 
df = pd.read_csv("comments.csv", skiprows=1, names=["team", "url", "published_date", "comment"])

# Example usage
# comments = [
#     "I think either way we will get brushed aside.",
#     "Sheffield are the most overrated team in this league.",
#     "Just watched the Spurs/Blades match. Sheffield have never stopped running all night."
# ]

results = sentiment_pipeline(df["comment"].tolist(), truncation=True, batch_size=32)

# Add sentiment results to the DataFrame
df["sentiment"] = [label_map[result["label"]] for result in results]
df["sentiment_score"] = [result["score"] for result in results]

df.to_csv("comments_with_sentiment.csv", index=False)

# # Output example
# for comment, result in zip(comments, results):
#     print(f"{comment}\n → {result['label']} (score: {result['score']:.3f})\n")
 