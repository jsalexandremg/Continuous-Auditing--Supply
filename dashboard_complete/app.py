import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

# --- Configuration ---
original_file = "/home/ubuntu/upload/Base Dados v2.XLSX"
suspect_file = "/home/ubuntu/suspect_skus_for_external_check.csv"

# --- Data Loading and Preparation ---
# Load original data
df_orig = pd.read_excel(original_file, sheet_name=0)
df_orig['Quantidade'] = pd.to_numeric(df_orig['Quantidade'], errors='coerce')
df_orig['Valor Liquido'] = pd.to_numeric(df_orig['Valor Liquido'], errors='coerce')
df_orig.dropna(subset=['Quantidade', 'Valor Liquido', 'SKU', 'Centro'], inplace=True)
df_orig = df_orig[df_orig['Quantidade'] > 0]
df_orig = df_orig[df_orig['Valor Liquido'] >= 0]
df_orig['Preco_Unitario'] = df_orig['Valor Liquido'] / df_orig['Quantidade']
df_orig['Data Doc.'] = pd.to_datetime(df_orig['Data Doc.'], errors='coerce')

# Load suspect SKUs data
df_suspect = pd.read_csv(suspect_file)
# Sort suspects for relevance
df_suspect.sort_values(by=['Num_Outliers_IQR', 'CV_Percent'], ascending=False, inplace=True)

# External price comparison data (hardcoded based on external_price_notes.md)
comparison_data = {
    'SKU': [
        '00-060.742',
        '00-013.991',
        '00-050.758',
        '00-013.992'
    ],
    'Descrição': [
        'LINGUICA MINEIRA 0,8KG CX 6,4 KG',
        '8947 FILE PEITO DESF TEMP 400GCX12KG UNI',
        '8943 LASANHA A BOLONHESA 600G CX 6KG UNI',
        '8949 FILE PEITO DESFIADO 4KG CX 16KG UNI'
    ],
    'Centro': [
        'CDF2',
        'CDUA',
        'CDUA',
        'CDUA'
    ],
    'Preço Médio Interno (R$)': [
        10.78,  # R$ 69.02 / 6.4kg
        268.70,  # Assumed unit, likely incorrect
        68.56,  # Assumed unit, likely incorrect
        339.79  # Assumed unit, likely incorrect
    ],
    'Referência Externa (R$)': [
        23.99,  # Paxa 1kg
        13.99,  # Atacado Vem 400g (lowest found)
        15.40,  # Paulistao 600g (lowest found)
        134.25  # Eficaz 4kg
    ],
    'Observação': [
        'Variação interna alta, min R$2.42/kg',
        'Discrepância ENORME - Verificar unidade/qtd interna',
        'Discrepância ENORME - Verificar unidade/qtd interna',
        'Discrepância ENORME - Verificar unidade/qtd interna'
    ]
}
df_comp = pd.DataFrame(comparison_data)

# Get unique values for filters
centros = sorted(df_orig['Centro'].unique())
skus = sorted(df_orig['SKU'].unique())
fornecedores = sorted(df_orig['Fornecedor'].unique())
grupos_servico = sorted(df_orig['Grp. Mercadoria'].dropna().unique())
descricoes_grupo = sorted(df_orig['Descrição.1'].dropna().unique())

# --- Initialize Dash App ---
app = dash.Dash(__name__, 
                external_stylesheets=[
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
                ])
server = app.server

