import dash
from dash import Input, Output, callback, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path="/", title="Übersicht – Fieberthermometer", name="Übersicht")

layout = html.Div([html.H1("Übersicht"), html.Div(id="overview-content")])


@callback(Output("overview-content", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(_n, theme):
    return views.overview(theme or "light", fmt.utcnow())
