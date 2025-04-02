import pandas as pd
import os


base_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

def classify(df):
    """
    Classifies Instagram post captions into specific categories based on the presence of keywords.

    This function processes the captions in the given DataFrame and assigns binary values 
    (1 or 0) to various category columns, indicating the presence of keywords associated 
    with specific themes. The function performs the following operations:

    1. Removes hashtags from captions.
    2. Checks each caption for keywords related to:
       - Family-friendly content
       - High-value offerings
       - Influencer mentions
       - Halloween themes
       - Festive occasions
       - Minion promotions
       - Deals and promotions
       - Attraction events
       
    The results are stored in the DataFrame as new columns with binary indicators.

    Parameters:
        df (DataFrame): The DataFrame containing Instagram post data with a 'caption' column 
        that includes the text content of each post.

    Returns:
        None: This function modifies the input DataFrame in place and saves the classified 
        data to a CSV file named `uss_ig_classified.csv`.
    """
    # Define functions for each category
    def is_family_friendly(caption):
        family_friendly_keywords = ["family", "kid-friendly", "fun", "children", "parents"]
        return any(word in caption for word in family_friendly_keywords)

    def is_high_value(caption):
        high_value_keywords = ["luxury", "premium", "exclusive", "high quality", "best value", "vip"]
        return any(word in caption for word in high_value_keywords)

    def is_influencer(caption):
        influencer_key_words = ["photo: @", "📷: @", "jackson wang", "@terencethen"]
        return any(word in caption for word in influencer_key_words)

    def is_halloween(caption):
        halloween_keywords = ["halloween", "spooky", "pumpkin", "costume", "hhn", "halloweenhorrornights", "usshhn", "haunted", "terror"]
        return any(word in caption for word in halloween_keywords)

    def is_festive(caption):
        festive_keywords = ["festive", "holiday", "christmas", "xmas", "santa", "cny", "lunar new year"]
        return any(word in caption for word in festive_keywords)

    def is_deals_promotions(caption):
        deals_keywords = ["sale", "discount", "offer", "limited time", "deal", "promotion", "merch", "meal", "eat", "fuel", "feast", "starbot cafe", "kt's grill", "loui's pizza", "mel's drive-in", "discovery food court", "oasis spice cafe", "treat", "food", "dish", "merchandise", "collection", "plushie", "indulge"]
        return any(word in caption for word in deals_keywords)

    def is_minion_promotion(caption):
        minion_keywords = ["minion", "despicable me", "despicable"]
        return any(word in caption for word in minion_keywords)

    def attraction_event_based(caption):
        attraction_event_keywords = [
            "limited time", "attraction", "wicked", "temporary", "special event", "ride"
        ]
        return any(word in caption for word in attraction_event_keywords)

    # Remove hashtags from captions
    df['caption'] = df['caption'].str.replace(r'#\w+', '', regex=True).str.strip()
    df['family_friendly'] = df['caption'].apply(is_family_friendly).astype(int)
    df['high_value'] = df['caption'].apply(is_high_value).astype(int)
    df['influencer'] = df['caption'].apply(is_influencer).astype(int)
    df['halloween'] = df['caption'].apply(is_halloween).astype(int)
    df['festive'] = df['caption'].apply(is_festive).astype(int)
    df['is_minion'] = df['caption'].apply(is_minion_promotion).astype(int)
    df['deals_promotions'] = df['caption'].apply(is_deals_promotions).astype(int)
    df['attraction_event'] = df['caption'].apply(attraction_event_based).astype(int)

    df.to_csv(f"{base_dir}/uss_ig_classified.csv", index=False)


if __name__ == "__main__":
    df = pd.read_csv(f"{base_dir}/cleaned_instagram_data.csv")
    classify(df)
