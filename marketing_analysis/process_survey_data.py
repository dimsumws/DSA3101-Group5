import pandas as pd

def mapping(df):
    """
    Maps visitor frequency and spending categories in the given DataFrame.

    This function transforms the `visit_freq` column into categories such as 'rare', 'moderate', 
    'frequent', and 'traveller' based on predefined mappings. It also categorizes the top spending 
    type into 'low spender', 'average spender', or 'high spender' and renames the resulting column 
    to `spender_type`, which is set as an ordered categorical type.

    Parameters:
        df (DataFrame): The DataFrame containing visitor data with `visit_freq` and `top_expense` columns.

    Returns:
        DataFrame: The modified DataFrame with additional columns for frequency and spending category.
    """
    freq_mapping = {
        '< Once every 3 years': 'rare',
        'Once every 2-3 years': 'rare',
        'Once every year': 'moderate',
        'A few times every year': 'frequent',
        'Once every month': 'frequent',
        '> Once every month': 'frequent',
        'When on vacation': 'traveller'
    }
    
    df['frequency'] = df['visit_freq'].replace(freq_mapping) 

    spender_mapping = {
        'Transportation': 'low spender',
        'F&B': 'average spender',
        'Merchandise': 'high spender'
    }

    spending_order = ['low spender', 'average spender', 'high spender']

    df['spending_cat'] = df['top_expense'].replace(spender_mapping)
    df = df.rename(columns={'spending_cat':'spender_type'})
    df['spender_type'] = pd.Categorical(df['spender_type'], categories=spending_order, ordered=True)

    return df


def create_visit_reason_columns(df):
    """
    Creates binary columns for visit reasons based on the provided keywords.

    This function checks the `visit_reason` column for specific keywords related to 
    various reasons for visiting the theme park. It generates new columns indicating 
    whether each reason is applicable (1) or not (0) for each visitor.

    Parameters:
        df (DataFrame): The DataFrame containing visitor data with a `visit_reason` column.

    Returns:
        DataFrame: The modified DataFrame with new binary columns for each visit reason.
    """
    reasons = {"attraction": "To experience a specific attraction or ride",
               "event": "To attend a special event or seasonal celebration (e.g., Halloween, Christmas, Exhibitions in collaboration with other franchises)",
               "promotion": "Because of a special promotion or discount",
               "social": "To spend time with family/friends",
               "leisure": "For a relaxing getaway or vacation",
               "tourism": "As part of a larger travel plan (e.g., trip to the area)",
               "new_attraction": "To visit a newly opened or recently renovated park/area",
               "social_media": "Because of a social media post or influencer recommendation"}
    
    for col_name, keywords in reasons.items():
        df[col_name] = df['visit_reason'].apply(lambda x: 1 if keywords in x else 0)

    return df


def create_mkting_content_seen_columns(df):
    """
    Creates columns indicating the number of marketing content types seen by visitors.

    This function evaluates the `mkting_content_seen` column and checks for the presence of 
    various marketing content keywords. It generates new columns that count the occurrences 
    of each marketing content type.

    Parameters:
        df (DataFrame): The DataFrame containing visitor data with a `mkting_content_seen` column.

    Returns:
        DataFrame: The modified DataFrame with new columns for each marketing content type, indicating the count of occurrences.
    """
    # Mappings where some categories are grouped
    marketing_content = {
        "online_ads": ["Social media ads", "Online banner ads"],  # Grouped together
        "tv_commercials": ["TV commercials"],
        "youtube_influencer": ["YouTube videos or influencer content (can be overseas theme parks as well)"],
        "email_newsletter": ["Email newsletter or promotional offers"],
        "physical_ads": ["Billboard or outdoor ads", "Print advertisements (e.g., magazines, brochures)"],
        "theme_park_websites": ["Theme park websites or blogs"],
        "third_party_promotions": ["Promotions or discounts offered by travel agencies or third-party platforms like Agoda, Groupon, etc."]
    }

    # Function to check if any keyword in the list exists in the given row
    def extract_content_seen(row, keywords):
        return sum(1 for keyword in keywords if keyword in row)

    # Create new columns that count occurrences
    for col_name, keywords in marketing_content.items():
        df[col_name] = df['mkting_content_seen'].apply(lambda x: extract_content_seen(str(x), keywords))

    return df


def create_mkting_content_pref_columns(df):
    """
    Creates binary columns indicating the marketing content preferences of visitors.

    This function checks the `mkting_content_pref` column for specific marketing content 
    keywords and generates new columns indicating whether each content type is preferred (1) 
    or not preferred (0) for each visitor.

    Parameters:
        df (DataFrame): The DataFrame containing visitor data with a `mkting_content_pref` column.

    Returns:
        DataFrame: The modified DataFrame with new binary columns for each marketing content preference.
    """
    marketing_content = {
        "deals_promotions": "Discounts, special offers, or bundles",
        "attraction_events": "New attractions or event announcements",
        "insider_access": "Behind-the-scenes content or exclusive previews",
        "social_media": "User-generated content (e.g., visitor testimonials, influencer partnerships)",
        "engagement_based": "Interactive experiences (e.g., virtual tours, social media contests)"
    }

    # Create new columns that count occurrences instead of binary 0/1
    for col_name, keywords in marketing_content.items():
        df[col_name] = df['mkting_content_pref'].apply(lambda x: 1 if keywords in x else 0)

    return df