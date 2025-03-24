import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Load the category metrics data from CSV
df = pd.read_csv('category_metrics.csv')
df_sentiment = pd.read_csv('uss_ig_classified_sentiment.csv')
df_sentiment['post_date'] = pd.to_datetime(df_sentiment['post_date'])

categories = ['family_friendly', 'high_value', 'influencer', 'halloween', 'festive', 'deals_promotions', 'attraction_event']

# Melt the DataFrame to long format for easier plotting
df_long = df_sentiment.melt(id_vars=['post_date', 'num_likes', 'sentiment'], value_vars=categories,
                             var_name='category', value_name='is_in_category')

# Keep only rows where the post belongs to a category
df_long = df_long[df_long['is_in_category'] == 1]

# Group by date and category, then calculate engagement (e.g., total likes or comments)
df_engagement = df_long.groupby(['post_date', 'category']).agg({'num_likes': 'mean', 'sentiment': 'mean'}).reset_index()


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Marketing Category Metrics"),
    dash.dash_table.DataTable(
        id='category-metrics-table',
        columns=[{"name": i, "id": i} for i in df.columns],  # Create table columns based on DataFrame columns
        data=df.to_dict('records'),  # Convert DataFrame to a list of dictionaries
        page_size=10,  # Number of rows per page
        style_table={'overflowX': 'auto'},  # Allow horizontal scrolling
        style_cell={
            'textAlign': 'left',  # Align text to the left
            'padding': '10px'  # Padding for table cells
        },
        style_header={
            'backgroundColor': 'lightgrey',  # Header background color
            'fontWeight': 'bold'  # Bold header text
        },
    ),
    dcc.Graph(
        id='likes-sentiment-graph',
        figure=px.line(df_sentiment, x='post_date', y='num_likes', title='Likes Over Time', labels={'likes': 'Total Likes'}),
    ),
    
    dcc.Graph(
        id='sentiment-graph',
        figure=px.line(df_sentiment, x='post_date', y='sentiment', title='Sentiment Over Time', labels={'sentiment': 'Sentiment Score'}),
    ),
    # Engagement over time grouped by category
    dcc.Graph(
        id='engagement-by-category',
        figure=px.line(df_engagement, x='post_date', y='num_likes', color='category', 
                       title='Engagement Over Time by Marketing Category',
                       labels={'likes': 'Total Likes', 'category': 'Marketing Category'})
    ),
    dcc.Graph(
        id='comments-by-category',
        figure=px.line(df_engagement, x='post_date', y='sentiment', color='category', 
                       title='Comments Over Time by Marketing Category',
                       labels={'comment': 'Total Comments', 'category': 'Marketing Category'})
    )
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
