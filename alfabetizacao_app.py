import requests
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# URL da API SIDRA
url = "https://apisidra.ibge.gov.br/values/t/10056/n3/all/v/all/p/all/c58/allxt/c2/6794/c86/95251/d/v3795%202"

def carregar_dados():
    response = requests.get(url)
    data = response.json()
    colunas = list(data[0].values())
    dados = [list(d.values()) for d in data[1:]]
    df = pd.DataFrame(dados, columns=colunas)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df

df = carregar_dados()

app = Dash(__name__)
app.title = "Dashboard sobre a taxa de alfabetização dos estados brasileiros"

app.layout = html.Div([
    html.H1("Dashboard sobre a taxa de alfabetização dos estados brasileiros", style={"textAlign": "center"}),

    html.Label("Selecione o Ano:"),
    dcc.Dropdown(
        id='ano-dropdown',
        options=[{"label": ano, "value": ano} for ano in sorted(df["Ano"].unique())],
        value=sorted(df["Ano"].unique())[0]
    ),

    dcc.Graph(id='grafico')
])

@app.callback(
    Output("grafico", "figure"),
    Input("ano-dropdown", "value")
)
def atualizar_dashboard(ano):
    df_ano = df[df["Ano"] == ano]

    # Total por UF
    totais = (
        df_ano
        .groupby("Unidade da Federação")["Valor"]
        .sum()
        .rename("Total_UF")
        .reset_index()
    )

    # Merge e cálculo da porcentagem
    df_pct = df_ano.merge(totais, on="Unidade da Federação")
    df_pct["Pct"] = (df_pct["Valor"] / df_pct["Total_UF"])

    # Gráfico de barras (%), formatado como porcentagem
    fig = px.bar(
        df_pct,
        x="Unidade da Federação",
        y="Pct",
        barmode="group",
        title=f"% de cada condição por UF – Ano {ano}",
        labels={"Pct": "% do total por UF"}
    )

    # Formatação como porcentagem no eixo y e no hover
    fig.update_layout(
        yaxis_tickformat=".2%",
    )
    fig.update_traces(
        hovertemplate='%{x}<br>%{y:.2%}<extra></extra>'
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
