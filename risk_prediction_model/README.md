# Predicting Guest Complaints and Service Recovery
## Part 1 : Build a predictive model to flag high-risk interactions using historical complaint data.
### Overview

As part of Business Question 9, we aimed to build a predictive model using historical complaint data to flag out high-risk interactions before they escalate into complaints.

--- 

## Data
### Google Reviews

Review data from USS Google Reviews using web scrapping using Apify. The most recent 5000 reviews were retreived and is stored in ** `data/google_reviews/googlescrap5000` **.

### Trip Advisor Reviews
tbc tbc


## Methodology
### Data Preprocessing
1. Less useful columns are dropped.
2. One-hot encoding applied for categorical variables.
3. Dataset split to obtain all reviews with non-empty review text.
4. Removed stop words and applied lemmatization for review text.

### Data Analysis
Sentiment analysis is conducted on review texts to determine the emotional tone or opinion expressed in a piece of text and further classified into positive, negative and neutral based on pre-determined thresholds. 

### Feature Engineering
In order to prepare our data for model training, we created the following features.
1. Sentiment of review text.
2. Risk rating and corresponding risk label.
3. TD-IDF vectors with a maximum of 3 features.
4. BERT sentence embedding of review text.

### Modelling
- Machine Learning Models evaluated:
    - Logistic Regression
    - Decision Tree

- Evaluation metrics
    - Logistic Regression : Accuracy, Precision, Recall
    - Decision Tree : Cross-validation training accuracy and test accuracy

- Training and test data
    - Training data : 80% of total review data
    - Test data : 20% of total review data

- **Final Model:**
    - **Decision Tree with TF-IDF vectors** was selected due to:
        - Highest test set accuracy : 0.991686   
        - Outperformed logistics regression and both models using BERT sentence embedding

---

## Conclusion
### Key Insights
- Using decision tree with TF-IDT vectorization, the model was able to assign the correct risk label for unseen review data to very high accuracy.
- The most common keywords are 'Express pass', 'Waiting time' and 'Roller coaster'.
- This suggests that we can target our recommendation towards enhancing guest experience when queueing for attraction, reduce waiting time and improve attraction maintenance. This will be further discussed in part 2 of this business question.


### Business Insights
- An accurate high-risk detection model can alert USS staff to de-escalate potential incidents which can negatively impact guest satisfaction.
- Guest experience can be enhanced through receiving swift assistance from USS staff.
- Frequent high-risk feedback in concentrated areas can prompt USS operations to reallocate more staff to specific locations.
- The model can be implemented to a live feedback station to gain real-time guest feedback data.

## Part 2: Propose proactive interventions to address potential issues before complaints arise






