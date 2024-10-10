import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
# from utils.functions import create_card
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
    path='/gcn',
)

# dataset
df_cursos = pd.read_csv('data/df_cursos.csv')

df_cursos['data final'] = pd.to_datetime(df_cursos['data final'], format='ISO8601')
df_cursos['data inicial'] = pd.to_datetime(df_cursos['data inicial'], format='ISO8601')

df_gcn = df_cursos[df_cursos['curso'] == 'Gestão e Controle de Negócios']

# Cache e funções de gráficos
@lru_cache(maxsize=32)
def update_graphs(modulo_selecionado):
    gcn_filtrado = df_gcn.copy()
    if modulo_selecionado:
        gcn_filtrado = gcn_filtrado[gcn_filtrado['Módulo'].isin(modulo_selecionado)]

# Operação com o df para gerar o gráfico
    data_minima = gcn_filtrado['data inicial'].min()
    data_maxima = date.today()

# Plotagem do gráfico
    gcn_gantt = px.timeline(gcn_filtrado,
                            x_start='data inicial',
                            x_end='data final',
                            y='ID',
                            color='progresso',
                            color_continuous_scale=['#ffd700', '#FF0023'],)
    gcn_gantt.update_layout(grafico_config, title={'text': 'Linha do tempo — Produção das Aulas', 'x': 0.5})
    gcn_gantt.update_yaxes(autorange='reversed', title='Aulas',)
    gcn_gantt.update_xaxes(title='Seletor de intervalo', gridcolor='rgba(255, 255, 255, 0.04)',
                           autorange=False, range=[data_minima, data_maxima],
                           rangeslider=dict(visible=True, thickness=0.07),
                           rangeselector=dict(buttons=list([
                               dict(count=1, label='mês', step='month', stepmode='todate', ),
                               dict(count=6, label='semestre', step='month', stepmode='todate'),
                               dict(count=1, label='ano', step='year', stepmode='todate'),
                               dict(count=1, label='todo', step='all')]),
                               bgcolor='rgba(0, 0, 0, 0)', activecolor='#007eff')
                           )
    gcn_gantt.update_coloraxes(showscale=False)
    gcn_gantt.update_traces(marker_line_width=0,
                            customdata=np.stack((gcn_filtrado['Módulo'], gcn_filtrado['Aula'],
                                                 gcn_filtrado['Subtarefa'], gcn_filtrado['Responsável']), axis=-1),
                            hovertemplate='<b>Aula %{customdata[1]}</b><br>'
                                          'Módulo %{customdata[0]}<br>'
                                          'Início: %{base}<br>'
                                          'Término: %{x}<br>'
                                          'Subtarefa: %{customdata[2]}<br>'
                                          'Responsável: %{customdata[3]}<br>'
                            )

# Linhas e Indicadores
# Configurando as cores das linhas
    def cores_linhas(fig, df):
        for i, id in enumerate(fig.data):
            progresso = df[df['ID'] == id.name]['progresso'].iloc[-1]
            if progresso == 100:
                fig.data[i].line.color = '#FF0023'
                fig.data[i].marker.color = '#FF0023'
            else:
                fig.data[i].line.color = '#ffd700'
                fig.data[i].marker.color = '#ffd700'

        return fig

# Plotando
    gcn_linhas = px.line(gcn_filtrado,
                         x='data final',
                         y='progresso',
                         color='ID',
                         markers=True,
                         hover_data={'ID': False, 'Aula': True, 'Módulo': True}
                         )

    gcn_linhas = cores_linhas(gcn_linhas, gcn_filtrado)

    gcn_linhas.update_layout(grafico_config,
                             title={'text': 'Progresso das aulas', 'x': 0.5},
                             )
    gcn_linhas.update_yaxes(title='Progresso (%)', range=[0, 100], gridcolor='rgba(255, 255, 255, 0.04)')
    gcn_linhas.update_xaxes(showgrid=False,
                            title='Seletor de intervalo', autorange=False, range=[data_minima, data_maxima],
                            rangeslider=dict(visible=True, thickness=0.07),
                            rangeselector=dict(buttons=list([
                                dict(count=1, label='mês', step='month', stepmode='todate', ),
                                dict(count=6, label='semestre', step='month', stepmode='todate'),
                                dict(count=1, label='ano', step='year', stepmode='todate'),
                                dict(count=1, label='todo', step='all')]),
                                bgcolor='rgba(0, 0, 0, 0)', activecolor='#007eff')
                            )

    gcn_linhas.update_traces(
        hovertemplate='<b>Data</b> %{x}<br>'
                      '<b>Progresso</b> %{y:.0f}%<br>'  # '.0f' formata como inteiro
                      '<b>Aula</b> %{customdata[1]}<br>'  # 'Aula' está em customdata[1]
                      '<b>Módulo</b> %{customdata[2]}<br>'  # 'Módulo' está em customdata[2]
    )

