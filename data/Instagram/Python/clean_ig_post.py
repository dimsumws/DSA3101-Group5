import ast
import re
import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

base_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

def clean_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
   
   # Lowercase, remove extra spaces
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove stop words + lemmatisation
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)


def format_comments(comments):
    """Converts comments from a string to a list of dictonaries.
    """
    formatted_comments = []
    for c in comments:
        comments_list = ast.literal_eval(c)
        comments_dict = {}
        for user, comment in comments_list:
            if user not in comments_dict:
                comments_dict[user] = []
            comments_dict[user].append(clean_text(comment))
        formatted_comments.append(comments_dict)
    return formatted_comments


def clean_data(df, df2):
    df["post_date"] = pd.to_datetime(df["post_date"])
    df2["post_date"] = pd.to_datetime(df2["post_date"])
    df["caption"] = df["caption"].apply(clean_text)
    df["comments"] = format_comments(df["comments"])
    
    # Save to a new CSV file
    df.to_csv(os.path.join(base_dir, "cleaned_instagram_data.csv"), index=False)
    df2.to_csv(os.path.join(base_dir, "cleaned_instagram_stories.csv"), index=False)


if __name__ == "__main__":
    df = pd.read_csv(f"{base_dir}/uss_ig.csv")
    df2 = pd.read_csv(f"{base_dir}/uss_ig_stories.csv")
    clean_data(df, df2)