# --- App Layout ---
app.layout = html.Div([
    html.Div([
        html.H1("Dashboard de Análise de Preços", className="text-center my-4"),
        html.P("Análise de variação de preços e identificação de possíveis sobrepreços por SKU e Centro", 
               className="text-center text-muted mb-4"),
    ], className="container"),
    
    # Filters Section
    html.Div([
        html.Div([
            html.H4("Filtros", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Centro:"),
                    dcc.Dropdown(
                        id='centro-filter',
                        options=[{'label': c, 'value': c} for c in centros],
                        multi=True,
                        placeholder="Selecione um ou mais Centros"
                    ),
                ], className="col-md-4"),
                html.Div([
                    html.Label("SKU:"),
                    dcc.Dropdown(
                        id='sku-filter',
                        options=[{'label': s, 'value': s} for s in skus],
                        multi=True,
                        placeholder="Selecione um ou mais SKUs"
                    ),
                ], className="col-md-4"),
                html.Div([
                    html.Label("Fornecedor:"),
                    dcc.Dropdown(
                        id='fornecedor-filter',
                        options=[{'label': f, 'value': f} for f in fornecedores],
                        multi=True,
                        placeholder="Selecione um ou mais Fornecedores"
                    ),
                ], className="col-md-4"),
            ], className="row mb-3"),
            html.Div([
                html.Div([
                    html.Label("Grupo de Mercadoria:"),
                    dcc.Dropdown(
                        id='grupo-filter',
                        options=[{'label': g, 'value': g} for g in grupos_servico],
                        multi=True,
                        placeholder="Selecione um ou mais Grupos"
                    ),
                ], className="col-md-6"),
                html.Div([
                    html.Label("Descrição do Grupo:"),
                    dcc.Dropdown(
                        id='desc-grupo-filter',
                        options=[{'label': d, 'value': d} for d in descricoes_grupo],
                        multi=True,
                        placeholder="Selecione uma ou mais Descrições"
                    ),
                ], className="col-md-6"),
            ], className="row mb-3"),
            html.Div([
                html.Div([
                    html.Label("Período:"),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=df_orig['Data Doc.'].min(),
                        max_date_allowed=df_orig['Data Doc.'].max(),
                        start_date=df_orig['Data Doc.'].min(),
                        end_date=df_orig['Data Doc.'].max(),
                        display_format='DD/MM/YYYY'
                    ),
                ], className="col-md-6"),
                html.Div([
                    html.Label("Mostrar apenas SKUs suspeitos:"),
                    dcc.RadioItems(
                        id='only-suspects',
                        options=[
                            {'label': 'Sim', 'value': 'yes'},
                            {'label': 'Não', 'value': 'no'}
                        ],
                        value='no',
                        inline=True
                    ),
                ], className="col-md-6"),
            ], className="row mb-3"),
            html.Div([
                html.Button("Aplicar Filtros", id="apply-filters", className="btn btn-primary mr-2"),
                html.Button("Limpar Filtros", id="clear-filters", className="btn btn-secondary")
            ], className="text-right")
        ], className="p-4 bg-light rounded shadow-sm")
    ], className="container mb-4"),
    
    # Dashboard Tabs
    html.Div([
        dcc.Tabs([
            # Tab 1: Overview
            dcc.Tab(label="Visão Geral", children=[
                html.Div([
                    html.H4("Gastos por Centro", className="mt-4 mb-3"),
                    dcc.Graph(id='centro-spending-chart'),
                    
                    html.H4("Distribuição de Preço Unitário", className="mt-4 mb-3"),
                    dcc.Graph(id='price-distribution-chart'),
                    
                    html.H4("Evolução de Preço ao Longo do Tempo", className="mt-4 mb-3"),
                    dcc.Graph(id='price-time-chart'),
                ], className="p-3")
            ]),
            
            # Tab 2: Suspect Analysis
            dcc.Tab(label="Análise de Suspeitos", children=[
                html.Div([
                    html.H4("SKUs/Centros Suspeitos", className="mt-4 mb-3"),
                    html.Div(id='suspect-table-container', className="mb-4"),
                    
                    html.H4("Comparação: Preço Interno vs. Referência Externa", className="mt-4 mb-3"),
                    dcc.Graph(id='internal-external-comparison'),
                    
                    html.H4("Detalhes de Outliers", className="mt-4 mb-3"),
                    html.Div(id='outlier-details-container')
                ], className="p-3")
            ]),
            
            # Tab 3: Detailed Data
            dcc.Tab(label="Dados Detalhados", children=[
                html.Div([
                    html.H4("Transações Filtradas", className="mt-4 mb-3"),
                    html.Div(id='filtered-data-container', className="mb-4"),
                    
                    html.Div([
                        html.Button("Exportar CSV", id="export-csv", className="btn btn-success")
                    ], className="text-right mb-3"),
                    
                    html.Div(id='export-notification', className="alert alert-success", style={'display': 'none'})
                ], className="p-3")
            ]),
        ])
    ], className="container mb-5"),
    
    # Footer
    html.Footer([
        html.P("Dashboard de Análise de Preços - Desenvolvido para análise de possíveis sobrepreços", 
               className="text-center text-muted")
    ], className="container py-3")
])

