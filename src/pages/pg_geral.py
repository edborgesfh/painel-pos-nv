import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date

from functools import lru_cache

# Estilo

# Para os Gráficos
grafico_config = {
    "showlegend": False,
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    "margin": {"pad": 0},
    "margin_b": 60,
    "font_color": "#D3D3D3",
}

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path='/visaogeral',
)

# dataset
df_cursos = pd.read_csv('data/df_cursos.csv')
df_cursos['data final'] = pd.to_datetime(df_cursos['data final'], format='ISO8601')
df_cursos['data inicial'] = pd.to_datetime(df_cursos['data inicial'], format='ISO8601')

prog_aulas_curso = pd.read_csv('data/prog_aulas_curso.csv')
prog_aulas_curso['data final'] = pd.to_datetime(prog_aulas_curso['data final'], format='ISO8601')

@lru_cache(maxsize=32)
def grafico_geral(curso_selecionado):
    prog_aulas_curso_filtrado = prog_aulas_curso.copy()
    if curso_selecionado:
        prog_aulas_curso_filtrado = prog_aulas_curso[prog_aulas_curso['curso'].isin(curso_selecionado)]

    data_min = prog_aulas_curso['data final'].min()
    data_max = date.today()

    cores_cursos = {
        'Gestão e Controle de Negócios': '#ff5c00',
        'Gestão de Recursos Humanos': '#FF0023',
        'Qualidade e Tecnologias da Carne': '#DB00FF'
    }

    # Plotagem do gráfico
    g_geral = px.line(prog_aulas_curso_filtrado,
                      height=600,
                      x='data final',
                      y='progresso_acumulado',
                      color='curso',
                      hover_data={'Aula': True},
                      color_discrete_map=cores_cursos
                      )

    g_geral.update_layout(grafico_config, showlegend=True,
                          legend=dict(orientation='h', title='Cursos', yanchor='bottom',
                                      y=1, xanchor='right', x=1),
                          )

    g_geral.update_yaxes(title='Aulas Finalizadas', showgrid=False)
    g_geral.update_xaxes(title='Seletor de intervalo', gridcolor='rgba(255, 255, 255, 0.04)',
                         autorange=False, range=[data_min, data_max],
                         rangeslider=dict(visible=True, thickness=0.07),
                         rangeselector=dict(buttons=list([
                             dict(count=1, label='mês', step='month', stepmode='todate', ),
                             dict(count=6, label='semestre', step='month', stepmode='todate'),
                             dict(count=1, label='ano', step='year', stepmode='todate'),
                             dict(count=1, label='todo', step='all')]),
                             bgcolor='rgba(0, 0, 0, 0)', activecolor='#007eff')
                         )
    g_geral.update_traces(mode='lines+markers',
                          customdata=np.stack(
                              (prog_aulas_curso['curso'], prog_aulas_curso['Módulo'], prog_aulas_curso['Aula']),
                              axis=-1),
                          hovertemplate='Módulo %{customdata[1]}<br>'
                                        'Aula: %{customdata[2]}<br>'
                                        'Concluída em %{x}<br>'
                          )

    return g_geral.to_dict()

# layout
layout = dbc.Container(
    [
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2(
                                    'Visão Geral',  # titulo
                                    className='title',
                                ),
                            ], width=5,
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(id='filtro-cursos',  # filtro
                                             options=[{'label': curso, 'value': curso}
                                                      for curso in df_cursos['curso'].unique()],
                                             placeholder='Selecione o Curso',
                                             value=None,
                                             multi=True,
                                             searchable=True,
                                             className='dropdown',
                                             ),
                            ], width=7,
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id='g-geral',
                                    # config={'displayModeBar': False},
                                    # className='chart-card',
                                    style={'height': '580px'},
                                ),
                                type='circle',
                                color='#f79500',
                            ),
                        ),
                    ],
                ),
            ],
            className='page-content',
        ),
    ],
    fluid=True,
)

# callback cards and graphs

@callback(
        Output('g-geral', 'figure'),
        Input('filtro-cursos', 'value'),
)
def atualizar_grafico_geral(curso_selecionado):
    # Usando a função com cache
    return grafico_geral(tuple(curso_selecionado) if curso_selecionado else None)
