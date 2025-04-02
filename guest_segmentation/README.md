# Guest segmentation at Universal Studios Singapore (USS)

## Overview

Guest segmentation involves separating guests into groups based on various factors like demographics, preferences and behaviour. 
Guest segmentation is important as it allows businesses to make more personalised experiences for the guests, increasing guest satisfaction. In the long term, this helps with guest loyalty towards USS.

## Data Sources

Only data from our survey was used. There were a total of 171 respondents, 169 of whom have been to USS.

## Methodology

Acknowledging that our small data size would give rise to high variance, we used random forest, an ensemble method that reduces variance. 
Random forest was also used as we wanted to identify the top 5 factors influencing the spender type of the guests visiting USS.

### Data Preprocessing

1. Data Cleaning:

From our survey data, we identified the following variables that could be useful in guest segmentation: `frequency`,	`age`,	`gender`,	`monthly_income`,	`nationality`, `companion`,	`ride_intensity`,	`occasion`,	`spending_cat`. 
The data was then cleaned for each variable. 
As we only had information on the category (Transportation (e.g. Parking, taxi fares etc.), F&B, Merchandise) that our respondents spend the most on in USS, we decided to use this information to categorise the guests into `spender_type`. 
Those who spend most on transport are low spenders, those who spend most on f&b are average spenders and those who spend most on merchandise are high spenders.

2. Exploratory Data Analysis:
 
We then plotted bar graphs to visualise the relationship between each of our variables and spender type. Generally, we observe a majority of average spenders. 

![frequency](https://github.com/user-attachments/assets/10b43ddb-b64a-4fbf-add5-e9ff9a26690e)

Figure 1: Number of spender types based on the frequency that the respondents visit USS

![age](https://github.com/user-attachments/assets/dcf797e4-bf1b-4aa4-9159-7a2f7b57399e)

Figure 2: Number of spender types based on age of the respondents

![gender](https://github.com/user-attachments/assets/ab0b9980-1741-41d4-af5f-2b323fbe5c3b)

Figure 3: Number of spender types based on gender of the respondents

![monthly income](https://github.com/user-attachments/assets/7ecbe1c9-a70d-4870-9d0f-116c72a52d1d)

Figure 4: Number of spender types based on monthly income of the respondents

![nationality](https://github.com/user-attachments/assets/7a4e2e1e-9bd3-4ad4-b2e4-9c9bc11a3478)

Figure 5: Number of spender types based on nationality of the respondents

![companion](https://github.com/user-attachments/assets/4e3c0c78-ab13-4648-b777-0c1b342588c7)

Figure 6: Number of spender types based on the types of people that the respondents visit USS with (companion)

![ride_intensity](https://github.com/user-attachments/assets/53b911dc-b70d-443b-bf2b-45275143f27d)

Figure 7: Number of spender types based on the preferred ride intensity of the respondents

![occasion](https://github.com/user-attachments/assets/8a89951b-21c1-4968-a913-5190f5fbfc7d)

Figure 8: Number of spender types based on the occasion that the respondents choose to visit USS

We also grouped by each variable and counted the number of spender types for each unique value in the variables for further inspection of the data.

3. Feature Engineering:

To prepare the variables for the model, ordinal variables were label encoded while nominal variables were one-hot encoded. 

### Modeling Approach

* Training: The data was split into train and test set, where the train sets were used to train the RandomForestClassifier.
* Evaluation: We analysed the model in 2 ways, namely using the Gini importance of the trained model and the permutation importance using the test set of the model.
  The higher the Gini importance value, the more influential the factor is in predicting the spender type of the respondent. Permutation importance can be interpreted the same way.

### Key Findings:

![image](https://github.com/user-attachments/assets/8f5d58aa-450b-4ed0-9207-d401ba097700)
Comparing the Gini importance and permutation importance, we see that the top 5 influencing factors of spender types are `ride_intensity`, `age`, `gender`, `frequency` and `monthly_income`. 
Guests who are adults and visit theme parks fewer than once every year who prefer medium and high intensity rides are more likely to be high spenders. 

## Applications

Understanding the profile of guests and their preferences allow the business to make more informed decisions such as targeted marketing to encourage high spenders to visit USS more frequently and spend more. 
Allocation of resources can also be optimized by having different strategies for different segments of crowds (e.g.: on public holidays where people are more likely to visit USS with their family, arrange more staff at low intensity rides and attractions.)
