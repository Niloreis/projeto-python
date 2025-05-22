import requests
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import numpy as np

# Configurações de estilo
COLORS = {
    'background': '#F9F9F9',
    'text': '#333333',
    'primary': '#1F77B4',
    'secondary': '#FF7F0E',
    'accent': '#2CA02C',
    'grid': '#E5E5E5',
    'hover': '#D3D3D3'
}

# URL da API SIDRA para taxa de alfabetização (tabela 10091)
url = "https://apisidra.ibge.gov.br/values/t/10091/n3/all/v/2513/p/all"

def carregar_dados():
    response = requests.get(url)
    data = response.json()
    colunas = list(data[0].values())
    dados = [list(d.values()) for d in data[1:]]
    df = pd.DataFrame(dados, columns=colunas)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    
    # Adicionar região para cada estado
    regioes = {
        'Rondônia': 'Norte', 'Acre': 'Norte', 'Amazonas': 'Norte', 'Roraima': 'Norte',
        'Pará': 'Norte', 'Amapá': 'Norte', 'Tocantins': 'Norte',
        'Maranhão': 'Nordeste', 'Piauí': 'Nordeste', 'Ceará': 'Nordeste',
        'Rio Grande do Norte': 'Nordeste', 'Paraíba': 'Nordeste', 'Pernambuco': 'Nordeste',
        'Alagoas': 'Nordeste', 'Sergipe': 'Nordeste', 'Bahia': 'Nordeste',
        'Minas Gerais': 'Sudeste', 'Espírito Santo': 'Sudeste', 'Rio de Janeiro': 'Sudeste',
        'São Paulo': 'Sudeste',
        'Paraná': 'Sul', 'Santa Catarina': 'Sul', 'Rio Grande do Sul': 'Sul',
        'Mato Grosso do Sul': 'Centro-Oeste', 'Mato Grosso': 'Centro-Oeste',
        'Goiás': 'Centro-Oeste', 'Distrito Federal': 'Centro-Oeste'
    }
    
    df['Região'] = df['Unidade da Federação'].map(regioes)
    
    # Converter valor para decimal (já que vem como percentual)
    df['Taxa'] = df['Valor'] / 100
    
    return df

df = carregar_dados()

# Inicialização do app com tema personalizado
app = Dash(
    __name__, 
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)
app.title = "Dashboard sobre a taxa de alfabetização dos estados brasileiros"