# --- Callbacks ---

# Filter data based on user selections
@app.callback(
    Output('filtered-data', 'data'),
    Input('apply-filters', 'n_clicks'),
    State('centro-filter', 'value'),
    State('sku-filter', 'value'),
    State('fornecedor-filter', 'value'),
    State('grupo-filter', 'value'),
    State('desc-grupo-filter', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('only-suspects', 'value'),
    prevent_initial_call=True
)
def filter_data(n_clicks, centros, skus, fornecedores, grupos, desc_grupos, start_date, end_date, only_suspects):
    # Start with the original dataframe
    filtered_df = df_orig.copy()
    
    # Apply filters
    if centros and len(centros) > 0:
        filtered_df = filtered_df[filtered_df['Centro'].isin(centros)]
    
    if skus and len(skus) > 0:
        filtered_df = filtered_df[filtered_df['SKU'].isin(skus)]
    
    if fornecedores and len(fornecedores) > 0:
        filtered_df = filtered_df[filtered_df['Fornecedor'].isin(fornecedores)]
    
    # Apply new group filters
    if grupos and len(grupos) > 0:
        filtered_df = filtered_df[filtered_df['Grp. Mercadoria'].isin(grupos)]
    
    if desc_grupos and len(desc_grupos) > 0:
        filtered_df = filtered_df[filtered_df['Descrição.1'].isin(desc_grupos)]
    
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Data Doc.'] >= start_date) & 
                                 (filtered_df['Data Doc.'] <= end_date)]
    
    # Filter for only suspect SKUs if selected
    if only_suspects == 'yes':
        suspect_skus_centros = [(row['SKU'], row['Centro']) for _, row in df_suspect.iterrows()]
        filtered_df = filtered_df[filtered_df.apply(lambda row: (row['SKU'], row['Centro']) in suspect_skus_centros, axis=1)]
    
    return filtered_df.to_dict('records')

# Clear filters
@app.callback(
    [Output('centro-filter', 'value'),
     Output('sku-filter', 'value'),
     Output('fornecedor-filter', 'value'),
     Output('grupo-filter', 'value'),
     Output('desc-grupo-filter', 'value'),
     Output('date-range', 'start_date'),
     Output('date-range', 'end_date'),
     Output('only-suspects', 'value')],
    Input('clear-filters', 'n_clicks'),
    prevent_initial_call=True
)
def clear_filters(n_clicks):
    return None, None, None, None, None, df_orig['Data Doc.'].min(), df_orig['Data Doc.'].max(), 'no'

# Update Centro Spending Chart
@app.callback(
    Output('centro-spending-chart', 'figure'),
    Input('filtered-data', 'data')
)
def update_centro_spending(data):
    if not data:
        # Return empty figure if no data
        return go.Figure()
    
    df = pd.DataFrame(data)
    centro_spending = df.groupby('Centro')['Valor Liquido'].sum().reset_index().sort_values('Valor Liquido', ascending=False)
    
    fig = px.bar(
        centro_spending, 
        x='Centro', 
        y='Valor Liquido',
        title='Gasto Total por Centro',
        labels={'Valor Liquido': 'Valor Líquido Total (R$)', 'Centro': 'Centro'},
        color='Valor Liquido',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title='Centro',
        yaxis_title='Valor Líquido Total (R$)',
        yaxis_tickformat=',.2f',
        coloraxis_showscale=False
    )
    
    return fig

