# Customer Satisfaction Analysis

## Overview
This explores customer satisfaction at Universal Studios Singapore (USS) touchpoints, and how satisfaction may consequently affect customer loyalty to USS.
**File:** `customer_satisfaction_analysis.py`

## Data and Methods

### 1. Survey Data Collection
 - Survey questions answering customer satisfaction and loyalty used a 7-point Likert Scale: A 7-point scale allows us to use NPS and CSAT metrics without overwhelming respondents with too few or too many options
 - Used qualitative responses of deterrent factors at USS

### 2. Metrics and Visualisations 
 - Visualised distribution of Likert Scale responses, and qualitative responses
 - Used Customer Satisfaction (CSAT) and Net Promoter Score (NPS) metrics

## Analysis
### Visualisation of Scale Responses
![image](https://github.com/user-attachments/assets/ae105f4d-ecad-477b-9e51-abb75becdc0e)
The distribution for 3 points relating to fee pricing, queue times and express passes have a distribution skewed towards the lower end. This will be reflected when using the CSAT metric.

### Customer Satisfaction Metirc (CSAT)
For the CSAT, we define:
Satisfied responses = Ratings 5, 6, or 7
Neutral = Rating 4
Dissatisfied = Ratings 1, 2, or 3

Our percentages for CSAT are as follows:

get_ticket         80.0<br>
fee_pricing        29.0<br>
queuing            25.0<br>
fast_pass_worth    36.0<br>
cleanliness        88.0<br>
facilities         81.0<br>
navigation         81.0<br>
rides              84.0<br>
theme              84.0<br>
relavamce          79.0<br>
staffing           83.0<br>
friendliness       84.0

For the CSAT, scores from 75%-85% and above are considered "good" and anything below needs improvement.
These points relate to wait times/queues, pricing, and the current solution to long wait-times (fastpass). This suggests a disatisfaction with these touchpoints, which could be factors, additionaly, compromising customer loyalty.

### Net Promoter Score (NPS)
Using a Net Promoter Score Metric, we define for our 7-point scale:
Detractors (Score of 1-3 included): unlikely to recommend to others, could actively discourage future customers; Unhappy
Passives (Score of 4-5): tends not to actively promote the brand, but will not damage it either.
Promoters (Score of 6-7): most enthusiastic and loyal customers, likely to act as brand ambassadors; Highly Satisfied

NPS Score Range: -100 to 100

Positive NPS → More promoters than detractors → Good customer loyalty
Negative NPS → More detractors than promoters → Needs improvement
0-50 NPS → Neutral
Above 50 → Excellent

We calculated a neutral NPS score of 43, indicating that visitors to Universal Studios are unlikely to promote the brand to others.

### Qualitative Responses
![image](https://github.com/user-attachments/assets/713ee3a3-6f22-45fb-80fd-f9b4e1633721)
Using qualitative responses of survey respondents answering the question "What dissuades you from wanting to visit a theme park?", we can see from the bar chart that long wait times have the highest percentages. This, along with our CSAT metric show that customer disatisfaction with wait times and costs indeed could affect customer loyalty, therefore explaing our low NPS score.

### Insights
The CSAT scores demonstrate to us low satisfaction at 2 main touchpoints, queue times and costs and at the express pass solution. Using the CSAT along with qualitative responses which suggest that deterents to visiting are mainly wait-times/crowds and costs, we see that dissatisfaction at these touchpoints are major areas which can affect customer loyalty.
Indeed, from analysis of the NPS,inicates that Universal Studios Singapore has lower customer loyalty and its visitors are more unlikely to return. 
Indeed, in answering another buisiness question: Predicting Guest Complaints and Service Recovery sentiment analysis supports our findings.

In order to address these issues, we could explore these solutions:
- Provide better solutions to queue/wait-times like virtual lines to improve customer satisfaction and loyalty, as express passes currently provided are percieved by visitors as "not worth it", suggesting that it is not effective enough for the price it is sold at.
- Enhance Customer Loyalty/Retention through loyalty programs. Indeed, Universal Studios Singapore currently no longer offers seasonal or annual passes.
- Optimize Pricing to change cost perception through bundle deals and loyalty programs.
