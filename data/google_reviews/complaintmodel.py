# Split google reviews and trip advisor dataset according to rating
# 1-2: Bad, 3: Neutral, 4-5: Good (consider binary label)
# Possible implementation (classification) : Log reg (probability of complaint), DT (predicting potential complains), KNN
# Identify common keywords and phrases in negative reviews to determine frequent guest complaints
# Use review time to detect trend over different weekdays, time slots
# Categorize complaints into key themes (ride malfunctions, staff behavior, wait time, clash w other patrons)
# Create a metric that determines how risky certain complaints are and categorize it with threshold (0-0.3, 0.3-0.7, 0.7-1)
# Classify the causes of high risk complaints
# Determine ways to predict when/how it can happen
# Create prevention methods to PREVENT it from happening at all + if it actually happens what to do
# Pre-planning (schedule to split up the crowds) & Active response (emergency plan if shit happens)
# Link to iot? Helps with live data

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')

# Load your dataset (assuming a CSV file)
df = pd.read_excel('googlereviews5000.xlsx')

# Function to clean text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    tokens = word_tokenize(text)  # Tokenize words
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
    return ' '.join(tokens)

# Apply preprocessing
df['cleaned_review'] = df['review_text'].astype(str).apply(preprocess_text)
df.head()

from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# Compute sentiment scores
df['sentiment_score'] = df['cleaned_review'].apply(lambda x: sia.polarity_scores(x)['compound'])

# Classify sentiment based on score
df['sentiment_label'] = df['sentiment_score'].apply(lambda x: 'positive' if x > 0.05 else ('negative' if x < -0.05 else 'neutral'))

df[['review_text', 'sentiment_label']].head()

df['complaint'] = df['rating'].apply(lambda x: 1 if x <= 2 else 0 if x >= 4 else None)
df = df.dropna()  # Remove neutral ratings

# Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(df['cleaned_review'], df['complaint'], test_size=0.2, random_state=42)

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(max_features=5000)  # Limit vocab size
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Predictions
y_pred = model.predict(X_test_tfidf)

# Evaluate performance
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