# Update Price Distribution Chart
@app.callback(
    Output('price-distribution-chart', 'figure'),
    Input('filtered-data', 'data')
)
def update_price_distribution(data):
    if not data:
        # Return empty figure if no data
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    # Group by SKU and Centro
    grouped = df.groupby(['SKU', 'Centro'])
    
    # Get top 10 SKU/Centro combinations by number of transactions
    top_groups = grouped.size().reset_index(name='count').sort_values('count', ascending=False).head(10)
    
    # Create box plots for these top groups
    fig = go.Figure()
    
    for _, row in top_groups.iterrows():
        sku, centro = row['SKU'], row['Centro']
        group_data = df[(df['SKU'] == sku) & (df['Centro'] == centro)]
        
        # Get a short description (first 20 chars)
        desc = group_data['Descrição'].iloc[0][:20] + '...' if len(group_data['Descrição'].iloc[0]) > 20 else group_data['Descrição'].iloc[0]
        
        fig.add_trace(go.Box(
            y=group_data['Preco_Unitario'],
            name=f"{sku} ({centro})<br>{desc}",
            boxpoints='outliers'
        ))
    
    fig.update_layout(
        title='Distribuição de Preço Unitário (Top 10 SKU/Centro por volume)',
        yaxis_title='Preço Unitário (R$)',
        showlegend=False,
        height=500
    )
    
    return fig

# Update Price Time Chart
@app.callback(
    Output('price-time-chart', 'figure'),
    Input('filtered-data', 'data')
)
def update_price_time_chart(data):
    if not data:
        # Return empty figure if no data
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    # Ensure data is sorted by date
    df = df.sort_values('Data Doc.')
    
    # Group by SKU, Centro and Date
    df['Mês'] = df['Data Doc.'].dt.to_period('M').astype(str)
    
    # Get top 5 SKU/Centro combinations by number of transactions
    top_groups = df.groupby(['SKU', 'Centro']).size().reset_index(name='count').sort_values('count', ascending=False).head(5)
    
    fig = go.Figure()
    
    for _, row in top_groups.iterrows():
        sku, centro = row['SKU'], row['Centro']
        group_data = df[(df['SKU'] == sku) & (df['Centro'] == centro)]
        
        # Calculate monthly average price
        monthly_avg = group_data.groupby('Mês')['Preco_Unitario'].mean().reset_index()
        
        # Get a short description
        desc = group_data['Descrição'].iloc[0][:15] + '...' if len(group_data['Descrição'].iloc[0]) > 15 else group_data['Descrição'].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=monthly_avg['Mês'],
            y=monthly_avg['Preco_Unitario'],
            mode='lines+markers',
            name=f"{sku} ({centro}) - {desc}"
        ))
    
    fig.update_layout(
        title='Evolução do Preço Unitário Médio Mensal (Top 5 SKU/Centro por volume)',
        xaxis_title='Mês',
        yaxis_title='Preço Unitário Médio (R$)',
        legend_title='SKU (Centro)',
        height=500
    )
    
    return fig

