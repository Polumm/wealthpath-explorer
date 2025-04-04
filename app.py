import dash
from dash import dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import uuid

from database import (
    insert_scenario, get_all_scenarios, get_scenario_by_label,
    delete_scenario, update_scenario
)
# We import both the scenario-labelling function and the chart-building code
from plots import plot_multi_scenarios, extract_common_params, format_common_text
from model import advanced_asset_model  # your advanced model
from utils import safe_float, safe_int

external_stylesheets = [dbc.themes.BOOTSTRAP]

fraction_alert = dbc.Alert(
    id="fraction_alert",
    children="",
    color="danger",
    dismissable=True,
    is_open=False
)

# --- This function ensures each scenario has a unique "display_label"
#     by appending "|— N" to duplicates.
def assign_branch_labels(scenario_list):
    """
    Given a list of scenario dicts from the DB, ensure each scenario
    has a unique 'display_label'. If multiple scenarios share the same
    scenario['label'], then the 2nd, 3rd, etc. scenario get a suffix
    like '|— 2', '|— 3', etc.

    If scenario['display_label'] already exists, we skip re-assigning.
    """
    label_count = {}

    for sc in scenario_list:
        # If we already assigned a display_label in a prior pass, skip
        if "display_label" in sc:
            continue

        original_label = sc.get("label", "Scenario")
        # Count how many times we've seen 'original_label'
        if original_label not in label_count:
            label_count[original_label] = 1
            sc["display_label"] = original_label
        else:
            label_count[original_label] += 1
            suffix_num = label_count[original_label]
            sc["display_label"] = f"{original_label} |— {suffix_num}"

    return scenario_list



