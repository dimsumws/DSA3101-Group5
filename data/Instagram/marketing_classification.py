import pandas as pd

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
    halloween_keywords = ["halloween", "spooky", "pumpkin", "costume", "hhn", "halloweenhorrornights", "usshhn", "haunted"]
    return any(word in caption for word in halloween_keywords)

def is_festive(caption):
    festive_keywords = ["festive", "holiday", "christmas", "xmas", "santa", "cny", "lunar new year"]
    return any(word in caption for word in festive_keywords)

def is_deals_promotions(caption):
    deals_keywords = ["sale", "discount", "offer", "limited time", "deal", "promotion", "merch", "meal", "eat", "fuel", "feast", "starbot cafe", "kt's grill", "loui's pizza", "mel's drive-in", "discovery food court", "oasis spice cafe", "treat", "food", "dish", "merchandise", "collection", "plushie", "indulge"]
    return any(word in caption for word in deals_keywords)

def is_minion_promotion(caption):
    minion_keywords = ["minion", "despicable me"]
    return any(word in caption for word in minion_keywords)

def attraction_event_based(caption):
    attraction_event_keywords = [
        "minion", "despicable me", "limited time", "attraction", "wicked", "temporary", "special event", "ride"
    ]
    return any(word in caption for word in attraction_event_keywords)

def classify(df):
    # Remove hashtags from captions
    df['caption'] = df['caption'].str.replace(r'#\w+', '', regex=True).str.strip()
    df['family_friendly'] = df['caption'].apply(is_family_friendly).astype(int)
    df['high_value'] = df['caption'].apply(is_high_value).astype(int)
    df['influencer'] = df['caption'].apply(is_influencer).astype(int)
    df['halloween'] = df['caption'].apply(is_halloween).astype(int)
    df['festive'] = df['caption'].apply(is_festive).astype(int)
    df['deals_promotions'] = df['caption'].apply(is_deals_promotions).astype(int)
    df['attraction_event'] = df['caption'].apply(attraction_event_based).astype(int)

    df.to_csv("uss_ig_classified.csv", index=False)


if __name__ == "__main__":
    df = pd.read_csv("cleaned_instagram_data.csv")
    classify(df)
