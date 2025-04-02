import ast
import re
import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

base_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

def clean_text(text):
    """
    Preprocesses the input text by performing the following steps:
    
    1. Converts text to lowercase and removes extra spaces.
    2. Removes stop words to eliminate common but unimportant words.
    3. Applies lemmatisation to reduce words to their base form.
    
    Parameters:
        text (str): The input text string to be cleaned.
    
    Returns:
        str: The cleaned and processed text.
    """
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
    """
    Converts comments from a string representation into a list of dictionaries.
    
    Each comment entry is assumed to be a stringified list of tuples, where each 
    tuple contains a username and a corresponding comment. The function:
    
    1. Parses the string representation into an actual list using `ast.literal_eval`.
    2. Groups comments by user into a dictionary.
    3. Cleans each comment using `clean_text()` before storing it.
    4. Appends the resulting dictionary to a list.
    
    Parameters:
        comments (list of str): A list of stringified lists of (user, comment) tuples.
    
    Returns:
        list of dict: A list where each dictionary maps usernames to lists of their cleaned comments."
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
    """
    Cleans and preprocesses two DataFrames containing Instagram post data and story data.
    
    This function performs the following operations:
    1. Converts the `post_date` column in both DataFrames to datetime format.
    2. Cleans the `caption` column by applying the `clean_text` function to each caption.
    3. Formats the `comments` column into a list of dictionaries using the `format_comments` function.
    4. Saves the cleaned DataFrames to new CSV files named `cleaned_instagram_data.csv` and `cleaned_instagram_stories.csv`.
    
    Parameters:
        df (DataFrame): The DataFrame containing Instagram post data, which includes columns for `post_date`, `caption`, and `comments`.
        df2 (DataFrame): The DataFrame containing Instagram story data, which includes a `post_date` column.
    
    Returns:
        None: This function does not return any value. It directly modifies the input DataFrames and saves the cleaned data to CSV files.
    """
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
