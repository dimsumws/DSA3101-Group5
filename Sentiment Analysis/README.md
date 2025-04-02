# Sentiment Analysis on Tripadvisor Review data.

## Goal:

The goal is to do a sentiment analysis on the reviews from TripAdvisor regarding Universal Studios Singapore (USS). We hope to identify what guests liked and identify pain points that can be potentially tackled.

### Data Cleaning:

First, we read the file and dropped some less useful columns such as 'Review Id', 'User Avatar' and 'URL'. Then we removed non-English reviews. While there are existing packages that could translate these reviews to English, we have no means of verifying whether the translations would be accurate, and since we're doing sentiment analysis, where the choice of words would determine the emotional tone and attitudes expressed, we opted to remove non-English reviews.

### Data preprocessing (Text preprocessing):

The aim is to clean and standardise textual data for analysis. We applied the following techniques to the attributes Review Title and Review Text.

1. Remove special characters, numbers, and extra spaces.
    - This eliminates unnecessary noise from things like punctuation, symbols, and redundant whitespace. This helps to standardize text for ML models.

2. Convert text to lowercase.
    - Ensures consistency by eliminating case sensitivity and preventing the duplication of words due to different capitalizations. This helps match texts and reduces vocabulary size.


3. Tokenization and removing stopwords.
    - Removing stop words like "the", "is", "and", etc. that don’t add much meaning. This is to reduce text size once again.

4. Lemmatization.
    - Converts words to their base form to normalize the variations of the same word. This reduces vocabulary size and improves model generalisation.
  
### Exploratory Data Analysis:

Looking at the distribution of the guests' ratings, we get a preliminary idea of how the overall experience is perceived. We can see from the bar chart that the vast majority of guests rated their experience at least a 4 out of 5. We can then suspect that sentiment analysis will also reveal to be largely positive.  

## Sentiment Analysis

### VADER: 
We used VADER (Valence Aware Dictionary and Sentiment Reasoner) to perform the sentiment analysis. VADER is a vocabulary and rule-based feeling analysis instrument that was designed to be sensitive towards the way people communicate in web-based media. 

Every word in the vocabulary is appraised; more positive words will have a higher positive evaluation, and more negative words will have a more negative score.

Using this on our dataset, the reviews would be scored between -1 to 1 and categorized into the following categories:
- positive (score > 0.05) 
- neutral (-0.05 < score < 0.05)
- negative (score < -0.05)

### Reasoning:
Why do sentiment analysis when we already have a Rating column?
- To better capture emotional tone. For example, a high rating (eg 4 stars) may not mean the review is fully positive. Doing sentiment analysis will help detect nuanced opinions.
- To better handle Rating inconsistencies. Users might also perceive ratings differently from one another which makes the Rating attribute potentially inconsistent.

## Bigram Analysis

To better identify key themes in positive and negative feedback, we analyze common word pairs (bigrams) in positive and negative reviews to identify key phrases associated with sentiment. Here we extracted the top 20 for both positive and negative reviews. This will provide insights into common praises and common complaints of USS.

### Positive reviews:

The phrase "express pass" stands out prominently, suggesting that positive experiences are closely tied to a premium experience—specifically, the ability to skip lines by purchasing the Express Pass.

Additionally, phrases like "waiting time" indicate that guests prioritize a reasonable queuing experience, implying that the efficiency of wait times plays a significant role in their overall satisfaction.

Finally, the frequent mention of specific ride names highlights that the attractions themselves are key highlights of the visit, suggesting that customers value the quality and experience of the rides.


### Negative reviews:

"Express pass" appears frequently in negative reviews, suggesting that the service did not meet customer expectations. This likely reflects situations where guests felt the Express Pass did not significantly reduce wait times as anticipated. Additionally, given the higher cost of these passes, customers may have had high expectations for the service, only to be disappointed by the actual experience. This is further corroborated by the presence of phrases like "waiting time" and "waste of money", which indicate frustration with the perceived value. This underscores the importance of the queuing experience in determining overall customer satisfaction.

