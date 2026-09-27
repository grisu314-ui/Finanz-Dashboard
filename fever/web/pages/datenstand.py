import dash
from dash import Input, Output, callback, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path="/datenstand", title="Datenstand – Fieberthermometer", name="Datenstand")

layout = html.Div([html.H1("Datenstand"), html.Div(id="status-content")])


@callback(Output("status-content", "children"), Input("refresh", "n_intervals"))
def refresh(_n):
    return views.data_status(fmt.utcnow())