# Layout aprimorado
app.layout = html.Div([
    # Cabeçalho
    html.Div([
        html.H1("Taxa de Alfabetização nos Estados Brasileiros", 
                style={"textAlign": "center", "color": COLORS['text'], "marginBottom": "10px"}),
        html.H4("Análise interativa dos dados de alfabetização por estado e região", 
                style={"textAlign": "center", "color": COLORS['text'], "fontWeight": "normal", "marginTop": "0px"}),
    ], style={"padding": "20px 0", "backgroundColor": COLORS['background']}),
    
    # Filtros e controles
    html.Div([
        html.Div([
            html.Label("Selecione o Ano:", style={"fontWeight": "bold", "color": COLORS['text']}),
            dcc.Dropdown(
                id='ano-dropdown',
                options=[{"label": ano, "value": ano} for ano in sorted(df["Ano"].unique())],
                value=sorted(df["Ano"].unique())[-1],  # Último ano disponível
                clearable=False,
                style={"width": "100%"}
            ),
        ], className="four columns", style={"padding": "10px"}),
        
        html.Div([
            html.Label("Agrupar por:", style={"fontWeight": "bold", "color": COLORS['text']}),
            dcc.RadioItems(
                id='agrupamento-radio',
                options=[
                    {'label': 'Estados', 'value': 'estado'},
                    {'label': 'Regiões', 'value': 'regiao'}
                ],
                value='estado',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={"padding": "10px 0"}
            ),
        ], className="four columns", style={"padding": "10px"}),
        
        html.Div([
            html.Label("Tipo de Visualização:", style={"fontWeight": "bold", "color": COLORS['text']}),
            dcc.RadioItems(
                id='tipo-grafico-radio',
                options=[
                    {'label': 'Barras', 'value': 'barra'},
                    {'label': 'Mapa de Calor', 'value': 'heatmap'},
                    {'label': 'Mapa Geográfico', 'value': 'mapa'}
                ],
                value='barra',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={"padding": "10px 0"}
            ),
        ], className="four columns", style={"padding": "10px"}),
    ], className="row", style={"backgroundColor": "#EAEAEA", "padding": "15px", "borderRadius": "5px", "margin": "20px"}),
    
    # Indicadores principais
    html.Div([
        html.Div(id='indicadores-principais', className="row", style={"margin": "20px 0"}),
    ]),
    
    # Gráfico principal
    html.Div([
        dcc.Loading(
            id="loading-1",
            type="circle",
            children=html.Div(id='grafico-container', style={"height": "600px"})
        ),
    ], style={"padding": "20px", "backgroundColor": COLORS['background'], "borderRadius": "5px", "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)"}),
    
    # Informações adicionais
    html.Div([
        html.H4("Comparação entre Anos", style={"textAlign": "center", "color": COLORS['text']}),
        dcc.Loading(
            id="loading-2",
            type="circle",
            children=html.Div(id='grafico-comparativo', style={"height": "400px"})
        ),
    ], style={"padding": "20px", "backgroundColor": COLORS['background'], "borderRadius": "5px", "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "marginTop": "20px"}),
    
    # Rodapé
    html.Div([
        html.P("Dados obtidos da API SIDRA/IBGE - Dashboard criado com Dash e Plotly", 
               style={"textAlign": "center", "color": "#888888", "fontSize": "12px"})
    ], style={"padding": "20px", "marginTop": "30px"}),
    
    # Armazenamento de dados processados
    dcc.Store(id='dados-processados'),
    
], style={"fontFamily": "Arial, sans-serif", "margin": "0 auto", "maxWidth": "1200px", "padding": "20px"})

# Callback para processar dados
@app.callback(
    Output('dados-processados', 'data'),
    Input('ano-dropdown', 'value')
)
def processar_dados(ano):
    if not ano:
        raise PreventUpdate
    
    df_ano = df[df["Ano"] == ano].copy()
    
    # Calcular médias por região
    df_regiao = df_ano.groupby("Região")["Taxa"].mean().reset_index()
    
    # Preparar dados para retorno
    return {
        'df_uf': df_ano.to_dict('records'),
        'df_regiao': df_regiao.to_dict('records'),
        'media_nacional': df_ano["Taxa"].mean(),
        'max_uf': df_ano["Taxa"].max(),
        'min_uf': df_ano["Taxa"].min(),
        'max_uf_nome': df_ano.loc[df_ano["Taxa"].idxmax(), "Unidade da Federação"],
        'min_uf_nome': df_ano.loc[df_ano["Taxa"].idxmin(), "Unidade da Federação"],
        'ano': ano
    }

# Callback para indicadores principais
@app.callback(
    Output('indicadores-principais', 'children'),
    Input('dados-processados', 'data')
)
def atualizar_indicadores(dados):
    if not dados:
        raise PreventUpdate
    
    # Criar cards de indicadores
    return [
        html.Div([
            html.H4("Média Nacional", style={"textAlign": "center", "margin": "0"}),
            html.H2(f"{dados['media_nacional']:.2%}", style={"textAlign": "center", "color": COLORS['primary'], "margin": "10px 0"})
        ], className="four columns", style={"backgroundColor": "white", "padding": "15px", "borderRadius": "5px", "boxShadow": "0px 0px 5px rgba(0,0,0,0.1)"}),
        
        html.Div([
            html.H4("Maior Taxa", style={"textAlign": "center", "margin": "0"}),
            html.H2(f"{dados['max_uf']:.2%}", style={"textAlign": "center", "color": COLORS['accent'], "margin": "10px 0"}),
            html.P(f"{dados['max_uf_nome']}", style={"textAlign": "center", "fontSize": "14px"})
        ], className="four columns", style={"backgroundColor": "white", "padding": "15px", "borderRadius": "5px", "boxShadow": "0px 0px 5px rgba(0,0,0,0.1)"}),
        
        html.Div([
            html.H4("Menor Taxa", style={"textAlign": "center", "margin": "0"}),
            html.H2(f"{dados['min_uf']:.2%}", style={"textAlign": "center", "color": COLORS['secondary'], "margin": "10px 0"}),
            html.P(f"{dados['min_uf_nome']}", style={"textAlign": "center", "fontSize": "14px"})
        ], className="four columns", style={"backgroundColor": "white", "padding": "15px", "borderRadius": "5px", "boxShadow": "0px 0px 5px rgba(0,0,0,0.1)"})
    ]

# Callback para o gráfico principal
@app.callback(
    Output('grafico-container', 'children'),
    [
        Input('dados-processados', 'data'),
        Input('agrupamento-radio', 'value'),
        Input('tipo-grafico-radio', 'value')
    ]
)
def atualizar_grafico_principal(dados, agrupamento, tipo_grafico):
    if not dados:
        raise PreventUpdate
    
    # Converter dados de volta para DataFrame
    df_uf = pd.DataFrame(dados['df_uf'])
    df_regiao = pd.DataFrame(dados['df_regiao'])
    
    # Escolher DataFrame baseado no agrupamento
    if agrupamento == 'estado':
        df_plot = df_uf
        x_col = "Unidade da Federação"
        title_prefix = "Estados"
    else:
        df_plot = df_regiao
        x_col = "Região"
        title_prefix = "Regiões"
    
    # Escolher tipo de gráfico
    if tipo_grafico == 'barra':
        # Gráfico de barras ordenado
        df_plot = df_plot.sort_values("Taxa", ascending=False)
        
        fig = px.bar(
            df_plot,
            x=x_col,
            y="Taxa",
            color="Taxa",
            color_continuous_scale="Viridis",
            title=f"Taxa de Alfabetização por {title_prefix} - {dados['ano']}",
            labels={"Taxa": "Taxa de Alfabetização", x_col: title_prefix}
        )
        
        # Melhorar aparência
        fig.update_layout(
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font={"color": COLORS['text']},
            yaxis_tickformat=".2%",
            coloraxis_colorbar=dict(title="Taxa"),
            hoverlabel=dict(bgcolor="white", font_size=14),
            margin=dict(l=40, r=40, t=50, b=40),
        )
        
        fig.update_traces(
            hovertemplate='%{x}<br>Taxa: %{y:.2%}<extra></extra>',
            marker_line_color='white',
            marker_line_width=1.5,
            opacity=0.8
        )
        
    elif tipo_grafico == 'heatmap':
        # Preparar dados para heatmap
        if agrupamento == 'estado':
            # Reorganizar para ter UFs nas linhas e variáveis nas colunas
            pivot_df = df_plot.pivot_table(
                index=x_col, 
                values="Taxa", 
                aggfunc='mean'
            ).reset_index()
            
            # Ordenar por valor
            pivot_df = pivot_df.sort_values("Taxa", ascending=False)
            
            # Criar heatmap
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df["Taxa"].values.reshape(-1, 1),
                x=["Taxa de Alfabetização"],
                y=pivot_df[x_col],
                colorscale="Viridis",
                text=[[f"{val:.2%}"] for val in pivot_df["Taxa"]],
                texttemplate="%{text}",
                showscale=True,
                colorbar=dict(title="Taxa")
            ))
            
        else:
            # Para regiões, criar um heatmap mais simples
            pivot_df = df_plot.pivot_table(
                index=x_col, 
                values="Taxa", 
                aggfunc='mean'
            ).reset_index()
            
            # Ordenar por valor
            pivot_df = pivot_df.sort_values("Taxa", ascending=False)
            
            # Criar heatmap
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df["Taxa"].values.reshape(-1, 1),
                x=["Taxa de Alfabetização"],
                y=pivot_df[x_col],
                colorscale="Viridis",
                text=[[f"{val:.2%}"] for val in pivot_df["Taxa"]],
                texttemplate="%{text}",
                showscale=True,
                colorbar=dict(title="Taxa")
            ))
        
        fig.update_layout(
            title=f"Mapa de Calor da Taxa de Alfabetização por {title_prefix} - {dados['ano']}",
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font={"color": COLORS['text']},
            margin=dict(l=100, r=40, t=50, b=40),
        )
        
    elif tipo_grafico == 'mapa':
        # Para mapa geográfico, precisamos de um gráfico choropleth
        # Como não temos os dados geográficos completos, vamos criar um gráfico de dispersão com tamanho dos pontos
        
        # Coordenadas aproximadas dos estados (centróides)
        coordenadas = {
            'Acre': [-9.0, -70.0], 'Alagoas': [-9.5, -36.5], 'Amapá': [1.0, -52.0],
            'Amazonas': [-3.5, -65.0], 'Bahia': [-12.5, -41.7], 'Ceará': [-5.0, -39.0],
            'Distrito Federal': [-15.8, -47.9], 'Espírito Santo': [-19.6, -40.5],
            'Goiás': [-16.0, -49.0], 'Maranhão': [-5.0, -45.0], 'Mato Grosso': [-13.0, -56.0],
            'Mato Grosso do Sul': [-20.5, -55.0], 'Minas Gerais': [-18.0, -44.0],
            'Pará': [-3.0, -53.0], 'Paraíba': [-7.0, -36.0], 'Paraná': [-24.5, -51.5],
            'Pernambuco': [-8.5, -37.5], 'Piauí': [-7.0, -42.0], 'Rio de Janeiro': [-22.0, -43.2],
            'Rio Grande do Norte': [-5.5, -36.5], 'Rio Grande do Sul': [-30.0, -53.0],
            'Rondônia': [-10.5, -63.0], 'Roraima': [2.0, -61.5], 'Santa Catarina': [-27.0, -50.5],
            'São Paulo': [-22.0, -48.0], 'Sergipe': [-10.5, -37.5], 'Tocantins': [-10.0, -48.0]
        }
        
        # Adicionar coordenadas ao DataFrame
        if agrupamento == 'estado':
            df_map = df_plot.copy()
            df_map['lat'] = df_map[x_col].map(lambda x: coordenadas.get(x, [0, 0])[0])
            df_map['lon'] = df_map[x_col].map(lambda x: coordenadas.get(x, [0, 0])[1])
            
            # Criar mapa
            fig = px.scatter_geo(
                df_map,
                lat='lat',
                lon='lon',
                size='Taxa',
                color='Taxa',
                hover_name=x_col,
                size_max=30,
                color_continuous_scale="Viridis",
                title=f"Distribuição Geográfica da Taxa de Alfabetização - {dados['ano']}",
                projection="mercator",
                scope="south america",
                labels={"Taxa": "Taxa de Alfabetização"}
            )
            
            # Adicionar texto aos pontos
            fig.update_traces(
                text=df_map[x_col],
                hovertemplate='<b>%{hovertext}</b><br>Taxa: %{marker.color:.2%}<extra></extra>'
            )
            
        else:
            # Para regiões, criar um gráfico de barras com cores por região
            fig = px.bar(
                df_regiao,
                x=x_col,
                y="Taxa",
                color=x_col,
                title=f"Taxa de Alfabetização por {title_prefix} - {dados['ano']}",
                labels={"Taxa": "Taxa de Alfabetização", x_col: "Região"}
            )
            
            fig.update_layout(
                showlegend=False,
                yaxis_tickformat=".2%",
            )
            
            fig.update_traces(
                hovertemplate='%{x}<br>Taxa: %{y:.2%}<extra></extra>',
                marker_line_color='white',
                marker_line_width=1.5,
                opacity=0.8
            )
        
        fig.update_layout(
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font={"color": COLORS['text']},
            margin=dict(l=40, r=40, t=50, b=40),
        )
    
    return dcc.Graph(figure=fig, style={"height": "100%"})

