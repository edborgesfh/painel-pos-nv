import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

app = Dash(
    __name__,
    use_pages=True,
    title='Painel Pós-Graduações UNICORP',
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)
server = app.server

# sidebar
sidebar = html.Div(
    [
        dbc.Row(
            [html.Img(src='src/assets/logos/bed.png', style={'height': '20px'})],
            className='sidebar-logo',
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink([
                    html.I(id='icone-geral',
                           className='fa-solid fa-home nav-icon',
                           ),
                    dbc.Tooltip(
                        'Visão Geral',
                        target='icone-geral',
                        placement='right',
                        style={'font-size': '1rem'}
                    ),
                ],
                    href='/visaogeral',
                    active='exact'
                ),
                dbc.NavLink([
                    html.I(id='icone-gcn',
                           className='fa-solid fa-briefcase nav-icon',
                           ),
                    dbc.Tooltip(
                        'Gestão e Controle de Negócios',
                        target='icone-gcn',
                        placement='right',
                        style={'font-size': '1rem'}
                    ),
                ],
                    href='/gcn',
                    active='exact'
                ),
                dbc.NavLink([
                    html.I(id='icone-grh',
                           className='fa-solid fa-users nav-icon',
                           ),
                    dbc.Tooltip(
                        'Gestão de Recursos Humanos',
                        target='icone-grh',
                        placement='right',
                        style={'font-size': '1rem'}
                    ),
                ],
                    href='/grh',
                    active='exact'
                ),
                dbc.NavLink([
                    html.I(id='icone-qtc',
                           className='fa-solid fa-bacon nav-icon',
                           ),
                    dbc.Tooltip(
                        'Qualidade e Tecnologias da carne',
                        target='icone-qtc',
                        placement='right',
                        style={'font-size': '1rem'}
                    ),
                ],
                    href='/qtc',
                    active='exact'
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Span('Por '),
                html.A(
                    'Eduardo Filho',
                    href='https://github.com/edborgesfh',
                    target='_blank',
                ),
                html.Br(),
                html.Span('Fonte ',),
                html.A(
                    'CPC Bittar Educação',
                ),
            ],
            className='subtitle-sidebar',
            style={'position': 'absolute', 'bottom': '10px', 'width': '100%'},
        ),
    ],
    className='sidebar',
)

content = html.Div(
    className='page-content',
)

# layout
app.layout = html.Div(
    [
        dcc.Location(id='url', pathname='/visaogeral'),
        sidebar,
        content,
        dash.page_container,
    ]
)

if __name__ == '__main__':
    app.run_server(port=8066, debug=True)
