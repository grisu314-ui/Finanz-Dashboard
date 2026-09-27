import dash
from dash import html

from fever.web import views

dash.register_page(__name__, path="/erklaerungen", title="Erklärungen – Fieberthermometer", name="Erklärungen")


def layout(**_query):
    return html.Div([html.H1("Erklärungen"), *views.explanations()])
