import dash
from dash import dcc, html, Input, Output, dash_table, State
import pandas as pd
import plotly.express as px
import io
import base64
import os

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Ticket Dashboard"
server = app.server  # Expose server for deployment

# App layout
app.layout = html.Div([
    html.H1("Ticket Dashboard"),
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)


# App layout
app.layout = html.Div([
    # Title
    html.Div([
        html.H1("Ticket Management Dashboard", style={'text-align': 'center', 'color': '#ffffff'}),
    ], style={'background-color': '#4CAF50', 'padding': '20px', 'margin-bottom': '20px'}),

    # File upload section
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div(['📂 Drag and Drop or ', html.A('Select an Excel File')]),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px auto',
                'background-color': '#f9f9f9',
                'cursor': 'pointer'
            },
            multiple=False
        ),
    ]),

    # Filters section
    html.Div([
        html.Div([
            html.Label("Filter by Company", style={'font-weight': 'bold'}),
            dcc.Dropdown(id='company-filter', multi=True, placeholder="Select Company"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Filter by Employee", style={'font-weight': 'bold'}),
            dcc.Dropdown(id='employee-filter', multi=True, placeholder="Select Employee"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Filter by Date Range", style={'font-weight': 'bold'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                display_format="DD-MM-YYYY"
            ),
        ], style={'width': '35%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'margin-bottom': '20px', 'padding': '10px', 'background-color': '#f0f0f0', 'border-radius': '10px'}),

    # Metrics cards
    html.Div([
        html.Div([
            html.H4("📊 Total Tickets", style={'color': '#4CAF50'}),
            html.P(id='total-tickets', style={'font-size': '24px', 'font-weight': 'bold'})
        ], className='card'),

        html.Div([
            html.H4("✅ Closed", style={'color': '#2196F3'}),
            html.P(id='closed-tickets', style={'font-size': '24px', 'font-weight': 'bold'})
        ], className='card'),

        html.Div([
            html.H4("🆕 New", style={'color': '#FF9800'}),
            html.P(id='new-tickets', style={'font-size': '24px', 'font-weight': 'bold'})
        ], className='card'),

        html.Div([
            html.H4("⏳ Open", style={'color': '#F44336'}),
            html.P(id='open-tickets', style={'font-size': '24px', 'font-weight': 'bold'})
        ], className='card'),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-bottom': '20px'}),

    # Main visualizations and table
    html.Div([
        html.Div([
            dcc.Graph(id='tickets-by-employee'),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='tickets-by-company'),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='tickets-by-product'),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.H4("Ticket Titles", style={'text-align': 'center'}),
            dash_table.DataTable(
                id='ticket-table',
                style_table={'overflowX': 'auto', 'height': '400px', 'overflowY': 'scroll'},
                style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#f9f9f9', 'color': 'black'},
                page_size=10,
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # Footer section
    html.Div([
        html.Div([
            html.P("Developed by ", style={'font-weight': 'bold', 'font-size': '16px', 'display': 'inline'}),
            html.A("Sahil Paleja", href="https://www.linkedin.com/in/sahil-paleja", target="_blank",
                   style={'color': '#4CAF50', 'font-size': '16px', 'font-weight': 'bold', 'display': 'inline'}),
        ], style={'text-align': 'center', 'padding': '20px', 'background-color': '#333', 'color': 'white'})
    ], style={'margin-top': '40px'}),
], style={'font-family': 'Arial, sans-serif', 'background-color': '#f8f9fa', 'padding': '20px'})

# Callback to process the uploaded file and update dropdown options and date picker defaults
@app.callback(
    [Output('company-filter', 'options'),
     Output('employee-filter', 'options'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_filters_and_dates(contents, filename):
    if not contents:
        return [], [], None, None

    # Decode the uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))

    # Parse the Last_Activity column
    df['Last_Activity'] = pd.to_datetime(df['Last_Activity'], errors='coerce')
    valid_dates = df['Last_Activity'].dropna()

    if valid_dates.empty:
        return [], [], None, None

    company_options = [{'label': company, 'value': company} for company in df['Client'].unique()]
    employee_options = [{'label': employee, 'value': employee} for employee in df['Assigned_to'].unique()]
    start_date = valid_dates.min().date()
    end_date = valid_dates.max().date()

    return company_options, employee_options, start_date, end_date

# Callback to update the dashboard components
@app.callback(
    [Output('total-tickets', 'children'),
     Output('closed-tickets', 'children'),
     Output('new-tickets', 'children'),
     Output('open-tickets', 'children'),
     Output('tickets-by-employee', 'figure'),
     Output('tickets-by-company', 'figure'),
     Output('tickets-by-product', 'figure'),
     Output('ticket-table', 'data'),
     Output('ticket-table', 'columns')],
    [Input('company-filter', 'value'),
     Input('employee-filter', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_dashboard(company_filter, employee_filter, start_date, end_date, contents, filename):
    if not contents:
        return "0", "0", "0", "0", {}, {}, {}, [], []

    # Decode and process the uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))

    # Parse the Last_Activity column
    df['Last_Activity'] = pd.to_datetime(df['Last_Activity'], errors='coerce')
    df = df.dropna(subset=['Last_Activity'])

    # Apply filters
    if company_filter:
        df = df[df['Client'].isin(company_filter)]
    if employee_filter:
        df = df[df['Assigned_to'].isin(employee_filter)]
    if start_date and end_date:
        df = df[(df['Last_Activity'] >= pd.to_datetime(start_date)) & (df['Last_Activity'] <= pd.to_datetime(end_date))]

    total_tickets = len(df)
    closed_tickets = len(df[df['Status'] == 'Closed'])
    new_tickets = len(df[df['Status'] == 'New'])
    open_tickets = len(df[df['Status'] == 'Open'])

    employee_fig = px.bar(df.groupby('Assigned_to').size().reset_index(name='Ticket Count'),
                          x='Ticket Count', y='Assigned_to', title='Tickets by Employee', orientation='h')

    company_fig = px.bar(df.groupby('Client').size().reset_index(name='Ticket Count'),
                         x='Client', y='Ticket Count', title='Tickets by Company')

    product_fig = px.bar(df.groupby('Ticket_Type').size().reset_index(name='Ticket Count'),
                         x='Ticket_Type', y='Ticket Count', title='Tickets by Product')

    table_data = df[['Title']].to_dict('records')
    table_columns = [{'name': 'Title', 'id': 'Title'}]

    return str(total_tickets), str(closed_tickets), str(new_tickets), str(open_tickets), employee_fig, company_fig, product_fig, table_data, table_columns

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
