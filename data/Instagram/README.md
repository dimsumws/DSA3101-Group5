# Dataset Overview 

This folder contains all datasets related to Universal Studios Singapore's Instagram posts. Below is a description of each file:  

### **Raw Datasets**  
- **`uss_ig.csv`** – Contains raw Instagram post data, including:  
  - `shortcode` (post identifier)  
  - `caption` (post text)  
  - `num_likes` (number of likes)  
  - `comments` (list of comments)  
  - `post_date` (date of post)  
  - `post_type` (e.g., image, video, carousel)  

- **`uss_ig_stories.csv`** – Contains raw Instagram highlights (stories) data, including:  
  - `highlight_title` (title of the highlight)  
  - `shortcode` (post identifier)  
  - `post_date` (date of highlight)  
  - `post_type` (e.g., image, video)  

### **Cleaned Datasets**  
- **`cleaned_instagram_data.csv`** – A cleaned version of `uss_ig.csv` with improved formatting and consistency.  
- **`cleaned_instagram_stories.csv`** – A cleaned version of `uss_ig_stories.csv`.  

### **Classified & Processed Datasets**  
- **`uss_ig_classified.csv`** – An enhanced version of `cleaned_instagram_data.csv`, with additional binary columns indicating whether a post belongs to a specific marketing category:  
  - `family_friendly`  
  - `high_value`
  - `influencer`
  - `halloween`
  - `festive`
  - `is_minion`
  - `deals_promotions`
  - `attraction_event`  

- **`uss_ig_classified_sentiment.csv`** – A further processed version of `uss_ig_classified.csv`, including:  
  - `num_comments` (number of comments)  
  - `sentiment` (aggregated sentiment score from comments)  
  - `engagement_score = a*num_likes + b*num_comments + c*sentiment` (weighted engagement metric)  

### **Summary Metrics**  
- **`category_metrics.csv`** – Aggregated engagement metrics for different marketing categories.  


# Guide on Extracting, Cleaning and Performing Feature Engineering on Data from Universal Studios Singapore's Instagram Posts

### Ensure You're in the Correct Directory  
Make sure you're in the `DSA3101-group5` directory before running any scripts.  

## Steps to Extract Data from Universal Studios Singapore’s Instagram Posts  

### Log in to Instagram via Firefox  
- Open **[Instagram](https://www.instagram.com/)** in **Firefox** and log in to your account.  

### Import Your Instagram Session from Firefox
- Run the following script to import your session:  
    ```bash
    python data/Instagram/Python/615_import_firefox_session.py
    ```
### Extract Instagram Post/Story Data 
- Run the extraction script for posts:
    ```bash
    python data/Instagram/Python/extract_ig_post.py
    ```
- Run the extraction script for stories:
    ```bash
    python data/Instagram/Python/extract_ig_story.py
    ```

### Troubleshooting: If You Encounter the Error: `400 Bad Request - "challenge_required"`
- **Open Instagram in Firefox**.
- If Instagram prompts **"Suspicious Login Attempt"** or **"Verify It’s You"**, follow the verification steps via email/SMS.
- After completing the verification, run the extraction script again:
    ```bash
    python data/Instagram/Python/extract_ig_post.py
    ```
    ```bash
    python data/Instagram/Python/extract_ig_story.py
    ```

## Steps to Clean Data Extracted from Universal Studios Singapore's Instagram

- Run the cleaning script:
    ```bash
    python data/Instagram/Python/clean_ig_post.py
    ```

## Performing Feature Engineering on Unviersal Studios Singapore's Post Data

### Classify Posts into Different Marketing Categories
- Run:
    ```bash
    python data/Instagram/Python/marketing_classification.py
    ```

### Extract Insights from Posts
- Run:
    ```bash
    python data/Instagram/Python/comment_engineering.py
    ```


