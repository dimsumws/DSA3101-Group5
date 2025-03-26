import dash
from dash import dcc, html, dash_table, callback, Output, Input
import os
import pandas as pd
import plotly.express as px

# cwd = "../DSA3101-Group5"
data_dir = os.path.abspath(os.path.join(os.getcwd(), "data/Instagram/Data"))

# Load data
df_metrics = pd.read_csv(f'{data_dir}/category_metrics.csv')
df_sentiment = pd.read_csv(f'{data_dir}/uss_ig_classified_sentiment.csv')
df_sentiment['post_date'] = pd.to_datetime(df_sentiment['post_date'])

# Define marketing categories and metrics
categories = ['family_friendly', 'high_value', 'influencer', 'halloween', 'festive', 'is_minion', 'deals_promotions', 'attraction_event']
metrics = ['num_likes', 'num_comments', 'sentiment', 'engagement_score']

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Marketing Strategy Engagement Over Time"),

    # Table displaying category metrics
    html.H3("Category Metrics"),
    dash_table.DataTable(
        id='category-metrics-table',
        columns=[{"name": i, "id": i} for i in df_metrics.columns],
        data=df_metrics.to_dict('records'),
        style_table={'overflowX': 'auto', 'margin-bottom': '20px'},
        style_cell={'textAlign': 'left'}
    ),


    # Dropdown for selecting marketing categories
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': cat.replace('_', ' ').title(), 'value': cat} for cat in categories],
        value=['family_friendly'],  # Default selected
        multi=True,
        placeholder="Select Marketing Categories",
    ),

    # Dropdown for selecting engagement metric
    dcc.Dropdown(
        id='metric-dropdown',
        options=[
            {'label': 'Likes', 'value': 'num_likes'},
            {'label': 'Comments', 'value': 'num_comments'},
            {'label': 'Sentiment Score', 'value': 'sentiment_score'},
            {'label': 'Engagement Score', 'value': 'engagement_score'}
        ],
        value='num_likes',
        placeholder="Select Metric",
    ),

    # Graph
    dcc.Graph(id='engagement-graph'),
])

# Callback to update graph
@callback(
    Output('engagement-graph', 'figure'),
    [Input('category-dropdown', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_graph(selected_categories, selected_metric):
    if not selected_categories:
        return px.line(title="No Categories Selected")

    # Filter dataset to include only selected categories
    filtered_df = df_sentiment[['post_date', selected_metric] + selected_categories]

    # Melt dataframe to long format so that each category becomes its own line
    melted_df = filtered_df.melt(id_vars=['post_date', selected_metric], 
                                 value_vars=selected_categories, 
                                 var_name='Category', 
                                 value_name='Is_In_Category')

    # Keep only rows where the category is marked as 1
    melted_df = melted_df[melted_df['Is_In_Category'] == 1]

    # Group by date and category
    grouped_df = melted_df.groupby(['post_date', 'Category'])[selected_metric].mean().reset_index()

    # Plot
    fig = px.line(grouped_df, x='post_date', y=selected_metric, color='Category', 
                  title="Engagement Over Time by Marketing Category")

    return fig

# Run server
if __name__ == '__main__':
    app.run(debug=True)
