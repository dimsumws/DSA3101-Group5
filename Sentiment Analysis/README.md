# IoT Data Integration for Experience Optimization

## Process:

The goal is to do a sentiment analysis on the reviews from TripAdvisor regarding Universal Studios Singapore (USS) to identify guests' common praises and pain points that can be potentially tackled by IoT solutions.

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

### Competitors analysis:

Now, we consider existing solutions that are in place in the tourism industry. Firstly, Disneyland allows users to queue for attractions and rides virtually on the Disneyland app. (Walt Disney World Resort, n.d.). This is important as it allows guests to enjoy other experiences while queueing, which lowers the perceived time wasted on queues, increasing satisfaction. Next, consider hotels such as the Marriott hotel, which uses internet-connected devices. For example, guests are tracked to ensure they do not enter restricted premises. Also, using their in-house application, the guests can interact with various features in their hotel room, such as climate control. Vitally, guests are also able to see relevant information such as checkout time.

### Current limitations:

Before presenting our recommendations, we believe it is vital to first highlight the shortcomings of IoT solutions at USS, specifically the USS application. Currently, the USS application lacks in terms of information disseminated to the guests. For instance, as seen in the image below, the application currently only shows the rough location of their rides, shows, dining places, etc. However, it does not show the users' current location, which makes navigation via the application challenging.

![image](https://github.com/user-attachments/assets/63f2de1c-b440-4858-b6f1-558d122dd8fe)


Secondly, as seen from the image below, while the application shows the estimated queueing time for their rides, it does not show guests the current progress when they are inside the queue. Furthermore, there does not exist a virtual queuing feature. 

![Screenshot 2025-04-02 191642](https://github.com/user-attachments/assets/7814efcf-18f6-4768-abf6-0d20dca34843)

### Business impact:

Guest satisfaction is closely tied to the queues, costs and ride experiences. According to queue theory, poor queue management could cost businesses due to customers’ perceived trade-offs. As customers get frustrated, they are less likely to spend and return, potentially resulting in a loss of revenue for USS. Hence, to retain loyalty and increase spending, the park can consider adopting strategies to make queues more bearable and forgettable. (Zhou & Soman, 2003) 

### Recommendations:

The park can utilise the existing USS app to adopt features such as:
* Current Queue progress
* Virtual queueing system
* Guest location tracking and suggestions. This allows for the park to identify overcrowded areas and redirect visitors with notifications (eg “Transformers currently have low wait times”)
* Dissemination information and navigation (eg “The UV index is now 3-5, it is recommended that you apply sunscreen”/ “The chance of raining is 67%, the nearest shelter is at …”)


![USS prototype](https://github.com/user-attachments/assets/c75aa543-0778-4df1-b3e5-f9bc34e08bd4)



### References:
Virtual Queues | Walt Disney World Resort. (n.d.). https://disneyworld.disney.go.com/guest-services/virtual-queue/


