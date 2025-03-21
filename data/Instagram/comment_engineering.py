import ast
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def comments_sentiment_analysis(df):
    def compute_avg_sentiment(comments):
        comments = ast.literal_eval(comments)
        analyser = SentimentIntensityAnalyzer()
        if not comments:
            return 0
        sentiments = [analyser.polarity_scores(comment)['compound'] for comment in comments.values()]
        return sum(sentiments) / len(sentiments)
    
    df['sentiment'] = df['comments'].apply(compute_avg_sentiment)
    df.to_csv("uss_ig_classified_sentiment.csv", index=False)


# idk if this should go into the same analysis script as the USJ, Tokyo Disney, Japan tourism script
def calculate_category_metrics(df):
    category_metrics = {}
    categories = ['family_friendly', 'high_value', 'influencer', 'halloween', 'festive', 'deals_promotions', 'attraction_event']
    for _, row in df.iterrows():
        for cat in categories:
            if cat not in category_metrics:
                category_metrics[cat] = {'total_likes': 0, 'total_sentiment': 0, 'post_count': 0}

            if row[cat]:
                category_metrics[cat]['total_likes'] += row['num_likes']
                category_metrics[cat]['total_sentiment'] += row['sentiment']
                category_metrics[cat]['post_count'] += 1
    
    # Convert to DataFrame
    category_df = pd.DataFrame.from_dict(category_metrics, orient='index')
    category_df['avg_likes'] = category_df['total_likes'] / category_df['post_count']
    category_df['avg_sentiment'] = category_df['total_sentiment'] / category_df['post_count']

    return category_df


if __name__ == "__main__":
    df = pd.read_csv("uss_ig_classified.csv")
    comments_sentiment_analysis(df)
