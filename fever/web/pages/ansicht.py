import dash
from dash import Input, Output, callback, dcc, html

from fever.web import format as fmt
from fever.web import validation_view, views

dash.register_page(__name__, path_template="/ansicht/<name>", title="Ansicht – Fieberthermometer", name="Ansicht")


def layout(name=None, **_query):
    if name == "visualisierung":  # static frame: the heatmap switch and the selection survive the refresh
        return html.Div(views.visualisation_frame())
    if name == "validierung":  # static frame as well: the choice of event survives the refresh
        return html.Div(validation_view.frame())
    return html.Div([dcc.Store(id="view-name", data=name), html.Div(id="view-content")])


@callback(Output("view-content", "children"), Input("view-name", "data"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(name, _n, theme):
    return views.view(name, theme or "light", fmt.utcnow())


# --- view 7 ------------------------------------------------------------------------------------------


@callback(Output("vis-stress", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh_stress(_n, theme):
    return views.vis_stress(theme or "light", fmt.utcnow())


@callback(Output("vis-regime", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh_regime(_n, theme):
    return views.vis_regime(theme or "light", fmt.utcnow())


@callback(Output("vis-heatmap", "children"), Input("heatmap-grain", "value"), Input("refresh", "n_intervals"),
          Input("theme", "data"))
def refresh_heatmap(grain, _n, theme):
    return views.vis_heatmap(grain or "weekly", theme or "light", fmt.utcnow())


@callback(Output("vis-bands", "children"), Input("bands-indicator", "value"), Input("refresh", "n_intervals"),
          Input("theme", "data"))
def refresh_bands(indicator_id, _n, theme):
    return views.vis_bands(indicator_id, theme or "light", fmt.utcnow())


@callback(Output("vis-sparklines", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh_sparklines(_n, theme):
    return views.vis_sparklines(theme or "light", fmt.utcnow())


# --- view 8: validation (M10, E-93) ---------------------------------------------------------------------


@callback(Output("validation-content", "children"), Input("validation-event", "value"), Input("refresh", "n_intervals"),
          Input("theme", "data"))
def refresh_validation(event, _n, theme):
    return validation_view.content(event, theme or "light", fmt.utcnow())
