import dash
from dash import Input, Output, callback, dcc, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path_template="/kennzahl/<kennzahl_id>", title="Kennzahl – Fieberthermometer", name="Kennzahl")


def layout(kennzahl_id=None, **_query):
    return html.Div([dcc.Store(id="kennzahl-id", data=kennzahl_id), html.Div(id="kennzahl-content")])


@callback(Output("kennzahl-content", "children"), Input("kennzahl-id", "data"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(kennzahl_id, _n, theme):
    return views.kennzahl(kennzahl_id, theme or "light", fmt.utcnow())