# Configurando df e cores do Indicador Progresso
    media_progresso = gcn_filtrado.groupby('ID')['progresso'].max().mean()

    def cor_gauge_progresso(media_progresso):
        if media_progresso == 100:
            return '#FF0023'
        else:
            return '#ffd700'

# Plotando
    gcn_progresso = go.Figure(go.Indicator(
        mode="gauge+number",
        value=media_progresso,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': cor_gauge_progresso(media_progresso)},
               }
    ))

    gcn_progresso.update_layout(grafico_config,
                                margin=dict(r=50, l=20, b=10, t=60),
                                title={'text': 'Progresso Total (%)', 'x': 0.5},
                                )

# Configurando df e cores do Indicador Duração
    data_min = gcn_filtrado.groupby('ID')['data inicial'].min()
    data_max = gcn_filtrado.groupby('ID')['data final'].max()

    duracao = data_max - data_min
    media_duracao = duracao.mean().days
    duracao_minima = duracao.min().days
    duracao_maxima = duracao.max().days

    def cor_gauge_duracao(media_duracao):
        if media_duracao <= 100:
            return '#FF0023'
        elif 100 < media_duracao <= 200:
            return '#ffd700'
        else:
            return 'red'

# Plotando
    gcn_duracao = go.Figure(go.Indicator(
        mode="gauge+number",
        value=media_duracao,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [duracao_minima, duracao_maxima]}, 'bar': {'color': cor_gauge_duracao(media_duracao)}}
    ))

    gcn_duracao.update_layout(grafico_config,
                              margin=dict(r=50, l=20, b=10, t=60),
                              title={'text': 'Produção (dias)', 'x': 0.5},
                              )

#  Barras (3)
# Modificação para Aula por Status
    aulas_gcn = gcn_filtrado.groupby(['curso', 'Módulo', 'Aula', 'Status']).agg({'data final': 'max'}).reset_index()
    aulas_gcn = aulas_gcn.drop(columns=['data final'])
    aulas_gcn = aulas_gcn.groupby(['Status']).size().to_frame(name='Aula').reset_index()
# Plotando
    gcn_barras = px.bar(
        aulas_gcn,
        x='Status',
        y='Aula',
        labels=False,
        color='Status',
        color_discrete_map={'CONCLUÍDA': '#FF0023',
                            'EM ANDAMENTO': '#ffd700',
                            'PENDENTE': 'gray'},
        text_auto=True,
        hover_data=None,
    )

    gcn_barras.update_layout(grafico_config,
                             title={'text': 'Aulas por Status', 'x': 0.5},
                             )
    gcn_barras.update_yaxes(showticklabels=False, showgrid=False, title=None, zeroline=False)
    gcn_barras.update_xaxes(title=None)
    gcn_barras.update_traces(textfont_size=20, textfont_color='#D3D3D3', marker_line_width=0)

# Modificação para Aulas por Professor(a)
    professor_gcn = gcn_filtrado.groupby(['curso', 'Professor', 'Módulo', 'Aula', 'Status']).agg({'data final': 'max'})
    professor_gcn = professor_gcn.reset_index()
    professor_gcn = professor_gcn.groupby(['curso', 'Professor', 'Módulo', 'Status']).size().to_frame(name='Aula')
    professor_gcn = professor_gcn.reset_index()
# Plotando
    gcn_professores = px.bar(
        professor_gcn,
        y='Professor',
        x='Aula',
        color='Status',
        orientation='h',
        color_discrete_map={'CONCLUÍDA': '#FF0023',
                            'EM ANDAMENTO': '#ffd700',
                            'PENDENTE': 'gray',
                            },
        hover_data={'Módulo': True, 'Status': False, 'Aula': True},
        text_auto=True,
    )

    gcn_professores.update_layout(grafico_config,
                                  title={'text': 'Aulas por professor(a)', 'x': 0.5},
                                  )

    gcn_professores.update_xaxes(showticklabels=False, showgrid=False, title=None, zeroline=False)
    gcn_professores.update_yaxes(title=None)
    gcn_professores.update_traces(textfont_size=12, textfont_color='#D3D3D3', marker_line_width=0,
                                  customdata=np.stack((professor_gcn['Módulo'],
                                                      professor_gcn['Aula']), axis=-1),
                                  hovertemplate='<b>Professor(a) %{y}</b><br>'
                                                'Módulo %{customdata[0]}<br>'
                                                '%{x} aulas<br>')