# --- Form with "Starting Age" ---
form = dbc.Form(
    [
        dbc.Row([
            dbc.Label("Label", width=4),
            dbc.Col(dbc.Input(id='label', type='text', value='My Scenario'), width=8),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Initial Asset", width=6),
            dbc.Col(dbc.Input(id='initial_asset', type='number', value=10000, step=1, min=0), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Initial Annual Income", width=6),
            dbc.Col(dbc.Input(id='annual_income_initial', type='number', value=50000, step=1, min=0), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Starting Age", width=6),
            dbc.Col(dbc.Input(id='starting_age', type='number', value=30, step=1, min=0), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Invest Fraction (%)", width=6),
            dbc.Col(dbc.Input(id='invest_fraction', type='number', value=30.0, step=0.1, min=0, max=100), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Save Fraction (%)", width=6),
            dbc.Col(dbc.Input(id='save_fraction', type='number', value=20.0, step=0.1, min=0, max=100), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Consumption Fraction (%)", width=6),
            dbc.Col(dbc.Input(id='consumption_fraction', type='number', value=50.0, step=0.1, min=0, max=100), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Annual Return (Investment) (%)", width=6),
            dbc.Col(dbc.Input(id='annual_return_investment', type='number', value=7.0, step=0.1), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Annual Return (Savings) (%)", width=6),
            dbc.Col(dbc.Input(id='annual_return_savings', type='number', value=2.0, step=0.1), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Income Growth Rate (%)", width=6),
            dbc.Col(dbc.Input(id='income_growth_rate', type='number', value=3.0, step=0.1), width=6),
        ], class_name="mb-2"),

        dbc.Row([
            dbc.Label("Inflation Rate (%)", width=6),
            dbc.Col(dbc.Input(id='inflation_rate', type='number', value=2.0, step=0.1), width=6),
        ], class_name="mb-2", style={"display": "none"}),

        dbc.Row([
            dbc.Label("Years", width=6),
            dbc.Col(dbc.Input(id='years', type='number', value=30, min=1, max=100), width=6),
        ], class_name="mb-2"),

        html.Div([
            dbc.Button("Add / Update Scenario", id="add_scenario_button", color="primary"),
            dbc.Button("Clear Form", id="clear_form_button", color="secondary", className="ms-2"),
            dbc.Button("Delete Current Scenario", id="delete_current_scenario", color="danger", className="ms-2")
        ], className="d-grid gap-2 d-md-flex justify-content-md-end"),

        html.Div(fraction_alert, className="mt-3")
    ]
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(fluid=True, children=[
    html.H1("Life Calculator", className="mt-3 mb-4 text-center"),

    dbc.Row([
        dbc.Col(width=4, children=[
            dbc.Button("Toggle Scenario Inputs", id="toggle-inputs", color="primary", size="sm", className="mb-2"),
            dcc.Dropdown(
                id="scenario_selector",
                placeholder="Select a scenario to edit",
                clearable=True,
                style={"marginBottom": "1rem"}
            ),
            dbc.Collapse(
                dbc.Card([
                    dbc.CardHeader("Scenario Inputs"),
                    dbc.CardBody([form])
                ]),
                id="collapse-inputs",
                is_open=True
            ),
        ]),
        dbc.Col(width=8, children=[
            dcc.Graph(
                id='asset_graph',
                config={"displaylogo": False, "responsive": True},
                style={"height": "85vh"}
            )
        ])
    ]),
    html.Div(id="comparison_table", style={"marginTop": "20px"}),

    html.Div([
        html.H6("Developed by Polumm", style={"textAlign": "center", "fontSize": "12px"}),
    ], style={"marginTop": "30px", "backgroundColor": "#f8f9fa", "padding": "10px"})
])

# ----------------------------------------------------------------------------
# 1) Manage scenarios (Add/Update, Delete) + Build figure + Update dropdown
# ----------------------------------------------------------------------------
@app.callback(
    Output('asset_graph', 'figure'),
    Output('fraction_alert', 'is_open'),
    Output('fraction_alert', 'children'),
    Output('scenario_selector', 'options'),
    Input('add_scenario_button', 'n_clicks'),
    Input('delete_current_scenario', 'n_clicks'),
    State('label', 'value'),
    State('initial_asset', 'value'),
    State('annual_income_initial', 'value'),
    State('starting_age', 'value'),
    State('invest_fraction', 'value'),
    State('save_fraction', 'value'),
    State('consumption_fraction', 'value'),
    State('annual_return_investment', 'value'),
    State('annual_return_savings', 'value'),
    State('income_growth_rate', 'value'),
    State('inflation_rate', 'value'),
    State('years', 'value')
)
def manage_scenarios(
    add_n, delete_n,
    label,
    initial_asset,
    annual_income_initial,
    starting_age,
    invest_pct,
    save_pct,
    consume_pct,
    inv_return_pct,
    sav_return_pct,
    inc_growth_pct,
    inflation_pct,
    years
):
    alert_open = False
    alert_message = ""
    triggered_id = ctx.triggered_id

    if triggered_id == 'add_scenario_button':
        i = safe_float(invest_pct)
        s = safe_float(save_pct)
        c = safe_float(consume_pct)
        frac_sum = i + s + c
        if abs(frac_sum - 100.0) > 1e-6:
            alert_open = True
            alert_message = (
                f"Fractions sum to {frac_sum:.2f}%, not 100%. Please fix them."
            )
        else:
            scenario_data = {
                "label": label or f"Scenario_{uuid.uuid4()}",
                "initial_asset": safe_float(initial_asset),
                "annual_income_initial": safe_float(annual_income_initial),
                "invest_fraction": i / 100.0,
                "save_fraction": s / 100.0,
                "consumption_fraction": c / 100.0,
                "annual_return_investment": safe_float(inv_return_pct) / 100.0,
                "annual_return_savings": safe_float(sav_return_pct) / 100.0,
                "income_growth_rate": safe_float(inc_growth_pct) / 100.0,
                "inflation_rate": safe_float(inflation_pct) / 100.0,
                "years": safe_int(years, 30),
                "starting_age": safe_int(starting_age, 30),
            }
            existing = get_scenario_by_label(scenario_data["label"])
            if existing:
                scenario_data["id"] = existing["id"]
                update_scenario(scenario_data)
            else:
                insert_scenario(scenario_data)

    elif triggered_id == 'delete_current_scenario':
        if label:
            existing = get_scenario_by_label(label)
            if existing:
                delete_scenario(existing["id"])

    # 1) Retrieve scenarios from DB
    scenario_list = get_all_scenarios()

    # 2) Ensure unique "branch labels" before building the figure
    scenario_list = assign_branch_labels(scenario_list)

    # 3) Build figure with newly assigned display_label
    fig = plot_multi_scenarios(scenario_list)

    # 4) Build dropdown options with display_label (instead of label).
    #    But we still keep the 'value' = sc["label"] so user can load the correct scenario by label in DB.
    selector_options = [{"label": sc["display_label"], "value": sc["label"]} for sc in scenario_list]

    return fig, alert_open, alert_message, selector_options


# ----------------------------------------------------------------------------
# 2) Toggle inputs
# ----------------------------------------------------------------------------
@app.callback(
    Output("collapse-inputs", "is_open"),
    Input("toggle-inputs", "n_clicks"),
    State("collapse-inputs", "is_open"),
)
def toggle_inputs(n, is_open):
    if n:
        return not is_open
    return is_open


# ----------------------------------------------------------------------------
# 3) Populate Form (from chart click or dropdown)
# ----------------------------------------------------------------------------
@app.callback(
    [
        Output('label', 'value'),
        Output('initial_asset', 'value'),
        Output('annual_income_initial', 'value'),
        Output('starting_age', 'value'),
        Output('invest_fraction', 'value'),
        Output('save_fraction', 'value'),
        Output('consumption_fraction', 'value'),
        Output('annual_return_investment', 'value'),
        Output('annual_return_savings', 'value'),
        Output('income_growth_rate', 'value'),
        Output('inflation_rate', 'value'),
        Output('years', 'value'),
        Output('scenario_selector', 'value')
    ],
    [
        Input('asset_graph', 'clickData'),
        Input('scenario_selector', 'value')
    ],
    prevent_initial_call=False
)
def populate_form(click_data, selected_label):
    triggered_id = ctx.triggered_id
    scenario = None

    if triggered_id == 'asset_graph' and click_data:
        try:
            # We assume customdata = [label, diff_dict]
            label_clicked = click_data['points'][0]['customdata'][0]
            scenario = get_scenario_by_label(label_clicked)
        except:
            return [no_update]*12 + [no_update]

    elif triggered_id == 'scenario_selector' and selected_label:
        scenario = get_scenario_by_label(selected_label)

    if not scenario:
        return [no_update]*12 + [no_update]

    return [
        scenario.get('label'),
        round(float(scenario.get('initial_asset', 0.0)), 4),
        round(float(scenario.get('annual_income_initial', 0.0)), 4),
        scenario.get('starting_age', 30),
        round(float(scenario.get('invest_fraction', 0.0)) * 100, 4),
        round(float(scenario.get('save_fraction', 0.0)) * 100, 4),
        round(float(scenario.get('consumption_fraction', 0.0)) * 100, 4),
        round(float(scenario.get('annual_return_investment', 0.0)) * 100, 4),
        round(float(scenario.get('annual_return_savings', 0.0)) * 100, 4),
        round(float(scenario.get('income_growth_rate', 0.0)) * 100, 4),
        round(float(scenario.get('inflation_rate', 0.0)) * 100, 4),
        int(scenario.get('years', 30)),
        None
    ]


# ----------------------------------------------------------------------------
# 4) Clear Form
# ----------------------------------------------------------------------------
@app.callback(
    [
        Output('label', 'value', allow_duplicate=True),
        Output('initial_asset', 'value', allow_duplicate=True),
        Output('annual_income_initial', 'value', allow_duplicate=True),
        Output('starting_age', 'value', allow_duplicate=True),
        Output('invest_fraction', 'value', allow_duplicate=True),
        Output('save_fraction', 'value', allow_duplicate=True),
        Output('consumption_fraction', 'value', allow_duplicate=True),
        Output('annual_return_investment', 'value', allow_duplicate=True),
        Output('annual_return_savings', 'value', allow_duplicate=True),
        Output('income_growth_rate', 'value', allow_duplicate=True),
        Output('inflation_rate', 'value', allow_duplicate=True),
        Output('years', 'value', allow_duplicate=True),
        Output('scenario_selector', 'value', allow_duplicate=True)
    ],
    Input('clear_form_button', 'n_clicks'),
    prevent_initial_call=True
)
def clear_form(n):
    return [
        "My Scenario",
        10000,
        50000,
        30,
        30.0,
        20.0,
        50.0,
        7.0,
        2.0,
        3.0,
        2.0,
        30,
        None
    ]


# ----------------------------------------------------------------------------
# 5) Handle Legend Toggles to update common annotation and hover templates
# ----------------------------------------------------------------------------
@app.callback(
    Output('asset_graph', 'figure', allow_duplicate=True),
    Input('asset_graph', 'restyleData'),
    State('asset_graph', 'figure'),
    prevent_initial_call=True
)
def update_annotation_on_legend_toggle(restyle_data, fig):
    """
    Updates common annotation and ensures that hover templates follow a consistent format.
    """
    if not restyle_data or not fig:
        return no_update

    data = fig.get('data', [])
    visible_scenarios = []
    for trace in data:
        visible = trace.get('visible', True)
        if visible not in [False, 'legendonly']:
            meta = trace.get('meta')
            if meta:
                visible_scenarios.append(meta)

    from plots import extract_common_params, format_common_text
    common, diffs = extract_common_params(visible_scenarios)

    if 'layout' in fig and 'annotations' in fig['layout'] and len(fig['layout']['annotations']) > 0:
        fig['layout']['annotations'][0]['text'] = format_common_text(common)

    # Update hover templates.
    for trace in fig['data']:
        meta = trace.get('meta')
        if meta and meta in visible_scenarios:
            label = meta.get("label", "Scenario")
            diff_dict = next((d for d in diffs if d["label"] == label), {})
            parameter_groups = {}
            for k, v in diff_dict.items():
                if k in ["label", "inflation_rate"]:
                    continue
                is_percent = any(w in k for w in ['fraction', 'return', 'rate'])
                if is_percent:
                    val_str = f"{float(v)*100:.1f}%"
                else:
                    val_str = f"{v}"
                param_label = k.replace("_", " ").title()
                parameter_groups[param_label] = val_str

            if parameter_groups:
                diff_html = "<b>Differences:</b><br>"
                for param, val in parameter_groups.items():
                    diff_html += f"&nbsp;&nbsp;<b>{param}:</b> {val}<br>"
            else:
                diff_html = "<b>No Differences</b><br>"

            hovertemplate = (
                "<b>Age:</b> %{x}<br>"
                "<b>Total Asset:</b> %{y:,.2f}<br><br>"
                f"<b>{label}</b><br>"
                f"{diff_html}"
                "<extra></extra>"
            )
            trace['hovertemplate'] = hovertemplate

    return fig


# ----------------------------------------------------------------------------
# 6) Update Comparison Table on Initial Load and Legend Toggle
# ----------------------------------------------------------------------------
@app.callback(
    Output('comparison_table', 'children'),
    [Input('asset_graph', 'restyleData'),
     Input('asset_graph', 'figure')]
)
def update_comparison_table(restyle_data, fig):
    """
    Builds an HTML table comparing key outputs (final age and total asset)
    and scenario differences for the visible scenarios. This callback now runs
    on initial load and on legend toggle changes.
    """
    if not fig:
        return no_update

    visible_scenarios = []
    for trace in fig.get('data', []):
        visible = trace.get('visible', True)
        if visible not in [False, 'legendonly']:
            meta = trace.get('meta')
            if meta:
                visible_scenarios.append(meta)

    if not visible_scenarios:
        return "No scenarios visible."

    # Build header row.
    header = [html.Th("Parameter")]
    label_count = {}
    for sc in visible_scenarios:
        label = sc.get("label", "Scenario")
        if label in label_count:
            label_count[label] += 1
            display_label = f"{label} |— {label_count[label]}"
        else:
            label_count[label] = 1
            display_label = label
        # Store display_label for header; it will not be included in the data rows.
        sc["display_label"] = display_label
        header.append(html.Th(display_label))

    # Compute final outputs for each scenario.
    final_info = {}
    for sc in visible_scenarios:
        init_asset = float(sc.get('initial_asset', 0.0))
        ann_income = float(sc.get('annual_income_initial', 0.0))
        invest_frac = float(sc.get('invest_fraction', 0.0))
        save_frac = float(sc.get('save_fraction', 0.0))
        cons_frac = float(sc.get('consumption_fraction', 0.0))
        inv_ret = float(sc.get('annual_return_investment', 0.0))
        sav_ret = float(sc.get('annual_return_savings', 0.0))
        growth = float(sc.get('income_growth_rate', 0.0))
        inflation = float(sc.get('inflation_rate', 0.0))
        yrs = int(sc.get('years', 30))
        start_age = int(sc.get('starting_age', 30))
        _, total_assets, *_ = advanced_asset_model(
            init_asset, ann_income, invest_frac, save_frac,
            cons_frac, inv_ret, sav_ret, growth, inflation, yrs
        )
        final_age = start_age + yrs
        final_asset = total_assets[-1]
        final_info[sc.get("label")] = {"final_age": final_age, "final_asset": final_asset}

    # Build rows for final outputs.
    rows = []
    row_age = [html.Td("Final Age")]
    row_asset = [html.Td("Final Total Asset")]
    for sc in visible_scenarios:
        label = sc.get("label")
        row_age.append(html.Td(final_info[label]["final_age"]))
        row_asset.append(html.Td(f"{final_info[label]['final_asset']:,.2f}"))
    rows.append(html.Tr(row_age))
    rows.append(html.Tr(row_asset))

    # Build rows for scenario-specific differences.
    common, scenario_diffs = extract_common_params(visible_scenarios)
    diff_keys = set()
    for diff in scenario_diffs:
        for key in diff:
            if key != "label" and key.lower() != "display_label":
                diff_keys.add(key)
    diff_keys = sorted(diff_keys)
    for key in diff_keys:
        row = [html.Td(key.replace("_", " ").title())]
        for diff in scenario_diffs:
            val = diff.get(key, "-")
            if any(x in key for x in ['fraction','return','rate']):
                if val != "-":
                    val = f"{float(val)*100:.1f}%"
            row.append(html.Td(val))
        rows.append(html.Tr(row))

    table = html.Table(
        [html.Thead(html.Tr(header))] + [html.Tbody(rows)],
        style={"width": "100%", "border": "1px solid black", "borderCollapse": "collapse", "textAlign": "center"}
    )
    return table


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
