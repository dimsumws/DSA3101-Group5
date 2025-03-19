import csv
import instaloader
import pandas as pd
import os
import random
import time


def get_post_type(post):
    """Determine the type of Instagram post."""
    if post.typename == "GraphStoryImage":
        return "Image Post"
    elif post.typename == "GraphStoryVideo":
        return "Video Post"
    else:
        return "Unknown Type"
    

def extract_story_data(username, csv_file="uss_ig_stories.csv"):
    L = instaloader.Instaloader()
    L.load_session_from_file("group5_324")  # Load session for authentication
    profile = instaloader.Profile.from_username(L.context, username)

    # Check if the file exists, if not create an empty DataFrame
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=["shortcode", "caption", "num_likes", "comments", "post_date", "post_type"])

    existing_shortcodes = set(df["shortcode"])  # Store existing shortcodes to avoid duplicates

    # for post in profile.get_posts():
    for highlight in L.get_highlights(profile):
        highlight_title = highlight.title
        for story in highlight.get_items():
            shortcode = story.shortcode
            post_type = get_post_type(story)
            
            try:
                if shortcode not in existing_shortcodes:
                    # Collect story data
                    story_data = {
                        "highlight_title": highlight_title,
                        "shortcode": shortcode,
                        "post_date": story.date_utc.strftime("%Y-%m-%d"),
                        "post_type": post_type
                    }

                # Convert post_data into a DataFrame and append to CSV
                new_df = pd.DataFrame([story_data])
                new_df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False, encoding="utf-8")

                print(f"Story {shortcode} added")

                # Sleep to avoid rate limiting
                time.sleep(random.uniform(10, 60))

            except Exception as e:
                print(f"Error processing story {shortcode}: {e}")
                continue

    print(f"Data extraction complete. Saved as {csv_file}")



if __name__ == "__main__":
    extract_story_data("universalstudiossingapore")