# Modificação para Subtarefas por responsável
    responsavel_gcn = gcn_filtrado.groupby(['Responsável', 'Módulo', 'Status']).size().to_frame(
        name='Número de subtarefas')
    responsavel_gcn = responsavel_gcn.reset_index()

    ordem_gcn = responsavel_gcn.groupby('Responsável')['Número de subtarefas'].sum()
    ordem_gcn = ordem_gcn.sort_values(ascending=True).index
# Plotando
    gcn_responsavel = px.bar(
        responsavel_gcn,
        y='Responsável',
        x='Número de subtarefas',
        color='Status',
        orientation='h',
        color_discrete_map={'CONCLUÍDA': '#FF0023',
                            'EM ANDAMENTO': '#ffd700',
                            'PENDENTE': 'gray',
                            },
        hover_data={'Módulo': True, 'Status': False},
        text_auto=True
    )

    gcn_responsavel.update_layout(grafico_config,
                                  height=1200,
                                  title={'text': 'Subtarefas por Responsável', 'x': 0.5},
                                  )

    gcn_responsavel.update_xaxes(showticklabels=False, showgrid=False, title=None, zeroline=False)
    gcn_responsavel.update_yaxes(title=None, categoryorder='array', categoryarray=ordem_gcn)
    gcn_responsavel.update_traces(textfont_size=12, textfont_color='#D3D3D3', marker_line_width=0,
                                  customdata=np.stack((responsavel_gcn['Responsável'],
                                                       responsavel_gcn['Módulo'],
                                                       responsavel_gcn['Responsável']), axis=-1),
                                  hovertemplate='<b>%{y}</b> <br>'
                                                'Módulo %{customdata[1]}<br>'
                                                'Subtarefas: %{x}<br>'
                                  )

    return (gcn_gantt.to_dict(), gcn_linhas.to_dict(), gcn_progresso.to_dict(), gcn_duracao.to_dict(),
            gcn_barras.to_dict(), gcn_professores.to_dict(), gcn_responsavel.to_dict())

# layout
tab_gantt = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                dcc.Graph(
                    id='gcn-gantt',
                    className='chart-container'
                ), type='circle', color='#ffd700',
            ),
        ),
    ],
),

tab_indicadores = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                html.Div(
                    [dcc.Graph(
                        id='gcn-linhas',
                        className='chart-container'
                        )
                    ],
                ), type='circle', color='#ffd700',
            ), width=9,
        ),
        dbc.Col(
            dcc.Loading(
                html.Div(
                    [
                        dbc.Row(
                            dbc.Col(
                                [dcc.Graph(
                                    id='gcn-progresso',
                                    className='chart-container2'
                                )
                                ],
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                [dcc.Graph(
                                    id='gcn-duracao',
                                    className='chart-container2',
                                )
                                ],
                            )
                        ),
                    ],
                ), type='circle', color='#ffd700',
            ), width=3,
        ),
    ],
)

tab_colaboradores = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                html.Div(
                    [dcc.Graph(
                        id='gcn-barras',
                        className='chart-container'
                    )
                    ],
                ), type='circle', color='#ffd700',
            ), width=4,
        ),
        dbc.Col(
            dcc.Loading(
                html.Div(
                    [dcc.Graph(
                        id='gcn-professores',
                        className='chart-container'
                    ),
                    ],
                ), type='circle', color='#ffd700',
            ), width=4,
        ),
        dbc.Col(
            [
                dcc.Loading(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    dcc.Graph(id='gcn-responsaveis'),
                                    className='chart-container'
                                )
                            ]
                        )
                    ], type='circle', color='#ffd700',
                )
            ], width=4,
        )
    ]
)

tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(tab_gantt, label='Linha do Tempo', tab_id='tabgan'),
                dbc.Tab(tab_indicadores, label='Indicadores', tab_id='tabind'),
                dbc.Tab(tab_colaboradores, label='Colaboradores', tab_id='tabcol'),
            ], id='tabs', active_tab='tabgan'
        ),
    ]
)

layout = dbc.Container(
    [
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2(
                                    'Gestão e Controle de Negócios',  # title
                                    className='title',
                                ),
                            ], width=5,
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(id='filtro-modulo',
                                             options=[{'label': curso, 'value': curso}
                                                      for curso in df_gcn['Módulo'].unique()],
                                             placeholder='Selecione o Módulo',
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
                tabs,
            ],
            className='page-content',
        )
    ],
    fluid=True,
)

@callback(
    Output('gcn-gantt', 'figure'),

    Output('gcn-linhas', 'figure'),
    Output('gcn-progresso', 'figure'),
    Output('gcn-duracao', 'figure'),

    Output('gcn-barras', 'figure'),
    Output('gcn-professores', 'figure'),
    Output('gcn-responsaveis', 'figure'),

    Input('filtro-modulo', 'value')
)
def atualizar_graficos(modulo_selecionado):
    return update_graphs(tuple(modulo_selecionado) if modulo_selecionado else None)