# Update Suspect Table
@app.callback(
    Output('suspect-table-container', 'children'),
    Input('filtered-data', 'data')
)
def update_suspect_table(data):
    if not data:
        return html.Div("Nenhum dado disponível com os filtros atuais.")
    
    df = pd.DataFrame(data)
    
    # Get unique SKU/Centro combinations in filtered data
    filtered_sku_centro = set(zip(df['SKU'], df['Centro']))
    
    # Filter suspect dataframe to only show those in the filtered data
    filtered_suspects = df_suspect[df_suspect.apply(lambda row: (row['SKU'], row['Centro']) in filtered_sku_centro, axis=1)]
    
    if len(filtered_suspects) == 0:
        return html.Div("Nenhum SKU/Centro suspeito encontrado com os filtros atuais.")
    
    # Prepare data for table
    table_data = filtered_suspects[['SKU', 'Centro', 'Descrição', 'Num_Compras', 'Preco_Medio', 
                                   'Preco_Min', 'Preco_Max', 'CV_Percent', 'Num_Outliers_IQR', 'Motivo_Suspeita']]
    
    # Rename columns for better display
    table_data = table_data.rename(columns={
        'Num_Compras': 'Nº Compras',
        'Preco_Medio': 'Preço Médio (R$)',
        'Preco_Min': 'Preço Mín (R$)',
        'Preco_Max': 'Preço Máx (R$)',
        'CV_Percent': 'CV (%)',
        'Num_Outliers_IQR': 'Nº Outliers',
        'Motivo_Suspeita': 'Motivo Suspeita'
    })
    
    return dash_table.DataTable(
        id='suspect-table',
        columns=[{"name": col, "id": col} for col in table_data.columns],
        data=table_data.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        sort_action='native',
        filter_action='native',
        page_size=10
    )

# Update Internal vs External Comparison
@app.callback(
    Output('internal-external-comparison', 'figure'),
    Input('filtered-data', 'data')
)
def update_comparison_chart(data):
    # This chart uses the hardcoded comparison data
    fig = go.Figure(data=[
        go.Bar(name='Preço Médio Interno', x=df_comp['SKU'] + ' - ' + df_comp['Descrição'].str[:20], 
               y=df_comp['Preço Médio Interno (R$)'], 
               text=df_comp['Preço Médio Interno (R$)'].apply(lambda x: f'R$ {x:,.2f}'), 
               textposition='auto'),
        go.Bar(name='Referência Externa', x=df_comp['SKU'] + ' - ' + df_comp['Descrição'].str[:20], 
               y=df_comp['Referência Externa (R$)'], 
               text=df_comp['Referência Externa (R$)'].apply(lambda x: f'R$ {x:,.2f}'), 
               textposition='auto')
    ])
    
    fig.update_layout(
        barmode='group',
        title='Comparação: Preço Médio Interno vs. Referência Externa',
        xaxis_title='SKU - Descrição',
        yaxis_title='Preço (R$)',
        legend_title='Fonte do Preço',
        height=500
    )
    
    # Add annotations for observations
    annotations = []
    for i, obs in enumerate(df_comp['Observação']):
        annotations.append(dict(
            x=df_comp['SKU'][i] + ' - ' + df_comp['Descrição'][i][:20],
            y=-30,  # Position below x-axis
            xref='x',
            yref='y',
            text=f"Obs: {obs}",
            showarrow=False,
            font=dict(size=10),
            align='center'
        ))
    
    fig.update_layout(annotations=annotations, margin=dict(b=150))
    
    return fig

