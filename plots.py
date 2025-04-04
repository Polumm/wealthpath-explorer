import numpy as np 
import plotly.graph_objs as go
from model import advanced_asset_model

def extract_common_params(scenarios, ignore_keys=("id","label")):
    """
    Returns two things:
      1) a dictionary of param -> value that is the SAME across all scenarios.
      2) a list of scenario-specific dictionaries for each scenario,
         containing only the fields that differ from the common set (plus 'label').
    """
    if not scenarios:
        return {}, []
    keys = [k for k in scenarios[0].keys() if k not in ignore_keys]
    value_sets = {k: set() for k in keys}
    for sc in scenarios:
        for k in keys:
            value_sets[k].add(sc[k])
    common = {}
    for k in keys:
        if len(value_sets[k]) == 1:
            common[k] = value_sets[k].pop()
    scenario_diffs = []
    for sc in scenarios:
        diff_dict = {"label": sc["label"]}
        for k in sc.keys():
            if k in ignore_keys:
                continue
            if k not in common:
                diff_dict[k] = sc[k]
        scenario_diffs.append(diff_dict)
    return common, scenario_diffs

def format_percent(val):
    """Format a decimal as a percent, e.g. 0.03 -> '3.0%'."""
    return f"{val * 100:.1f}%"

def format_common_text(common, max_chars=120):
    """
    Formats common parameters into a wrapped string if needed.
    """
    if not common:
        return "No common parameters. All differ!"
    items = []
    for k, v in sorted(common.items()):
        if k == "inflation_rate":
            continue  # hide from display
        if any(w in k for w in ['fraction','return','rate']):
            val_str = format_percent(float(v))
        else:
            val_str = str(v)
        items.append(f"{k}={val_str}")
    base_prefix = "Common among visible curves: "
    full_line = base_prefix + ", ".join(items)
    if len(full_line) <= max_chars:
        return full_line
    # wrap lines if too long
    lines = [base_prefix]
    current_line = ""
    for item in items:
        proposed = (current_line + ", " + item) if current_line else item
        if len(proposed) > max_chars:
            lines.append(current_line)
            current_line = item
        else:
            current_line = proposed
    if current_line:
        lines.append(current_line)
    return "<br>".join(lines)

def plot_multi_scenarios(scenarios):
    """
    Builds a Plotly figure showing asset accumulation curves.
    Each trace stores the full scenario in meta and its specific differences in customdata.
    """
    fig = go.Figure()

    # Extract shared and differing parameters across scenarios.
    common, scenario_diffs = extract_common_params(scenarios)

    for sc, diff_dict in zip(scenarios, scenario_diffs):
        label       = sc.get("label", "Scenario")
        init_asset  = float(sc.get('initial_asset', 0.0))
        ann_income  = float(sc.get('annual_income_initial', 0.0))
        invest_frac = float(sc.get('invest_fraction', 0.0))
        save_frac   = float(sc.get('save_fraction', 0.0))
        cons_frac   = float(sc.get('consumption_fraction', 0.0))
        inv_ret     = float(sc.get('annual_return_investment', 0.0))
        sav_ret     = float(sc.get('annual_return_savings', 0.0))
        growth      = float(sc.get('income_growth_rate', 0.0))
        inflation   = float(sc.get('inflation_rate', 0.0))
        yrs         = int(sc.get('years', 30))
        start_age   = int(sc.get('starting_age', 30))

        # Timeline.
        t = np.arange(yrs + 1)
        age = t + start_age

        # Run asset model.
        _, total_assets, *_ = advanced_asset_model(
            init_asset, ann_income, invest_frac, save_frac,
            cons_frac, inv_ret, sav_ret, growth, inflation, yrs
        )

        # Store differences in customdata.
        customdata = [[label, diff_dict] for _ in range(len(age))]
        
        # Build differences display (without repeating the label).
        parameter_groups = {}
        for k in diff_dict:
            if k == "label" or k == "inflation_rate":
                continue
            is_percent = any(w in k for w in ['fraction','return','rate'])
            if is_percent:
                val_str = f"{diff_dict[k] * 100:.1f}%"
            else:
                val_str = f"{diff_dict[k]}"
            param_label = k.replace("_", " ").title()
            parameter_groups[param_label] = val_str

        if parameter_groups:
            diff_html = "<b>Differences:</b><br>"
            for param, val in parameter_groups.items():
                diff_html += f"&nbsp;&nbsp;<b>{param}:</b> {val}<br>"
        else:
            diff_html = "<b>No Differences</b><br>"

        # Consistent hover template.
        hovertemplate = (
            "<b>Age:</b> %{x}<br>"
            "<b>Total Asset:</b> %{y:,.2f}<br><br>"
            f"<b>{label}</b><br>"
            f"{diff_html}"
            "<extra></extra>"
        )
        fig.add_trace(go.Scatter(
            x=age,
            y=total_assets,
            mode='lines+markers',
            name=label,
            meta=sc,  # full scenario dict.
            customdata=customdata,
            hovertemplate=hovertemplate,
            visible=True
        ))

    # Annotation for common parameters.
    annotation_text = format_common_text(common)
    fig.add_annotation(
        x=0, y=1.12,
        xref='paper', yref='paper',
        text=annotation_text,
        showarrow=False,
        align="left",
        bordercolor="black",
        borderwidth=1,
        bgcolor="#f0f0f0",
        font=dict(size=12)
    )

    # Layout.
    fig.update_layout(
        title=" ",
        xaxis_title="Age",
        yaxis_title="Total Asset Balance (Nominal)",
        hovermode="closest",
        legend_title="Click to in/exclude",
    )
    return fig
