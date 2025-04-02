import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#nltk.download('vader_lexicon')
#nltk.download('wordnet')
#nltk.download('stopwords')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.tree import DecisionTreeClassifier
import datetime
from sklearn.feature_extraction.text import CountVectorizer


# Import Google Reviews and Trip Advisor data
file_path_1 = "../data/google_reviews/google reviews cleaned df_text.xlsx"
file_path_2 = "../data/TripAdvisor_reviews/raw_data/tripadvisor.csv"
df1 = pd.read_excel(file_path_1)
df2 = pd.read_csv(file_path_2)

# Select specific columns we are interested in
df1 = df1[['rating', 'visited_on', 'review_text', 'original_language']]

df2 = df2[['Rating', 'Stay Date', 'Review Text', 'Language']]

# Ensure both datasets have consistent column names
df2 = df2.rename(columns = {'Rating' : 'rating',
                 'Review Text' : 'review_text',
                 'Language' : 'original_language'})

df2['Stay Date'] = pd.to_datetime(df2['Stay Date'])

df2['visited_on'] = df2['Stay Date'].apply(lambda x: "Weekend" if pd.notna(x) and x.weekday() >= 5 else "Weekday")

df2 = df2[['rating', 'visited_on', 'review_text', 'original_language']]

# Merging both data sets
df = pd.concat([df1, df2], ignore_index=True)