# Callback para o gráfico comparativo
@app.callback(
    Output('grafico-comparativo', 'children'),
    [
        Input('agrupamento-radio', 'value'),
        Input('ano-dropdown', 'value')
    ]
)
def atualizar_grafico_comparativo(agrupamento, ano_selecionado):
    # Obter todos os anos disponíveis
    anos = sorted(df["Ano"].unique())
    
    # Garantir que temos pelo menos 2 anos para comparar
    if len(anos) < 2:
        return html.Div("Dados insuficientes para comparação entre anos")
    
    # Selecionar o ano atual e o anterior para comparação
    if ano_selecionado in anos and anos.index(ano_selecionado) > 0:
        ano_anterior = anos[anos.index(ano_selecionado) - 1]
    else:
        # Se não for possível, usar os dois últimos anos
        ano_anterior = anos[-2]
        ano_selecionado = anos[-1]
    
    # Filtrar dados para os dois anos
    df_atual = df[df["Ano"] == ano_selecionado]
    df_anterior = df[df["Ano"] == ano_anterior]
    
    # Agrupar por UF ou região conforme selecionado
    if agrupamento == 'estado':
        grupo = "Unidade da Federação"
    else:
        grupo = "Região"
    
    # Calcular médias para cada ano
    medias_atual = df_atual.groupby(grupo)["Taxa"].mean().reset_index()
    medias_anterior = df_anterior.groupby(grupo)["Taxa"].mean().reset_index()
    
    # Mesclar os dados
    medias_comparacao = medias_atual.merge(
        medias_anterior, 
        on=grupo, 
        suffixes=(f'_{ano_selecionado}', f'_{ano_anterior}')
    )
    
    # Calcular variação percentual
    medias_comparacao['variacao'] = (
        (medias_comparacao[f'Taxa_{ano_selecionado}'] - medias_comparacao[f'Taxa_{ano_anterior}']) / 
        medias_comparacao[f'Taxa_{ano_anterior}']
    ) * 100
    
    # Ordenar por variação
    medias_comparacao = medias_comparacao.sort_values('variacao', ascending=False)
    
    # Criar gráfico de barras para comparação
    fig = go.Figure()
    
    # Adicionar barras para cada ano
    fig.add_trace(go.Bar(
        x=medias_comparacao[grupo],
        y=medias_comparacao[f'Taxa_{ano_anterior}'],
        name=f'Ano {ano_anterior}',
        marker_color=COLORS['secondary'],
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=medias_comparacao[grupo],
        y=medias_comparacao[f'Taxa_{ano_selecionado}'],
        name=f'Ano {ano_selecionado}',
        marker_color=COLORS['primary'],
        opacity=0.9
    ))
    
    # Adicionar linha de variação percentual
    fig.add_trace(go.Scatter(
        x=medias_comparacao[grupo],
        y=medias_comparacao['variacao'],
        mode='lines+markers',
        name='Variação (%)',
        yaxis='y2',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8)
    ))
    
    # Configurar layout com eixo Y secundário
    fig.update_layout(
        title=f"Comparação entre {ano_anterior} e {ano_selecionado}",
        barmode='group',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font={"color": COLORS['text']},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            title="Taxa de Alfabetização",
            side="left",
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickformat=".2%"
        ),
        yaxis2=dict(
            title="Variação (%)",
            side="right",
            overlaying="y",
            showgrid=False,
            zeroline=False
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x unified"
    )
    
    return dcc.Graph(figure=fig, style={"height": "100%"})

# Adicionar CSS externo para responsividade
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
      app.run(debug=True)
