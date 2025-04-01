# Overview
The main objective of this project is to evaluate the impact of marketing strategies on guest behaviour through analysing past campaign data to understand changes in visitor segments, identify the most effective marketing content that drives engagement and visitation, and finally, recommend tailored marketing strategies to attract and retain different guest segments.

# Retrieving Data
The data used in this project consists of:
1. Instagram post metrics from @universalstudiossingapore extracted using Instaloader (https://instaloader.github.io/module/structures.html).
2. Survey responses collected from theme park visitors.

## Instagram Data
### Instagram Data Extraction
As detailed in data/Instagram/README.md, we used Instaloader to extract the following post attributes:
`shortcode`: Unique identifier for each post.
`caption`: Text content accompanying the post.
`num_likes`: Number of likes.
`comments`: List of comments.
`post_date`: Date of publication.
`post_type`: Type of media (image, video, carousel).

### Data Cleaning
After extraction, we performed the following preprocessing steps:
1. Convert `post_date` to datetime format
2. Transform `comments` into a dictionary {user1: [comment], user2: [comment], ...}
3. Standardise textual data in caption and comments by removing stopwords and whitespaces, lowercasing and lemmatisation.

### Feature Engineering
After cleaning the dataset, we performed additional transformations to derive meaningful insights:
1. Post classification via Bag of Words
- We manyally defined a Bag of Words (BoW) to classify captions into different marketing categories.
- This enabled us to analyse the effectiveness of various marketing strategies based on engagement metrics and identify guest segments based on their interactions with different content types.
- For example, if posts categorised under `family_friendly` receive high engagement, it su%ggests a segment of guests who are highly interested in family friendly experiences.
2. Comment Volume (`num_comments`)
- We computed the number of comments for each post to measure engagement levels.
3. Sentiment Analysis (`sentiment`)
- Using `VaderSentiment`’s `SentimentIntensityAnalyzer`, we computed the average sentiment score for comments on each post:
\[
\text{sentiments} = [\text{analyser.polarity\_scores}(\text{comment})['compound'] \text{ for comment in comments.values()}]
\]
\[
\text{average sentiment} = \frac{\sum \text{sentiments}}{\text{len(sentiments)}}
\]
4. Engagement Score (`engagement_score`)
To quantify overall engagement, we computed **engagement score** for each post using the formula:
\[
\text{engagement\_score} = (\alpha \times \text{num\_likes}) + (\beta \times \text{num\_comments}) + (\gamma \times \text{sentiment})
\]

#### Weighting Factors:
- $\alpha = 1$: Likes indicate passive interest, so they receive the lowest weight.
- $\beta = 2$: Comments require more effort and signify higher engagement, so they are weighted higher.
- $\gamma = 50$: Sentiment is crucial as it reflects how people emotionally react to content. A highly positive post with fewer likes may still be impactful, so it is given the highest weight.
This score allows us to identify which content resonates most with different guest segments, helping refine marketing strategies.

## Survey Data Processing

We further processed the survey responses from `data/survey_responses/cleaned_survey_responses.csv` to derive useful insights:

### 1. Mapping Visiting Frequencies  
Visitors were categorised into four segments based on their visiting frequency:  
- **Rare**: Infrequent visitors  
- **Moderate**: Occasional visitors  
- **Frequent**: Regular visitors  
- **Traveller**: Visitors from outside the local area  

### 2. Spender Categorisation  
Visitors were classified into different spending levels based on their highest expense category:  
- **Low Spenders**: Those who spend the most on transport  
- **Average Spenders**: Those who spend the most on food & beverage (F&B)  
- **High Spenders**: Those who spend the most on merchandise  

### 3. Mapping Visit Reasons  
Each visitor's reason for visiting was mapped to a predefined category:  

| Reason | Description |
|--------|------------|
| `attraction` | To experience a specific attraction or ride |
| `event` | To attend a special event or seasonal celebration (e.g., Halloween, Christmas, exhibitions in collaboration with other franchises) |
| `promotion` | Because of a special promotion or discount |
| `social` | To spend time with family/friends |
| `leisure` | For a relaxing getaway or vacation |
| `tourism` | As part of a larger travel plan (e.g., trip to the area) |
| `new_attraction` | To visit a newly opened or recently renovated park/area |
| `social_media` | Because of a social media post or influencer recommendation |

### 4. Mapping Marketing Content Seen  
Visitors' exposure to different marketing channels was grouped into broader categories:  

| Category | Included Sources |
|----------|----------------|
| `online_ads` | Social media ads, online banner ads |
| `tv_commercials` | TV commercials |
| `youtube_influencer` | YouTube videos or influencer content (including overseas theme parks) |
| `email_newsletter` | Email newsletters or promotional offers |
| `physical_ads` | Billboard or outdoor ads, print advertisements (e.g., magazines, brochures) |
| `theme_park_websites` | Theme park websites or blogs |
| `third_party_promotions` | Promotions or discounts from travel agencies or third-party platforms (e.g., Agoda, Groupon) |

### 5. Mapping Preferred Marketing Content  
Visitors' preferred marketing content types were categorized as follows:  

| Category | Description |
|----------|------------|
| `deals_promotions` | Discounts, special offers, or bundles |
| `attraction_events` | New attractions or event announcements |
| `insider_access` | Behind-the-scenes content or exclusive previews |
| `social_media` | User-generated content (e.g., visitor testimonials, influencer partnerships) |
| `engagement_based` | Interactive experiences (e.g., virtual tours, social media contests) |

These transformations enabled deeper analysis into guest segments, spending behaviors, and the effectiveness of different marketing strategies.  