stop_words = set(stopwords.words('english'))
additional_words = {'universal', 'uss', 'studio', 'singapore', 'theme', 'park'}
stop_words.update(additional_words)
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """Lowercase, remove special characters, and extra spaces."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text) # Keep only alphanumeric characters
    text = re.sub(r'\s+', ' ', text).strip() # Remove extra spaces
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words] # Remove stopwords + Lemmatization
    return ' '.join(words)

df['review_text'] = df['review_text'].apply(clean_text)
df['is_english_speaker'] = df['original_language'].apply(lambda x: 1 if x == 'en' else 0)
df['visited_on'] = df['visited_on'].apply(lambda x: 0 if x == 'Weekday' else 1)
df['rating'] = pd.to_numeric(df['rating'])

sid = SentimentIntensityAnalyzer()

def get_sentiment(text):
    sentiment = sid.polarity_scores(text)
    return sentiment['compound']  # The compound score indicates overall sentiment

df['sentiment'] = df['review_text'].apply(get_sentiment)
df['sentiment_label'] = df['sentiment'].apply(lambda x: 'positive' if x >= 0.05 else ('negative' if x <= -0.05 else 'neutral'))
df['sentiment_label'].value_counts()


# Create bigrams for filtered reviews
vectorizer = CountVectorizer(ngram_range = (2,2))
negative_reviews = df[(df['sentiment_label'] == 'negative') | (df['rating'] <= 3)]['review_text']

# Create the term-document matrix for negative reviews
negative_ngrams = vectorizer.fit_transform(negative_reviews)

# Convert to a DataFrame
word_counts = pd.DataFrame(
    negative_ngrams.toarray(), 
    columns=vectorizer.get_feature_names_out()
)

# Sum the occurrences of each n-gram
word_frequencies = word_counts.sum().sort_values(ascending=False)

# Get the top N unigrams and bigrams
top_n = 10  # Change this number as needed
print("Most Common Words and Phrases:")
print(word_frequencies.head(top_n))

# Manually input high-risk keywords
high_risk_keywords = ['accident', 'injury', 'unsafe', 'dangerous', 'broken', 'malfunction', 'waste',
                        'sick', 'poisoning', 'crowded', 'long wait', 'unhygienic', 'fell', 'hurt',
                        'defective', 'improper', 'hazard', 'inadequate', 'negligence', 'danger', 'waiting',
                        'bad', 'terrible', 'disappointing', 'angry', 'wait', 'long', 'issue', 'technical'
                        ]

def engineer_features(df, keywords):
    featured_df = df.copy()

    # Create feature for review length (might indicate detail of complaint)
    featured_df['review_length'] = featured_df['review_text'].apply(lambda x: len(str(x).split()) if isinstance(x, str) else 0)
    
    for keyword in keywords:
        featured_df[f'has_{keyword}'] = featured_df['review_text'].apply(
            lambda x: 1 if isinstance(x, str) and keyword in x.lower() else 0
        )
    
    # Create a complaint keyword count feature
    featured_df['complaint_keyword_count'] = featured_df[[f'has_{keyword}' for keyword in keywords]].sum(axis=1)

    scalar = MinMaxScaler()
    
    # Remove certain reviews which are just empty space
    featured_df = featured_df[featured_df['review_length'] != 0]
    featured_df.reset_index(drop=True, inplace=True)


    # Weights for risk rating tabulation
    w = [0.7, 0.5, 0.3]

    featured_df['risk_rating'] = (w[0] * (5 - featured_df['rating'])) + (w[1] * (1-featured_df['sentiment'])) + (w[2] * (featured_df['complaint_keyword_count']/featured_df['review_length']))
    featured_df['risk_rating'] = scalar.fit_transform(featured_df[['risk_rating']]) 
    
    featured_df['risk_label'] = featured_df['risk_rating'].apply(lambda x: 'low' if x<0.3 else ('medium' if x<0.7 else 'high'))

    # Define features and target
    X = featured_df[['rating', 'visited_on', 'review_text', 'sentiment', 'is_english_speaker']]
    y = featured_df['risk_label']
    
    return X, y

# Engineer new features and split into predictors and target
X, y = engineer_features(df, high_risk_keywords)

# Initialise the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(max_features=3, stop_words='english')
text_vectors = tfidf_vectorizer.fit_transform(X['review_text'])

# Convert text vectors to dense array and create a DataFrame
text_df = pd.DataFrame(
            text_vectors.toarray(), 
            columns=[f'tfidf_feature_{i}' for i in range(text_vectors.shape[1])]
        )
# Fit and transform the cleaned review text
X_tfidf = pd.concat([X, text_df], axis = 1)
X_tfidf = X_tfidf.drop(columns=['review_text'])

# Split the data into training set and test set
X_tfidf_train, X_tfidf_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)


# Load Sentence-BERT model
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert embeddings to DataFrame
X_sbert = sbert_model.encode(X['review_text'].tolist())
X_sbert_df = pd.DataFrame(X_sbert, 
                          index = X.index,
                          columns=[f'sbert_feature_{i}' for i in range(X_sbert.shape[1])]
)

# Merge embeddings back with original data
X_sbert = pd.concat([X, X_sbert_df], axis = 1)
X_sbert = X_sbert.drop(columns = ['review_text'])

X_sbert_train, X_sbert_test, y_sbert_train, y_sbert_test = train_test_split(X_sbert, y, test_size=0.2, random_state = 43)

# Logistic Regression Model
def logs_regression(X_train, X_test, y_train, y_test):
# Split the data

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Evaluate model performance
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    # Display the classification report
    print(classification_report(y_test, y_pred))

# Decision Tree Model
def decision_tree(X_train, X_test, y_train, y_test):

    dt = DecisionTreeClassifier(max_depth=5)
    dt_model = dt.fit(X_train,y_train)
 
    print('Decision Tree accuracy for training set: %f' % dt_model.score(X_train, y_train))
    print('Decision Tree accuracy for test set: %f' % dt_model.score(X_test, y_test))

    return dt_model

# Testing both models on datasets with TF-IDF vectors and BERT embedding
tfidf_lr = logs_regression(X_tfidf_train, X_tfidf_test, y_train, y_test)

tfidf_dt = decision_tree(X_tfidf_train, X_tfidf_test, y_train, y_test)

sbert_lr = logs_regression(X_sbert_train, X_sbert_test, y_sbert_train, y_sbert_test)

sbert_dt = decision_tree(X_sbert_train, X_sbert_test, y_sbert_train, y_sbert_test)

# Helper function to apply feature engineering to new data
def process_guest_data(new_data, type):
    """
    Apply the same feature engineering to new data as was done during training
    """
    # Create a copy
    processed_df = new_data.copy()

    processed_df['review_text'] = processed_df['review_text'].apply(clean_text)

    time_now = datetime.datetime.now()

    processed_df['visited_on'] = (lambda x: 1 if x.weekday() >= 5 else 0)(time_now)

    processed_df['is_english_speaker'] = processed_df['original_language'].apply(lambda x: 1 if x == 'en' else 0)

    processed_df['sentiment'] = processed_df['review_text'].apply(get_sentiment)
    
    # Create feature for review length
    processed_df['review_length'] = processed_df['review_text'].apply(lambda x: len(str(x).split()) if isinstance(x, str) else 0)
    
    # Extract high-risk keywords
    high_risk_keywords = ['accident', 'injury', 'unsafe', 'dangerous', 'broken', 'malfunction', 'waste',
                        'sick', 'poisoning', 'crowded', 'long wait', 'unhygienic', 'fell', 'hurt',
                        'defective', 'improper', 'hazard', 'inadequate', 'negligence', 'danger', 'waiting',
                        'bad', 'terrible', 'disappointing', 'angry', 'wait', 'long', 'issue', 'technical',
                        'time', 'queue'
                        ]
    
    for keyword in high_risk_keywords:
        processed_df[f'has_{keyword}'] = processed_df['review_text'].apply(
            lambda x: 1 if isinstance(x, str) and keyword in x.lower() else 0
        )
    
    # Create a complaint keyword count feature
    processed_df['complaint_keyword_count'] = processed_df[[f'has_{keyword}' for keyword in high_risk_keywords]].sum(axis=1)

    
    output_df = processed_df[['rating', 'visited_on', 'sentiment', 'is_english_speaker']]

    if type == 'tfidf':
        # Initialise the TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(max_features=3, stop_words='english')

        text_vectors = tfidf_vectorizer.fit_transform(processed_df['review_text'])

        # Convert text vectors to dense array and create a DataFrame
        text_df = pd.DataFrame(
                    text_vectors.toarray(), 
                    columns=[f'tfidf_feature_{i}' for i in range(text_vectors.shape[1])]
        )

        result_df = pd.concat([output_df, text_df], axis = 1)

    elif type == 'bert':
        # Load Sentence-BERT model
        sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Convert embeddings to DataFrame
        X_sbert = sbert_model.encode(processed_df['review_text'].tolist())
        X_sbert_df = pd.DataFrame(X_sbert, 
                                columns=[f'sbert_feature_{i}' for i in range(X_sbert.shape[1])]
            )

        # Merge embeddings back with original data
        result_df = pd.concat([output_df, X_sbert_df], axis = 1)
        
    return result_df

# Try inputing new feedback data!
from langdetect import detect

rating = input("How satisfied is your experience at USS so far? On a scale of 1-5: ")
feedback_text = input("What seems to be the issue you're facing?: ")
language = detect(feedback_text)

raw_data = {
    "rating" : [rating],
    "review_text" : feedback_text,
    "original_language" : language
}

raw_data = pd.DataFrame(raw_data)
raw_data["rating"] = pd.to_numeric(raw_data["rating"], errors="coerce")


guest_data_tfidf = process_guest_data(raw_data, 'tfidf')
guest_data_bert = process_guest_data(raw_data, 'bert')


print(f"Risk Level by TFIDF Decision Tree : {tfidf_dt.predict(guest_data_tfidf)[0]}")
print(f"Risk Level by BERT Decision Tree : {sbert_dt.predict(guest_data_bert)[0]}")