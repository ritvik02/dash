#!/usr/bin/env python
# coding: utf-8

# In[1]:


#1

import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

df = pd.read_excel('Dash 1.xlsx')

# Function to create a pie chart for specific status comparisons
def create_pie_chart(df, statuses, title):
    filtered_df = df[df['postgres_status__c'].isin(statuses)]
    status_counts = filtered_df['postgres_status__c'].value_counts().to_dict()
    values = [status_counts.get(status, 0) for status in statuses]
    fig = px.pie(names=statuses, values=values, title=title)
    return fig

# Function to create a line chart for inquiries over time
def create_line_chart(df):
    # Preparing the data
    df['inquiry_date__c'] = pd.to_datetime(df['inquiry_date__c'])
    df.set_index('inquiry_date__c', inplace=True)
    df.sort_index(inplace=True)
    status_types = ['Submitted', 'DNQ', 'Declined Participation', 'Abandoned']
    
    # Creating a DataFrame to hold counts for each status over time
    time_df = pd.DataFrame()
    for status in status_types:
        time_df[status] = df[df['postgres_status__c'] == status].resample('D').size()
    time_df['Total Inquiries'] = df.resample('D').size()
    time_df.fillna(0, inplace=True)
    
    # Creating the line chart
    fig = px.line(time_df, x=time_df.index, y=time_df.columns,
                  labels={'value': 'Number of Inquiries', 'variable': 'Status'},
                  title='Inquiries Over Time')
    return fig

# Calculate total number of inquiries
total_inquiries = df.shape[0]

# Create pie charts
fig_pql_dnq = create_pie_chart(df, ['Submitted', 'DNQ'], "PQL vs DNQ Inquiry Status")
fig_pql_declined = create_pie_chart(df, ['Submitted', 'Declined Participation'], "PQL vs Declined Participation Inquiry Status")
fig_pql_dnq_declined_abandoned = create_pie_chart(df, ['Submitted', 'DNQ', 'Declined Participation', 'Abandoned'], "PQL, DNQ, Declined, Abandoned Distribution")

# Create line chart for inquiries over time
fig_inquiries_over_time = create_line_chart(df)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    # Display total inquiries
    html.Div([
        html.H3(f'Total Number of Inquiries: {total_inquiries}')
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    # Container div for pie charts, side by side using flexbox
    html.Div([
        dcc.Graph(id='pql_dnq_pie_chart', figure=fig_pql_dnq),
        dcc.Graph(id='pql_declined_pie_chart', figure=fig_pql_declined),
        dcc.Graph(id='pql_dnq_declined_abandoned_pie_chart', figure=fig_pql_dnq_declined_abandoned)
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'margin-bottom': '20px'}),
    
    # Container for the line chart
    html.Div([
        dcc.Graph(id='inquiries_over_time_line_chart', figure=fig_inquiries_over_time)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)


