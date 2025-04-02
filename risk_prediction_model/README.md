# Predicting Guest Complaints and Service Recovery
## Part 1 : Build a predictive model to flag high-risk interactions using historical complaint data.
### Overview

As part of Business Question 9, we aimed to build a predictive model using historical complaint data to flag out high-risk interactions before they escalate into complaints.

--- 

## Data
### Google Reviews
Review data from USS Google reviews using web scrapping using Apify. The most recent 5000 reviews were retreived and is stored in ** `data/google_reviews/googlescrap5000` **.

### Trip Advisor Reviews
Review Data from USS Trip Advisor reviews using web scrapping. The data is stored in ** `data/TripAdvisor_reviews/tripadvisor.csv`** .

Both datasets will be cleaned and subsequently merged to become a combined reviews dataset with consistent features.

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
- The most common keywords are 'Express pass', 'Waiting time' and 'Roller coaster' through bigram analysis.
- This suggests that we can target our recommendation towards enhancing guest experience when queueing for attraction, reduce waiting time and improve attraction maintenance. This will be further discussed in part 2 of this business question.


### Business Insights
- An accurate high-risk detection model can alert USS staff to de-escalate potential incidents which can negatively impact guest satisfaction.
- Guest experience can be enhanced through receiving swift assistance from USS staff.
- Frequent high-risk feedback in concentrated areas can prompt USS operations to reallocate more staff to specific locations.
- The model can be implemented to a live feedback system to gain real-time guest feedback data to prevent further complaints.

### Future Improvements
- With new feedback data, the parameters for the model such as depth of decision tree and risk rating formula can be tuned to optimize high-risk detection for future predictions.
- Apply named entity recognition in order to extract the type of issue and location of issue from review data to improve staff reaction time.

## Part 2: Propose proactive interventions to address potential issues before complaints arise
Through the analysis of review data, we can devise solutions based on frequent guest complaints and live feedback data. The live feedback system will be included as part of our intended revamp of the USS mobile application.

### Common guest complaints
1. Long queues
2. Express pass is too expensive
3. Waiting time

## Proposed interventions
1. **Food & Beverage cart reallocation**
Given the mobile nature of food & beverage carts available around USS, they can be easily reallocated to specific locations to support high guest traffic. These high guest traffic can be tracked using the live feedback system based on guest feedback regarding "long queue" and "hot weather" conditions for queues that are located outdoors. This can help improve guest experience when they are queuing for attrations while also providing additional f&b sales revenue for USS.

2. **Utilization of portable seats**
For older and less physically mobile guests, they can alert staff using the live feedback system to request for portable seats for use in the queue. These portable seats will provide guest with the opportunity to rest while they are in the queue which helps improve their physical well-being. An example of the portable seat is show in the figure below. At the head of the queue, guests will be asked to return the portable seats back to USS staff. These low-cost seats are able to provide immediate relief for guests in longer queues and are portable such that they can be easily retracted and open for use at any location.

3. **Revamp of USS mobile application**
We intend to improve the following features for the USS mobile application: 
    **a. Current Queue progress**
        The current queue progress system will allow guests to view the waiting time for various attractions around USS to improve their path planning in USS. This will assist in guest to make more informed decision during their time in USS to reduce their time in queues and encourage guests to refrain from overcrowding in certain areas.

    **b. Virtual queueing system**
        The virtual queue system provide the option for guests to join a virtual queue for attractions without being physically present in the queue. Guests will be allocated a group number instead of a specific queue number to prevent late guests from cutting to the front of the queue. Guests of the same group number will be allowed into the attraction within a specific time frame. This function reduces the time guests are constraint in a physical queue which allows them to explore other segments of USS with more flexibility. The virtual queue will be in effect parallel to physical queues such that guests still have the option to enter the attraction faster in the physical queue.

    c. Guest location tracking and suggestions

    d. Personalized advertisement

    e. Dissemination information and navigation

    **f. Live feedback system**
        Utilizing the model from Part 1, guests will be able to provide immediate requests or feedback during their time in USS through the mobile app. These live data will be effective in alerting staff to assist guests and prevent potential high-risk interactions from guests. Guests will be allowed to provide feedback for attractions malfuction, insufficient utility allocation and food and beverage reviews. Visual signs will be placed at the entrance and exits of attractions, restaurants and popular locations in USS to prompt guest to provide feedback on their experience. This system will support the necessary proactive interventions by providing immediate alert to USS staff and ensure quick resolution and reduce guest dissatisfaction. 

Feature c-e are further explained under /sentiment_analysis/README.md/Recommendations

Guests will be prompted to install the USS application upon entering USS in order to enjoy these new personalized benefits, which will encourage guests to provide their location data to improve their overall experience in USS.

4. Personalized outreach
For guests with frequent high-risk feedback, they will be sent personalized communications such as proactive service offers and check-ins to ensure issues are resolved before they escalate. This initiative can reduce strong negative complaints by focusing on specific individuals or groups with high dissatisfaction rate in USS and assist USS staff in curating personalized solutions for them.

## Conclusion
### Key Insights
Through these interventions, supported by the revamped USS mobile application, we will be able to address the following issues:
- Strenuous experience when physically in long queue for attractions
- Long duration spent physically in queues
- Unresolved guest satisfaction due to lack of immediate feedback portal
- Overcrowding of guest in specific areas due to uninformed path planning

### Business Impact
With a more versatile mobile application, USS operations are able to more accurately monitor guest experience. Staff allocation can be optimized to assist in guests' needs, while food and beverage outlets will be able to increase revenue due to higher customer volume from personalized advertisements. These factors are able to improve customer retention by displaying USS' emphasis on customer satisfaction, while boosting revenue and receiving more data for future improvements.






