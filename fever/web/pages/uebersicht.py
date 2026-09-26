import dash
from dash import ALL, MATCH, Input, Output, callback, clientside_callback, ctx, html

from fever.web import format as fmt
from fever.web import views

dash.register_page(__name__, path="/", title="Übersicht – Fieberthermometer", name="Übersicht")


def layout(**_query):
    # The areas are a static frame outside "overview-content", so the 5-minute refresh keeps them open.
    return html.Div([html.H1("Übersicht"), html.Div(id="overview-content"), html.Div(views.areas(), id="areas")])


@callback(Output("overview-content", "children"), Input("refresh", "n_intervals"), Input("theme", "data"))
def refresh(_n, theme):
    return views.overview(theme or "light", fmt.utcnow())


@callback(
    Output({"type": "area-summary", "area": ALL}, "children"),
    Output({"type": "indicator-summary", "id": ALL}, "children"),
    Input("refresh", "n_intervals"),
)
def refresh_summaries(_n):
    area_ids = [output["id"]["area"] for output in ctx.outputs_list[0]]
    indicator_ids = [output["id"]["id"] for output in ctx.outputs_list[1]]
    return views.summaries(area_ids, indicator_ids, fmt.utcnow())


# Charts are built only for open sections (about 9 MB for all indicators at once, measured 26.09.2026).
@callback(
    Output({"type": "area-chart", "area": MATCH}, "children"),
    Input({"type": "area-toggle", "area": MATCH}, "n_clicks"),
    Input("refresh", "n_intervals"),
    Input("theme", "data"),
)
def refresh_area_chart(clicks, _n, theme):
    if not views.is_open(clicks):
        return []
    return views.area_chart(ctx.outputs_list["id"]["area"], theme or "light", fmt.utcnow())


@callback(
    Output({"type": "indicator-body", "id": MATCH}, "children"),
    Input({"type": "indicator-toggle", "id": MATCH}, "n_clicks"),
    Input("refresh", "n_intervals"),
    Input("theme", "data"),
)
def refresh_indicator(clicks, _n, theme):
    if not views.is_open(clicks):
        return []
    return views.indicator_detail(ctx.outputs_list["id"]["id"], theme or "light", fmt.utcnow())


# Opening and closing happen in the browser; the resize lets Plotly fit charts drawn while hidden.
TOGGLE = """
function (clicks) {
    const open = (clicks || 0) % 2 === 1;
    if (open) { setTimeout(function () { window.dispatchEvent(new Event("resize")); }, 0); }
    return [!open, open ? "true" : "false"];
}
"""
clientside_callback(
    TOGGLE,
    Output({"type": "area-body", "area": MATCH}, "hidden"),
    Output({"type": "area-toggle", "area": MATCH}, "aria-expanded"),
    Input({"type": "area-toggle", "area": MATCH}, "n_clicks"),
)
clientside_callback(
    TOGGLE,
    Output({"type": "indicator-body", "id": MATCH}, "hidden"),
    Output({"type": "indicator-toggle", "id": MATCH}, "aria-expanded"),
    Input({"type": "indicator-toggle", "id": MATCH}, "n_clicks"),
)
