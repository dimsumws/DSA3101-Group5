import matplotlib.pyplot as plt
import os
import pandas as pd
from process_survey_data import (
    mapping,
    create_visit_reason_columns, 
    create_mkting_content_pref_columns
)
import seaborn as sns

import pandas as pd
import matplotlib.pyplot as plt

base_dir = os.path.abspath(os.path.join(os.getcwd(), "marketing_analysis/visualisations"))

def save_table_as_image(obj, filename="table.png"):
    """Handles both Series and DataFrame and saves as a PNG."""
    if isinstance(obj, pd.Series):
        obj = obj.to_frame().reset_index()
    
    fig, ax = plt.subplots(figsize=(len(obj.columns) * 1.2, len(obj) * 0.5))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=obj.values, colLabels=obj.columns, cellLoc='center', loc='center')
    plt.savefig(filename, bbox_inches='tight', dpi=300)


class SurveyAnalyser:
    def __init__(self, survey_data):
        """Initialise the analyser with processed survey data."""
        self.survey_data = mapping(survey_data.loc[:, ['visit_freq', 'top_expense', 'visit_reason', 'mkting_content_pref']])
        self.survey_visit_reasons = create_visit_reason_columns(self.survey_data.copy())
        self.survey_mkting_pref = create_mkting_content_pref_columns(self.survey_data.copy())
        self.marketing_content =  {
                                    "deals_promotions": "Discounts, special offers, or bundles",
                                    "attraction_events": "New attractions or event announcements",
                                    "insider_access": "Behind-the-scenes content or exclusive previews",
                                    "social_media": "User-generated content (e.g., visitor testimonials, influencer partnerships)",
                                    "engagement_based": "Interactive experiences (e.g., virtual tours, social media contests)"
                                }
        self.reasons = {
            "attraction": "To experience a specific attraction or ride",
            "event": "To attend a special event or seasonal celebration",
            "promotion": "Because of a special promotion or discount",
            "social": "To spend time with family/friends",
            "leisure": "For a relaxing getaway or vacation",
            "tourism": "As part of a larger travel plan",
            "new_attraction": "To visit a newly opened or recently renovated park/area",
            "social_media": "Because of a social media post or influencer recommendation"
        }

    def frequency_distribution(self):
        """Returns visit frequency distribution."""
        frequency_distribution = self.survey_data["visit_freq"].value_counts()
        save_table_as_image(frequency_distribution, f"{base_dir}/freq_dist.png")

    def spender_distribution(self):
        """Returns spender type distribution."""
        spender_distribution = self.survey_data["spender_type"].value_counts()
        save_table_as_image(spender_distribution, f"{base_dir}/spender_dist.png")

    def top_mkting_pref(self):
        """Returns the most preferred marketing content."""
        d = {}
        for i in range(6, 11):
            d[self.survey_mkting_pref.columns[i]] = self.survey_mkting_pref.iloc[:, i].sum()
        df = pd.DataFrame(sorted(d.items(), key=lambda x: -x[1]), columns=['Marketing Content', 'Count'])
        save_table_as_image(df, f"{base_dir}/mkting_pref_table.png")

    def top_visit_reasons(self):
        """Returns the most common reasons for visiting."""
        d = {}
        for i in range(6, 14):
            d[self.survey_visit_reasons.columns[i]] = self.survey_visit_reasons.iloc[:, i].sum()
        df = pd.DataFrame(sorted(d.items(), key=lambda x: -x[1]), columns=['Visit Reason', 'Count'])
        save_table_as_image(df, f"{base_dir}visit_reasons_table.png")

    # def plot_top_reasons(self):
    #     """Visualises top visit reasons."""
    #     df = self.top_visit_reasons()
    #     ax = df.plot(kind='bar', x='Visit Reason', y='Count', legend=False)
    #     plt.title("Top Visit Reasons")
    #     plt.xticks(rotation=45, ha='right')
    #     plt.savefig(f"{base_dir}/top_visit_reasons.png", bbox_inches='tight', dpi=300)
    #     plt.close()

    # def plot_top_mkting_pref(self):
    #     """Visualises top marketing content preferences."""
    #     df = self.top_mkting_pref()
    #     ax = df.plot(kind='bar', x='Marketing Content', y='Count', legend=False)
    #     plt.title("Top Marketing Content Preferences")
    #     plt.xticks(rotation=45, ha='right')
    #     plt.savefig(f"{base_dir}/top_mkting_pref.png", bbox_inches='tight', dpi=300)
    #     plt.close()

    def visualise_preferences_by_freq(self):
        """Plots marketing content preferences and visit reasons by visitor frequency."""
    
        # Convert data to long format
        df_mkting_long = self.survey_mkting_pref.melt(id_vars=['frequency'], value_vars=self.marketing_content.keys(), var_name="content", value_name="selected")
        df_reasons_long = self.survey_visit_reasons.melt(id_vars=['frequency'], value_vars=self.reasons.keys(), var_name="reason", value_name="selected")

        # Filter only selected rows
        df_mkting_long = df_mkting_long[df_mkting_long['selected'] == 1]
        df_reasons_long = df_reasons_long[df_reasons_long['selected'] == 1]

        # Set frequency order for clarity
        freq_order = ["rare", "traveler", "moderate", "frequent"]

        plt.figure(figsize=(14, 7))

        # Marketing Content Plot
        plt.subplot(1, 2, 1)
        sns.countplot(data=df_mkting_long, x="frequency", hue="content", palette="Set2", order=freq_order)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Visiting Frequency")
        plt.ylabel("Number of Visitors")
        plt.title("Visitors by Frequency and Preferred Marketing Content")
        plt.legend(title="Marketing Content", loc="upper right")

        # Visit Reasons Plot
        plt.subplot(1, 2, 2)
        sns.countplot(data=df_reasons_long, x="frequency", hue="reason", palette="Set2", order=freq_order)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Visiting Frequency")
        plt.ylabel("Number of Visitors")
        plt.title("Visitors by Frequency and Visit Reason")
        plt.legend(title="Visit Reason", loc="upper right")

        plt.tight_layout()
        plt.savefig(f"{base_dir}/pref_by_freq.png", bbox_inches='tight', dpi=300)
        plt.close()

    def visualise_preferences_by_spending(self):
        """Plots marketing content preferences and visit reasons by spender type."""
        
        # Convert data to long format
        df_mkting_long = self.survey_mkting_pref.melt(id_vars=['spender_type'], value_vars=self.marketing_content.keys(), var_name="content", value_name="selected")
        # Filter only rows where the reason was selected (assuming 1 means selected)
        df_mkting_long = df_mkting_long[df_mkting_long['selected'] == 1]

        # Convert data to long format for easy plotting
        df_reasons_long = self.survey_visit_reasons.melt(id_vars=['spender_type'], 
                            value_vars=self.reasons.keys(), 
                            var_name="reason", 
                            value_name="selected")

        # Filter only rows where the reason was selected (assuming 1 means selected)
        df_reasons_long = df_reasons_long[df_reasons_long['selected'] == 1]

        # Combined Plot
        plt.figure(figsize=(14, 7))

        # Marketing Content Count Plot
        plt.subplot(1, 2, 1)
        sns.countplot(data=df_mkting_long, x="spender_type", hue="content", palette="Set2")
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Spender Type")
        plt.ylabel("Number of Visitors")
        plt.title("Number of Visitors by Spender Type and Preferred USS Marketing Content")
        plt.legend(title="Preferred USS Marketing Content", bbox_to_anchor=(1.05, 1), loc="upper left")

        # Visit Reasons Count Plot
        plt.subplot(1, 2, 2)
        sns.countplot(data=df_reasons_long, x="spender_type", hue="reason", palette="Set2")
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Spender Type")
        plt.ylabel("Number of Visitors")
        plt.title("Number of Visitors by Spender Type and Reason for Visiting USS")
        plt.legend(title="Reason for Visiting", bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()
        plt.savefig(f"{base_dir}/pref_by_spending.png", bbox_inches='tight', dpi=300)
        plt.close()

if __name__ == '__main__':
    survey_data = pd.read_csv("data/survey_responses/cleaned_survey_responses.csv")
    analyser = SurveyAnalyser(survey_data)
    # print(analyser.survey_data)
    # print(analyser.survey_mkting_pref)
    # print(analyser.survey_visit_reasons)
    analyser.visualise_preferences_by_spending()