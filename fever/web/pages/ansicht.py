import dash
from dash import Input, Output, callback, dcc, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path_template="/ansicht/<name>", title="Ansicht – Fieberthermometer", name="Ansicht")


def layout(name=None, **_query):
    return html.Div([dcc.Store(id="view-name", data=name), html.Div(id="view-content")])


@callback(Output("view-content", "children"), Input("view-name", "data"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(name, _n, theme):
    return views.view(name, theme or "light", fmt.utcnow())
