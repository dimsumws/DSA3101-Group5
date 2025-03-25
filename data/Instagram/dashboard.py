import dash
from dash import dcc, html,  dash_table, callback, Output, Input
import pandas as pd
import plotly.express as px

# Load data
df_metrics = pd.read_csv('category_metrics.csv')
df_sentiment = pd.read_csv('uss_ig_classified_sentiment.csv')
df_sentiment['post_date'] = pd.to_datetime(df_sentiment['post_date'])

# Define marketing categories and metrics
categories = ['family_friendly', 'high_value', 'influencer', 'halloween', 'festive', 'deals_promotions', 'attraction_event']
metrics = ['num_likes', 'num_comments', 'sentiment', 'engagement_score']

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Marketing Strategy Analysis"),

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
        value=categories,  # Default: Show all categories
        multi=True,  
        placeholder="Select Marketing Categories",
    ),

    # Dropdown for selecting metric
    dcc.Dropdown(
        id='metric-dropdown',
        options=[{'label': metric.replace('_', ' ').title(), 'value': metric} for metric in metrics],
        value='num_likes',  # Default: Show Likes
        multi=False,  
        placeholder="Select Metric to Display",
    ),

    # Graph
    dcc.Graph(id='engagement-graph'),
])

# Callback to update the graph based on dropdown selections
@callback(
    Output('engagement-graph', 'figure'),
    Input('category-dropdown', 'value'),
    Input('metric-dropdown', 'value')
)
def update_graph(selected_categories, selected_metric):
    # Filter data based on selected categories
    df_filtered = df_sentiment[df_sentiment[selected_categories].sum(axis=1) > 0]
    
    # Aggregate data by date
    df_grouped = df_filtered.groupby('post_date')[selected_metric].sum().reset_index()

    # Generate graph
    fig = px.line(df_grouped, x='post_date', y=selected_metric,
                  title=f'{selected_metric.replace("_", " ").title()} Over Time',
                  labels={selected_metric: selected_metric.replace("_", " ").title()})
    
    return fig

# Run server
if __name__ == '__main__':
    app.run(debug=True)
