import ast
import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

base_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

def compute_post_engagement(df):
    """
    Computes engagement metrics for Instagram posts based on comments, likes, and sentiment analysis.

    This function performs the following operations:
    1. Calculates the number of comments for each post.
    2. Computes the average sentiment score of the comments using the VADER SentimentIntensityAnalyzer.
    3. Calculates an engagement score for each post based on the number of likes, comments, and sentiment score, using predefined weights.
    4. Saves the updated DataFrame, including the engagement metrics, to a CSV file.

    Parameters:
        df (DataFrame): The DataFrame containing Instagram post data, which includes the following columns:
            - `comments`: A string representation of a dictionary mapping users to their comments.
            - `num_likes`: The number of likes for each post.

    Returns:
        DataFrame: The updated DataFrame containing additional columns for:
            - `num_comments`: The number of comments for each post.
            - `sentiment`: The average sentiment score of comments for each post.
            - `engagement_score`: The computed engagement score for each post."
    """
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

def calculate_category_metrics(df):
    """
    Calculates aggregated metrics for specified content categories in the Instagram posts DataFrame.

    This function computes the following metrics for each category:
    - Total Likes
    - Total Comments
    - Total Sentiment Score
    - Total Engagement Score
    - Number of Posts (post count)

    It then calculates average values for Likes, Comments, Sentiment, and Engagement Score based on the number of posts in each category.

    Parameters:
        df (DataFrame): The DataFrame containing Instagram post data with the following relevant columns:
            - `num_likes`: Number of likes for each post.
            - `num_comments`: Number of comments for each post.
            - `sentiment`: Average sentiment score of comments for each post.
            - `engagement_score`: Engagement score for each post.
            - Categories: Boolean columns indicating the presence of specific marketing categories (e.g., `family_friendly`, `high_value`, etc.).

    Returns:
        None: This function does not return any value. It directly modifies the DataFrame and saves the aggregated metrics to a CSV file named `category_metrics.csv`."
    """
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
    category_df['avg_likes'] = round(category_df['total_likes'] / category_df['post_count'], 2)
    category_df['avg_comments'] = round(category_df['total_comments'] / category_df['post_count'], 2)
    category_df['avg_sentiment'] = round(category_df['total_sentiment'] / category_df['post_count'], 2)
    category_df['avg_engagement_score'] = round(category_df['total_engagement_score'] / category_df['post_count'], 2)

    category_df = category_df.drop(columns=["total_sentiment", "total_engagement_score", "total_likes", "total_comments"])

    category_df.to_csv(f"{base_dir}/category_metrics.csv", index=False)


if __name__ == "__main__":
    df = pd.read_csv(f"{base_dir}/uss_ig_classified.csv")
    df2 = compute_post_engagement(df)
    calculate_category_metrics(df2)
