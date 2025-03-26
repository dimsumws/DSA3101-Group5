import ast
import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

base_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

def compute_post_engagement(df):
    def compute_avg_sentiment(comments):
        comments = ast.literal_eval(comments)
        analyser = SentimentIntensityAnalyzer()
        if not comments:
            return 0
        sentiments = [analyser.polarity_scores(comment)['compound'] for comment in comments.values()]
        return sum(sentiments) / len(sentiments)
    
    df['num_comments'] = df['comments'].apply(lambda post_comments: len(ast.literal_eval(post_comments)))
    df['sentiment'] = df['comments'].apply(compute_avg_sentiment)

    # Define weights for engagement score
    alpha = 1  # Weight for likes
    beta = 2  # Weight for comments (since comments indicate deeper engagement)
    gamma = 50  # Weight for sentiment (scaled to have a significant impact)

    # Compute engagement score
    df['engagement_score'] = (
        alpha * df['num_likes'] + 
        beta * df['num_comments'] + 
        gamma * df['sentiment']
    )

    df.to_csv(f"{base_dir}/uss_ig_classified_sentiment.csv", index=False)
    return df


# idk if this should go into the same analysis script as the USJ, Tokyo Disney, Japan tourism script
def calculate_category_metrics(df):
    category_metrics = {}
    categories = ['family_friendly', 'high_value', 'influencer', 'halloween', 'festive', 'is_minion', 'deals_promotions', 'attraction_event']
    for _, row in df.iterrows():
        for cat in categories:
            if cat not in category_metrics:
                category_metrics[cat] = {'total_likes': 0, 'total_comments': 0, 'total_sentiment': 0, 'post_count': 0, 'total_engagement_score': 0}

            if row[cat]:
                category_metrics[cat]['total_likes'] += row['num_likes']
                category_metrics[cat]['total_comments'] += row['num_comments']
                category_metrics[cat]['total_sentiment'] += row['sentiment']
                category_metrics[cat]['total_engagement_score'] += row['engagement_score']
                category_metrics[cat]['post_count'] += 1
                
    
    # Convert to DataFrame
    category_df = pd.DataFrame.from_dict(category_metrics, orient='index')
    category_df.insert(0, 'category', categories)
    category_df['avg_likes'] = category_df['total_likes'] / category_df['post_count']
    category_df['avg_comments'] = category_df['total_comments'] / category_df['post_count']
    category_df['avg_sentiment'] = category_df['total_sentiment'] / category_df['post_count']
    category_df['avg_engagement_score'] = category_df['total_engagement_score'] / category_df['post_count'] 

    category_df.to_csv(f"{base_dir}/category_metrics.csv", index=False)


if __name__ == "__main__":
    df = pd.read_csv(f"{base_dir}/uss_ig_classified.csv")
    df2 = compute_post_engagement(df)
    calculate_category_metrics(df2)
