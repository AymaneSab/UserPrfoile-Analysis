from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pymongo import MongoClient
import pandas as pd

# Function to retrieve data from MongoDB
def get_data_from_mongodb(collection_name, db_name, uri):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Convert MongoDB collection to Pandas DataFrame
    data = pd.DataFrame(list(collection.find()))

    # Close the MongoDB client
    client.close()

    return data

# Create the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='nationality-count-bar-chart'),
    html.Div(id='average-age'),
    dcc.Graph(id='common-email-domains-pie-chart'),  # Added pie chart component
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds, set the interval for periodic updates (e.g., every 1 minute)
        n_intervals=0
    )
])

# Callback to update the bar chart, average age, and common email domains based on selected data
@app.callback(
    [Output('nationality-count-bar-chart', 'figure'),
     Output('average-age', 'children'),
     Output('common-email-domains-pie-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)

def update_data(n_intervals):
    # Retrieve the latest data from MongoDB
    user_count_df = get_data_from_mongodb("user_count_by_nationality", "User_Profiles" ,"mongodb://localhost:27017/")
    average_age_df = get_data_from_mongodb("average_age", "User_Profiles" ,"mongodb://localhost:27017/")
    common_email_domains_df = get_data_from_mongodb("common_email_domains", "User_Profiles" ,"mongodb://localhost:27017/")

    # Create a bar chart
    bar_chart_figure = {
        'data': [
            {'x': user_count_df['Nat'], 'y': user_count_df['user_count'], 'type': 'bar', 'name': 'User Count'},
        ],
        'layout': {
            'title': 'User Count by Nationality',
            'xaxis': {'title': 'Nationality'},
            'yaxis': {'title': 'User Count'},
        }
    }

    # Display average age
    average_age = f"Average Age: {average_age_df['avg_age'].iloc[0]:.2f} years"

    # Create a pie chart for common email domains
    pie_chart_figure = {
        'data': [
            {'labels': common_email_domains_df['email_domain'], 'values': common_email_domains_df['domain_count'], 'type': 'pie', 'name': 'Domain Count'},
        ],
        'layout': {
            'title': 'Common Email Domains',
        }
    }

    return bar_chart_figure, average_age, pie_chart_figure

if __name__ == '__main__':
    app.run_server(debug=True)