# Update Outlier Details
@app.callback(
    Output('outlier-details-container', 'children'),
    Input('filtered-data', 'data')
)
def update_outlier_details(data):
    if not data:
        return html.Div("Nenhum dado disponível com os filtros atuais.")
    
    df = pd.DataFrame(data)
    
    # Get unique SKU/Centro combinations in filtered data
    filtered_sku_centro = set(zip(df['SKU'], df['Centro']))
    
    # Filter suspect dataframe to only show those in the filtered data
    filtered_suspects = df_suspect[df_suspect.apply(lambda row: (row['SKU'], row['Centro']) in filtered_sku_centro, axis=1)]
    
    if len(filtered_suspects) == 0:
        return html.Div("Nenhum SKU/Centro suspeito encontrado com os filtros atuais.")
    
    # Get top 3 suspects by number of outliers
    top_suspects = filtered_suspects.sort_values('Num_Outliers_IQR', ascending=False).head(3)
    
    outlier_details = []
    
    for _, suspect in top_suspects.iterrows():
        sku, centro = suspect['SKU'], suspect['Centro']
        
        # Get data for this SKU/Centro
        sku_data = df[(df['SKU'] == sku) & (df['Centro'] == centro)]
        
        if len(sku_data) == 0:
            continue
        
        # Calculate IQR for outlier detection
        Q1 = sku_data['Preco_Unitario'].quantile(0.25)
        Q3 = sku_data['Preco_Unitario'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify outliers
        outliers = sku_data[(sku_data['Preco_Unitario'] < lower_bound) | (sku_data['Preco_Unitario'] > upper_bound)]
        
        if len(outliers) == 0:
            continue
        
        # Create a section for this SKU/Centro
        section = html.Div([
            html.H5(f"SKU: {sku} | Centro: {centro} | {suspect['Descrição'][:30]}..."),
            html.P(f"Preço Médio: R$ {suspect['Preco_Medio']:.2f} | Outliers: {len(outliers)} de {len(sku_data)} transações"),
            
            # Table with outlier details
            dash_table.DataTable(
                columns=[
                    {"name": "Nº Pedido", "id": "Nº Pedido"},
                    {"name": "Data", "id": "Data Doc."},
                    {"name": "Fornecedor", "id": "Fornecedor"},
                    {"name": "Quantidade", "id": "Quantidade"},
                    {"name": "Valor Líquido", "id": "Valor Liquido"},
                    {"name": "Preço Unitário", "id": "Preco_Unitario"}
                ],
                data=outliers[['Nº Pedido', 'Data Doc.', 'Fornecedor', 'Quantidade', 'Valor Liquido', 'Preco_Unitario']].to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                page_size=5
            ),
            html.Hr()
        ])
        
        outlier_details.append(section)
    
    if not outlier_details:
        return html.Div("Nenhum outlier encontrado nos SKUs/Centros filtrados.")
    
    return html.Div(outlier_details)

# Update Filtered Data Table
@app.callback(
    Output('filtered-data-container', 'children'),
    Input('filtered-data', 'data')
)
def update_filtered_data_table(data):
    if not data:
        return html.Div("Nenhum dado disponível com os filtros atuais.")
    
    df = pd.DataFrame(data)
    
    # Limit to 1000 rows for performance
    if len(df) > 1000:
        df = df.sample(1000)
        note = html.Div("Nota: Mostrando uma amostra aleatória de 1000 linhas para melhor performance.", 
                       className="text-muted mb-2")
    else:
        note = html.Div(f"Mostrando {len(df)} transações.", className="text-muted mb-2")
    
    # Select columns to display
    display_cols = ['Nº Pedido', 'Item', 'Data Doc.', 'SKU', 'Descrição', 'UN', 'Centro', 
                   'Quantidade', 'Valor Liquido', 'Preco_Unitario', 'Fornecedor']
    
    table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in display_cols],
        data=df[display_cols].to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '5px',
            'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        sort_action='native',
        filter_action='native',
        page_size=20
    )
    
    return html.Div([note, table])

# Export CSV callback
@app.callback(
    Output('export-notification', 'style'),
    Input('export-csv', 'n_clicks'),
    State('filtered-data', 'data'),
    prevent_initial_call=True
)
def export_csv(n_clicks, data):
    if not data:
        return {'display': 'none'}
    
    df = pd.DataFrame(data)
    
    # Export to CSV
    export_path = os.path.join('/home/ubuntu', 'exported_data.csv')
    df.to_csv(export_path, index=False, encoding='utf-8-sig')
    
    return {'display': 'block'}

# Store filtered data
app.clientside_callback(
    """
    function(data) {
        return data;
    }
    """,
    Output('filtered-data', 'data'),
    Input('filtered-data', 'data')
)

# Add a hidden div to store filtered data
app.layout.children.append(html.Div(id='filtered-data', style={'display': 'none'}))

# --- Run the app ---
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
