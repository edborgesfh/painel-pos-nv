import dash
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, timedelta

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

data_min = prog_aulas_curso['data final'].min()
data_max = date.today()

cores_cursos = {
    'Gestão e Controle de Negócios': '#ff5c00',
    'Gestão de Recursos Humanos': '#FF0023',
    'Qualidade e Tecnologias da Carne': '#DB00FF'
}

@lru_cache(maxsize=32)
def grafico_geral(curso_selecionado):
    prog_aulas_curso_filtrado = prog_aulas_curso.copy()
    if curso_selecionado:
        prog_aulas_curso_filtrado = prog_aulas_curso[prog_aulas_curso['curso'].isin(curso_selecionado)]

    # Plotagem do gráfico
    g_geral = px.line(prog_aulas_curso_filtrado,
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

@lru_cache(maxsize=64)
def aulas_concluidas_periodo(curso_selecionado, periodo='dia'):
    prog_aulas_curso_filtrado = prog_aulas_curso.copy()
    if curso_selecionado:
        prog_aulas_curso_filtrado = prog_aulas_curso[prog_aulas_curso['curso'].isin(curso_selecionado)]

    if periodo == 'dia':
        aulas_concluidas = prog_aulas_curso_filtrado.groupby(['data final', 'curso'])['progresso_100'].sum().reset_index()
        eixo_x = 'data final'
    elif periodo == 'semana':
        prog_aulas_curso['Ano'] = prog_aulas_curso['data final'].dt.year
        prog_aulas_curso['Semana'] = prog_aulas_curso['data final'].dt.isocalendar().week
        # Encontrar a primeira quinta-feira de cada semana
        def encontrar_primeira_quinta(row):
            ano = row['Ano']
            semana = row['Semana']
            data_referencia = date(ano, 1, 1)  # Data inicial do ano
            delta_dias = (7 - data_referencia.weekday()) % 7 + (semana - 1) * 7 + 3  # 3 representa a quarta-feira
            return data_referencia + timedelta(days=delta_dias)
        prog_aulas_curso['Semana'] = prog_aulas_curso.apply(encontrar_primeira_quinta, axis=1)
        # Agrupar por semana e curso, somando progresso_100
        aulas_concluidas = prog_aulas_curso.groupby(['Semana', 'curso'])['progresso_100'].sum().reset_index()
        eixo_x = 'Semana'
    elif periodo == 'mes':
        prog_aulas_curso_filtrado['mes'] = prog_aulas_curso_filtrado['data final'].dt.month
        prog_aulas_curso_filtrado['ano'] = prog_aulas_curso_filtrado['data final'].dt.year
        aulas_concluidas = prog_aulas_curso_filtrado.groupby(['ano', 'mes', 'curso'])['progresso_100'].sum().reset_index()
        aulas_concluidas['mes'] = pd.to_datetime(
            {'year': aulas_concluidas['ano'], 'month': aulas_concluidas['mes'], 'day': 1}).dt.date
        aulas_concluidas = aulas_concluidas.rename(columns={'mes': 'Data Inicial do Mês'})
        eixo_x = 'Data Inicial do Mês'
    else:
        raise ValueError("Período inválido. Os valores válidos são: 'dia', 'semana', 'mes'.")

    g_concluidas = px.line(aulas_concluidas,
                           x=eixo_x,
                           y='progresso_100',
                           color='curso',
                           color_discrete_map=cores_cursos
                           )
    g_concluidas.update_layout(grafico_config, showlegend=True,
                               legend=dict(orientation='h', title='Cursos', yanchor='bottom',
                                           y=1, xanchor='right', x=1),
                               )
    g_concluidas.update_yaxes(title='Aulas Finalizadas', showgrid=False)
    g_concluidas.update_xaxes(title='Seletor de intervalo', gridcolor='rgba(255, 255, 255, 0.04)',
                              autorange=False, range=[data_min, data_max],
                              rangeslider=dict(visible=True, thickness=0.07),
                              rangeselector=dict(buttons=list([
                                  dict(count=1, label='mês', step='month', stepmode='todate', ),
                                  dict(count=6, label='semestre', step='month', stepmode='todate'),
                                  dict(count=1, label='ano', step='year', stepmode='todate'),
                                  dict(count=1, label='todo', step='all')]),
                                  bgcolor='rgba(0, 0, 0, 0)', activecolor='#007eff')
                              )
    g_concluidas.update_traces(hovertemplate='Data: %{x}<br>'
                                             'Aula(s) Conluída(s) %{y}<br>'
    )

    return g_concluidas.to_dict()

# layout
tab_geral = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                dcc.Graph(
                    id='g-geral',
                    # config={'displayModeBar': False},
                    # className='chart-card',
                    style={'height': '550px'},
                ),
                type='circle',
                color='#f79500',
            ),
        ),
    ],
),

