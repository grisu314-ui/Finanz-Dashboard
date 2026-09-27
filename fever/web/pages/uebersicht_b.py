import dash
from dash import Input, Output, callback, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path="/uebersicht-b", title="Übersicht B – Fieberthermometer", name="Übersicht B")

layout = html.Div([html.H1("Übersicht B"), html.Div(id="overview-b-content")])


@callback(Output("overview-b-content", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(_n, theme):
    return views.overview_b(theme or "light", fmt.utcnow())
