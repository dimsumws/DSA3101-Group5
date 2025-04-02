import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#nltk.download('stopwords')
#nltk.download('punkt')

# Import google reviews data
df = pd.read_excel('googlereviews5000.xlsx')

# Drop unnecessary columns and rename columns to ensure consistency
df = df.drop(columns = ['rating', 'reviewUrl', 'reviewerNumberOfReviews', 'title', 'likesCount', 'isAdvertisement', 'reviewerId'])
df.rename(columns= {'stars' : 'rating',
                    'reviewContext/Reservation recommended' : 'reservation_recommended',
                    'reviewContext/Visited on' : 'visited_on',
                    'reviewContext/Wait time' : 'wait_time',
                    'publishedAtDate' : 'published_date',
                    'isLocalGuide' : 'is_local_guide',
                    'originalLanguage' : 'original_language',
                    'textTranslated' : 'text_translated'}, inplace=True)


# Convert language feature to binary
df['review_text'] = df.apply(lambda row: row["text"] if row["original_language"] == "en" else row["text_translated"], axis = 1)
df = df.drop(columns = ["text", "text_translated"])

# Convert published date to datetime type
df['published_date'] = df['published_date'].str[:10]

df['published_date'] = pd.to_datetime(df['published_date'])

# Create new column to determine day of visit 
df['visited_on'] = df['published_date'].apply(lambda x: "Weekend" if pd.notna(x) and x.weekday() >= 5 else "Weekday")

# Split dataset into 2 separate datasets
# df_no_text contains all reviews with empty review texts
# df_text contains all reviews with non-empty review texts
df_no_text = df[df["review_text"].isna() | (df["review_text"].str.strip() == "")]
df_text = df[~df["review_text"].isna() & (df["review_text"].str.strip() != "")]

# Store new datasets into new excels
df_no_text.to_excel("google reviews cleaned df_no_text.xlsx", index = False)
df_text.to_excel("google reviews cleaned df_text.xlsx", index = False)