tab_concluidas = dbc.Row(
    [
        dbc.Col(
            [
                dcc.Loading(
                    dcc.Graph(
                        id='g-concluidas',
                        # config={'displayModeBar': False},
                        # className='chart-card',
                        style={'height': '550px'},
                    ),
                    type='circle', color='#f79500',
                ),
            ], width=11,
        ),
        dbc.Col(
            [
                dbc.ButtonGroup(
                    [
                        dbc.Button("Dias", id='btn-dia', active=True),
                        dbc.Button("Semanas", id='btn-semana'),
                        dbc.Button("Meses", id='btn-mes'),
                    ], vertical=True,
                    id='filtro-periodo',
                ),
            ],  width=1, className='d-flex align-items-center justify-content-center'
        ),
    ],
),

tabs_visao = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(tab_geral, label='Progressão', tab_id='tabger'),
                dbc.Tab(tab_concluidas, label='Produção', tab_id='tabcon'),
            ], id='tabs-vis', active_tab='tabger'
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
                tabs_visao,
            ],
            className='page-content',
        ),
    ],
    fluid=True,
)

# callback cards and graphs

@callback(
    Output('g-geral', 'figure'),
    Output('g-concluidas', 'figure'),
    Output('btn-dia', 'active'),  # Outputs para atualizar o estado dos botões
    Output('btn-semana', 'active'),
    Output('btn-mes', 'active'),
    Input('filtro-cursos', 'value'),
    Input('btn-dia', 'n_clicks'),  # Inputs para detectar cliques nos botões
    Input('btn-semana', 'n_clicks'),
    Input('btn-mes', 'n_clicks'),
    State('btn-dia', 'active'),  # States para obter o estado atual dos botões
    State('btn-semana', 'active'),
    State('btn-mes', 'active'),
)
def atualizar_grafico_geral(curso_selecionado, btn_dia_clicks, btn_semana_clicks, btn_mes_clicks,
                        btn_dia_active, btn_semana_active, btn_mes_active):
    ctx = dash.callback_context

    # Detectar qual botão foi clicado
    button_clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_clicked == 'btn-dia':
        btn_dia_active = True
        btn_semana_active = False
        btn_mes_active = False
    elif button_clicked == 'btn-semana':
        btn_dia_active = False
        btn_semana_active = True
        btn_mes_active = False
    elif button_clicked == 'btn-mes':
        btn_dia_active = False
        btn_semana_active = False
        btn_mes_active = True

    # Determinar o período selecionado
    periodo_selecionado = 'dia'  # Valor padrão
    if btn_semana_active:
        periodo_selecionado = 'semana'
    elif btn_mes_active:
        periodo_selecionado = 'mes'

    return (
        grafico_geral(tuple(curso_selecionado) if curso_selecionado else None),
        aulas_concluidas_periodo(tuple(curso_selecionado) if curso_selecionado else None,
                                 periodo=periodo_selecionado),
        btn_dia_active,  # Retornar os estados atualizados dos botões
        btn_semana_active,
        btn_mes_active,
    )
