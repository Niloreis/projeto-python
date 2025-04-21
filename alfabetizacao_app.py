import requests
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# URL da API SIDRA
url = "https://apisidra.ibge.gov.br/values/t/10056/n3/all/v/all/p/all/c58/allxt/c2/6794/c86/95251/d/v3795%202"

# Função para carregar e transformar os dados
def carregar_dados():
    response = requests.get(url)
    data = response.json()
    
    # Cabeçalhos das colunas
    colunas = list(data[0].values())
    dados = [list(d.values()) for d in data[1:]]

    df = pd.DataFrame(dados, columns=colunas)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df

# Carrega os dados
df = carregar_dados()

# Inicializa o app Dash
app = Dash(__name__)
app.title = "Dashboard SIDRA IBGE"

# Layout do app
app.layout = html.Div([
    html.H1("Dashboard SIDRA - IBGE", style={"textAlign": "center"}),

    html.Label("Selecione o Ano:"),
    dcc.Dropdown(
        id='ano-dropdown',
        options=[{"label": ano, "value": ano} for ano in sorted(df["Ano"].unique())],
        value=sorted(df["Ano"].unique())[0]
    ),

    dcc.Graph(id='grafico'),
])

# Callback para atualizar gráfico
@app.callback(
    Output("grafico", "figure"),
    Input("ano-dropdown", "value")
)
def atualizar_dashboard(ano):
    df_filtrado = df[df["Ano"] == ano]

    fig = px.bar(
        df_filtrado,
        x="Unidade da Federação",
        y="Valor",
        color="Sexo",
        barmode="group",
        title=f"Indicador por UF - Ano {ano}",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"]  # Cores fortes e distintas
    )

    fig.update_traces(
        marker_line_color='black', 
        marker_line_width=1
    )

    fig.update_layout(
        xaxis_title="Estado (UF)",
        yaxis_title="Valor",
        font=dict(size=14),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    return fig

# Executa o app
if __name__ == '__main__':
    app.run(debug=True)
