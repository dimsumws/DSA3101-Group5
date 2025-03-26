import csv
import instaloader
import pandas as pd
import os
import random
import time

def get_post_type(post):
    """Determine the type of Instagram post."""
    if post.typename == "GraphImage":
        return "Image Post"
    elif post.typename == "GraphVideo":
        return "Video Post"
    elif post.typename == "GraphSidecar":
        return "Carousel (Multiple Images/Videos)"
    else:
        return "Unknown Type"
    

def extract_post_data(username, csv_file="uss_ig.csv"):
    L = instaloader.Instaloader()
    L.load_session_from_file("group5_324")  # Load session for authentication
    profile = instaloader.Profile.from_username(L.context, username)

    csv_file = os.path.abspath(os.path.join(os.getcwd(), "../Data/{csv_file}"))

    # Check if the file exists, if not create an empty DataFrame
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=["shortcode", "caption", "num_likes", "comments", "post_date", "post_type"])

    existing_shortcodes = set(df["shortcode"])  # Store existing shortcodes to avoid duplicates

    for post in profile.get_posts():
        shortcode = post.shortcode
        post_type = get_post_type(post)

        try:
            if shortcode not in existing_shortcodes:
                # Collect post data
                post_data = {
                    "shortcode": shortcode,
                    "caption": post.caption or "No caption",
                    "num_likes": post.likes,
                    "comments": [(c.owner.username, c.text) for c in post.get_comments()],
                    "post_date": post.date_utc.strftime("%Y-%m-%d"),
                    "post_type": post_type
                }

                # Convert post_data into a DataFrame and append to CSV
                new_df = pd.DataFrame([post_data])
                new_df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False, encoding="utf-8")

                print(f"Post {shortcode} added")

                # Sleep to avoid rate limiting
                time.sleep(random.uniform(10, 60))

        except Exception as e:
            print(f"Error processing post {shortcode}: {e}")
            continue

    print(f"Data extraction complete. Saved as {csv_file}")



if __name__ == "__main__":
    extract_post_data("universalstudiossingapore")
