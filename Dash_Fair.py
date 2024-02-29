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


# In[2]:


#2

import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Load the DataFrame
df = pd.read_excel('Dash 1.xlsx')
df['inquiry_date__c'] = pd.to_datetime(df['inquiry_date__c'])

# Filter for PQLs
pql_df = df[df['postgres_status__c'] == 'Submitted']

# Prepare the data for daily and weekly views
pql_daily = pql_df.groupby([pql_df['inquiry_date__c'].dt.date, 'source__c']).size().reset_index(name='count')
pql_weekly = pql_df.groupby([pql_df['inquiry_date__c'].dt.to_period('W').apply(lambda r: r.start_time), 'source__c']).size().reset_index(name='count')
pql_weekly['inquiry_date__c'] = pql_weekly['inquiry_date__c'].dt.date

# Initialize the Dash app
app = dash.Dash(__name__)

# Assuming total_inquiries and figures for pie charts and line chart are defined earlier
total_inquiries = df.shape[0] # Example definition

app.layout = html.Div([
    # First row for total inquiries
    html.Div([
        html.H3(f'Total Number of Inquiries: {total_inquiries}')
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    # Second row for pie charts
    html.Div([
        dcc.Graph(id='pql_dnq_pie_chart', figure=fig_pql_dnq),
        dcc.Graph(id='pql_declined_pie_chart', figure=fig_pql_declined),
        dcc.Graph(id='pql_dnq_declined_abandoned_pie_chart', figure=fig_pql_dnq_declined_abandoned)
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'margin-bottom': '20px'}),
    
    # Third row for the line chart
    html.Div([
        dcc.Graph(id='inquiries_over_time_line_chart', figure=fig_inquiries_over_time)
    ]),
    
    # Fourth row for the new bar chart with interactive time granularity
    html.Div([
        dcc.RadioItems(
            id='time_granularity_selector',
            options=[
                {'label': 'Day by Day', 'value': 'D'},
                {'label': 'Week by Week', 'value': 'W'}
            ],
            value='D',  # Default value
            style={'margin': '20px 0'}
        ),
        dcc.Graph(id='pql_over_time_chart')
    ])
])

@app.callback(
    Output('pql_over_time_chart', 'figure'),
    Input('time_granularity_selector', 'value')
)
def update_pql_chart(granularity):
    if granularity == 'D':
        fig = px.bar(pql_daily, x='inquiry_date__c', y='count', color='source__c', 
                     labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
                     title='PQLs Over Time (Daily)')
    else:
        fig = px.bar(pql_weekly, x='inquiry_date__c', y='count', color='source__c',
                     labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
                     title='PQLs Over Time (Weekly)')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


# In[3]:


#3

import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Load the DataFrame
df = pd.read_excel('Dash 1.xlsx')
df['inquiry_date__c'] = pd.to_datetime(df['inquiry_date__c'])

# Filter for PQLs
pql_df = df[df['postgres_status__c'] == 'Submitted']

# Prepare the data for daily and weekly views, including totals
pql_daily = pql_df.groupby([pql_df['inquiry_date__c'].dt.date, 'source__c']).size().reset_index(name='count')
pql_daily_total = pql_df.groupby([pql_df['inquiry_date__c'].dt.date]).size().reset_index(name='count')
pql_daily_total['source__c'] = 'Total'
pql_daily = pd.concat([pql_daily, pql_daily_total])

pql_weekly = pql_df.groupby([pql_df['inquiry_date__c'].dt.to_period('W').apply(lambda r: r.start_time), 'source__c']).size().reset_index(name='count')
pql_weekly_total = pql_df.groupby([pql_df['inquiry_date__c'].dt.to_period('W').apply(lambda r: r.start_time)]).size().reset_index(name='count')
pql_weekly_total['source__c'] = 'Total'
pql_weekly = pd.concat([pql_weekly, pql_weekly_total])
pql_weekly['inquiry_date__c'] = pql_weekly['inquiry_date__c'].dt.date

# Initialize the Dash app
app = dash.Dash(__name__)

# Assuming total_inquiries and figures for pie charts and line chart are defined earlier
total_inquiries = df.shape[0]  # Example definition

app.layout = html.Div([
    # First row for total inquiries
    html.Div([
        html.H3(f'Total Number of Inquiries: {total_inquiries}')
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    
    # Second row for pie charts
    html.Div([
        dcc.Graph(id='pql_dnq_pie_chart', figure=fig_pql_dnq),
        dcc.Graph(id='pql_declined_pie_chart', figure=fig_pql_declined),
        dcc.Graph(id='pql_dnq_declined_abandoned_pie_chart', figure=fig_pql_dnq_declined_abandoned)
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'margin-bottom': '20px'}),
    
    
     # Third row for the line chart
    html.Div([
        dcc.Graph(id='inquiries_over_time_line_chart', figure=fig_inquiries_over_time)
    ]),
    
    # Fourth row for the new bar chart with interactive time granularity
    html.Div([
        dcc.RadioItems(
            id='time_granularity_selector',
            options=[
                {'label': 'Day by Day', 'value': 'D'},
                {'label': 'Week by Week', 'value': 'W'}
            ],
            value='D',  # Default value
            style={'margin': '20px 0'}
        ),
        dcc.RadioItems(
            id='source_selector',
            options=[
                {'label': 'By Source', 'value': 'Source'},
                {'label': 'Total Only', 'value': 'Total'}
            ],
            value='Source',  # Default to showing by source
            style={'margin': '20px 0'}
        ),
        dcc.Graph(id='pql_over_time_chart')
    ])
])

@app.callback(
    Output('pql_over_time_chart', 'figure'),
    [Input('time_granularity_selector', 'value'),
     Input('source_selector', 'value')]
)
def update_pql_chart(granularity, show_source):
    if granularity == 'D':
        data = pql_daily
    else:
        data = pql_weekly
    
    # Show total or source based on selection
    if show_source == 'Total':
        data = data[data['source__c'] == 'Total']
    else:
        data = data[data['source__c'] != 'Total']
    
    fig = px.bar(data, x='inquiry_date__c', y='count', color='source__c',
            labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
            title=f'PQLs Over Time ({granularity})')

    # If 'Total' is selected, we adjust the bar chart to not color by source since it's a single series
    if show_source == 'Total':
        fig = px.bar(data, x='inquiry_date__c', y='count',
                labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
                title=f'PQLs Over Time ({granularity}) - Total Only')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


# In[5]:


#4

import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_table

# Load the DataFrame
df = pd.read_excel('Dash 1.xlsx')
df['inquiry_date__c'] = pd.to_datetime(df['inquiry_date__c'])


import pandas as pd

# Load the DataFrame
file_path = 'Dash 1.xlsx'
data = pd.read_excel(file_path)

# Ensure 'all_pre_screening_dq_variables__c' column is treated as a list of reasons for each row
data['all_pre_screening_dq_variables__c'] = data['all_pre_screening_dq_variables__c'].str.split(', ')

# Explode the dataset to separate each reason into its own row
exploded_data = data.explode('all_pre_screening_dq_variables__c')

# Extracting the month from 'inquiry_date__c' for monthly analysis
exploded_data['month'] = pd.to_datetime(exploded_data['inquiry_date__c']).dt.strftime('%Y-%m')

# Counting the frequency of each disqualification reason overall
dq_reasons_count = exploded_data['all_pre_screening_dq_variables__c'].value_counts()

# Selecting the top 10 reasons for disqualification
top_10_reasons = dq_reasons_count.head(10).index

# Calculating the percentage of total disqualifications for these reasons
total_disqualifications = dq_reasons_count.sum()
top_10_percentages = (dq_reasons_count.loc[top_10_reasons] / total_disqualifications * 100).round(2)

# Calculating monthly counts and percentages for the top 10 reasons
monthly_counts = exploded_data.groupby(['month', 'all_pre_screening_dq_variables__c']).size().unstack(fill_value=0)
monthly_percentages = monthly_counts[top_10_reasons].div(monthly_counts.sum(axis=1), axis=0) * 100

# Rounding off the monthly percentages to two decimal places
monthly_percentages = monthly_percentages.round(2)

# Creating the final DataFrame
final_df = pd.DataFrame({
    'Reason': top_10_reasons,
    'Percentage of Total DNQs': top_10_percentages.values
})

# Adding and rounding monthly percentages to the DataFrame
for month in monthly_percentages.index:
    final_df[month] = final_df['Reason'].apply(lambda x: monthly_percentages.at[month, x] if x in monthly_percentages.columns else 0).round(2)

# Resetting the index for compatibility with dash_table.DataTable
final_df.reset_index(drop=True, inplace=True)

# Now, final_df is ready for use in Dash app with all percentages rounded to two decimal places



app = dash.Dash(__name__)
# Assuming total_inquiries and figures for pie charts and line chart are defined earlier
total_inquiries = df.shape[0]  # Example definition

app.layout = html.Div([
    # First row for total inquiries
    html.Div([
        html.H3(f'Total Number of Inquiries: {total_inquiries}')
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    
    # Second row for pie charts
    html.Div([
        dcc.Graph(id='pql_dnq_pie_chart', figure=fig_pql_dnq),
        dcc.Graph(id='pql_declined_pie_chart', figure=fig_pql_declined),
        dcc.Graph(id='pql_dnq_declined_abandoned_pie_chart', figure=fig_pql_dnq_declined_abandoned)
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'margin-bottom': '20px'}),
    
    
     # Third row for the line chart
    html.Div([
        dcc.Graph(id='inquiries_over_time_line_chart', figure=fig_inquiries_over_time)
    ]),
    
    # Fourth row for the new bar chart with interactive time granularity
    html.Div([
        dcc.RadioItems(
            id='time_granularity_selector',
            options=[
                {'label': 'Day by Day', 'value': 'D'},
                {'label': 'Week by Week', 'value': 'W'}
            ],
            value='D',  # Default value
            style={'margin': '20px 0'}
        ),
        dcc.RadioItems(
            id='source_selector',
            options=[
                {'label': 'By Source', 'value': 'Source'},
                {'label': 'Total Only', 'value': 'Total'}
            ],
            value='Source',  # Default to showing by source
            style={'margin': '20px 0'}
        ),
        dcc.Graph(id='pql_over_time_chart')
    ]), 
    
    # New section for the DNQ analysis table
    html.Div([
        html.H3('Top 10 Disqualification Reasons'),
        dash_table.DataTable(
            id='dnq_analysis_table',
            columns=[{"name": i, "id": i} for i in final_df.columns],
            data=final_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '80px', 'width': '80px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            }
        )
    ], style={'width': '100%', 'margin-bottom': '20px'})
])

@app.callback(
    Output('pql_over_time_chart', 'figure'),
    [Input('time_granularity_selector', 'value'),
     Input('source_selector', 'value')]
)
def update_pql_chart(granularity, show_source):
    if granularity == 'D':
        data = pql_daily
    else:
        data = pql_weekly
    
    # Show total or source based on selection
    if show_source == 'Total':
        data = data[data['source__c'] == 'Total']
    else:
        data = data[data['source__c'] != 'Total']
    
    fig = px.bar(data, x='inquiry_date__c', y='count', color='source__c',
            labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
            title=f'PQLs Over Time ({granularity})')

    # If 'Total' is selected, we adjust the bar chart to not color by source since it's a single series
    if show_source == 'Total':
        fig = px.bar(data, x='inquiry_date__c', y='count',
                labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
                title=f'PQLs Over Time ({granularity}) - Total Only')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


# In[15]:


# 5

import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_table

# Load the DataFrame
df = pd.read_excel('Dash 1.xlsx')
df['inquiry_date__c'] = pd.to_datetime(df['inquiry_date__c'])


import pandas as pd

# Load the DataFrame
file_path = 'Dash 1.xlsx'
data = pd.read_excel(file_path)

# Ensure 'all_pre_screening_dq_variables__c' column is treated as a list of reasons for each row
data['all_pre_screening_dq_variables__c'] = data['all_pre_screening_dq_variables__c'].str.split(', ')

# Explode the dataset to separate each reason into its own row
exploded_data = data.explode('all_pre_screening_dq_variables__c')

# Extracting the month from 'inquiry_date__c' for monthly analysis
exploded_data['month'] = pd.to_datetime(exploded_data['inquiry_date__c']).dt.strftime('%Y-%m')

# Counting the frequency of each disqualification reason overall
dq_reasons_count = exploded_data['all_pre_screening_dq_variables__c'].value_counts()

# Selecting the top 10 reasons for disqualification
top_10_reasons = dq_reasons_count.head(10).index

# Calculating the percentage of total disqualifications for these reasons
total_disqualifications = dq_reasons_count.sum()
top_10_percentages = (dq_reasons_count.loc[top_10_reasons] / total_disqualifications * 100).round(2)

# Calculating monthly counts and percentages for the top 10 reasons
monthly_counts = exploded_data.groupby(['month', 'all_pre_screening_dq_variables__c']).size().unstack(fill_value=0)
monthly_percentages = monthly_counts[top_10_reasons].div(monthly_counts.sum(axis=1), axis=0) * 100

# Rounding off the monthly percentages to two decimal places
monthly_percentages = monthly_percentages.round(2)

# Creating the final DataFrame
final_df = pd.DataFrame({
    'Reason': top_10_reasons,
    'Percentage of Total DNQs': top_10_percentages.values
})

# Adding and rounding monthly percentages to the DataFrame
for month in monthly_percentages.index:
    final_df[month] = final_df['Reason'].apply(lambda x: monthly_percentages.at[month, x] if x in monthly_percentages.columns else 0).round(2)

# Resetting the index for compatibility with dash_table.DataTable
final_df.reset_index(drop=True, inplace=True)

# Now, final_df is ready for use in Dash app with all percentages rounded to two decimal places

# Assuming 'data' is your DataFrame loaded from 'Dash 1.xlsx'
data['inquiry_date__c'] = pd.to_datetime(data['inquiry_date__c'])
data['month'] = data['inquiry_date__c'].dt.to_period('M')
data['week'] = data['inquiry_date__c'].dt.to_period('W')
data['day'] = data['inquiry_date__c'].dt.date


app = dash.Dash(__name__)
# Assuming total_inquiries and figures for pie charts and line chart are defined earlier
total_inquiries = df.shape[0]  # Example definition

app.layout = html.Div([
    # First row for total inquiries
    html.Div([
        html.H3(f'Total Number of Inquiries: {total_inquiries}')
    ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
    
    # Second row for pie charts
    html.Div([
        dcc.Graph(id='pql_dnq_pie_chart', figure=fig_pql_dnq),
        dcc.Graph(id='pql_declined_pie_chart', figure=fig_pql_declined),
        dcc.Graph(id='pql_dnq_declined_abandoned_pie_chart', figure=fig_pql_dnq_declined_abandoned)
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'margin-bottom': '20px'}),
    
    # Third row for the line chart
    html.Div([
        dcc.Graph(id='inquiries_over_time_line_chart', figure=fig_inquiries_over_time)
    ]),
    
    # Fourth row for the PQL bar chart with interactive time granularity
    html.Div([
        dcc.RadioItems(
            id='pql_time_granularity_selector',  # Updated ID
            options=[
                {'label': 'Day by Day', 'value': 'D'},
                {'label': 'Week by Week', 'value': 'W'}
            ],
            value='D',  # Default value
            style={'margin': '20px 0'}
        ),
        dcc.RadioItems(
            id='source_selector',
            options=[
                {'label': 'By Source', 'value': 'Source'},
                {'label': 'Total Only', 'value': 'Total'}
            ],
            value='Source',  # Default to showing by source
            style={'margin': '20px 0'}
        ),
        dcc.Graph(id='pql_over_time_chart')
    ]), 

    # New section for the DNQ analysis table
    html.Div([
        html.H3('Top 10 Disqualification Reasons'),
        dash_table.DataTable(
            id='dnq_analysis_table',
            columns=[{"name": i, "id": i} for i in final_df.columns],
            data=final_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                'minWidth': '80px', 'width': '80px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            }
        )
    ], style={'width': '100%', 'margin-bottom': '20px'}),
    
    # Separate time granularity selector for the permission to contact graph
    dcc.RadioItems(
        id='permission_time_granularity_selector',  # Unique ID for this selector
        options=[
            {'label': 'Monthly', 'value': 'month'},
            {'label': 'Weekly', 'value': 'week'},
            {'label': 'Daily', 'value': 'day'}
        ],
        value='month',  # Default value
        style={'margin': '20px 0'}
    ),
    
    # Graph to display the permission to contact after DNQ percentages
    dcc.Graph(id='permission_to_contact_graph')
])

@app.callback(
    Output('pql_over_time_chart', 'figure'),
    [Input('pql_time_granularity_selector', 'value'),  # Updated ID
     Input('source_selector', 'value')]
)
def update_pql_chart(granularity, show_source):
    if granularity == 'D':
        data = pql_daily
    else:
        data = pql_weekly
    
    # Show total or source based on selection
    if show_source == 'Total':
        data = data[data['source__c'] == 'Total']
    else:
        data = data[data['source__c'] != 'Total']
    
    fig = px.bar(data, x='inquiry_date__c', y='count', color='source__c',
            labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
            title=f'PQLs Over Time ({granularity})')

    # If 'Total' is selected, we adjust the bar chart to not color by source since it's a single series
    if show_source == 'Total':
        fig = px.bar(data, x='inquiry_date__c', y='count',
                labels={'count': 'Number of PQLs', 'inquiry_date__c': 'Date'},
                title=f'PQLs Over Time ({granularity}) - Total Only')

    return fig
    
    
@app.callback(
    Output('permission_to_contact_graph', 'figure'),
    [Input('permission_time_granularity_selector', 'value')]
)
def update_permission_graph(granularity):
    # Filter out rows where 'permission_to_contact_after_dnq' is NaN
    filtered_data = data.dropna(subset=['permission_to_contact_after_dnq'])

    # Determine the period column based on the selected granularity
    if granularity == 'day':
        filtered_data['period'] = filtered_data['inquiry_date__c'].dt.date
    elif granularity == 'week':
        filtered_data['period'] = filtered_data['week'].dt.start_time
    else:  # 'month'
        filtered_data['period'] = filtered_data['month'].dt.start_time

    # Group by period and permission to contact, then calculate the size and unstack
    grouped = filtered_data.groupby(['period', 'permission_to_contact_after_dnq']).size().unstack(fill_value=0)

    # Calculate percentages after dropping NaNs, only considering 'Yes' and 'No'
    totals = grouped[['Yes', 'No']].sum(axis=1)
    percentages = grouped[['Yes', 'No']].div(totals, axis=0) * 100

    # Reset index for plotting (Plotly expects data in a certain format)
    percentages_reset = percentages.reset_index().melt(id_vars='period', value_name='Percentage')

    # Create the figure
    fig = px.bar(percentages_reset, x='period', y='Percentage', color='permission_to_contact_after_dnq',
                 barmode='group',
                 labels={'period': 'Period', 'Percentage': 'Percentage (%)'},
                 title=f'Permission to Contact After DNQ Over Time - {granularity.title()}')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




