
# Save this as starbucks_dash.py and run with: python3 starbucks_dash.py

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from collections import Counter
import re

# Data preparation
sb_nutr = pd.read_csv("starbucks-menu-nutrition.csv")
sb_nutr.columns = sb_nutr.columns.str.strip()

# Tokenize item names and find top 10 words
words = Counter(
    w for name in sb_nutr["Item"].dropna()
    for w in re.findall(r"[a-zA-Z]+", name.lower())
    if len(w) > 2
)
top10 = [w for w, _ in words.most_common(10)]

def find_word(item_name):
    for w in top10:
        if w in item_name.lower():
            return w
    return None

sb_nutr["top_word"] = sb_nutr["Item"].apply(find_word)
sb_top = sb_nutr.dropna(subset=["top_word"]).copy()

nutr_vars = ["Calories", "Fat (g)", "Carb. (g)", "Fiber (g)", "Protein (g)"]

# App layout
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Starbucks Menu Nutrition Explorer",
            style={"textAlign": "center", "fontFamily": "Arial"}),

    html.Div([
        html.Label("Select nutritional variable:", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="nutr-dd",
            options=[{"label": v, "value": v} for v in nutr_vars],
            value="Calories",
            clearable=False,
            style={"width": "300px"}
        ),
    ], style={"padding": "20px 40px", "fontFamily": "Arial"}),

    html.Div([
        dcc.Graph(id="bar-chart", style={"width": "50%", "display": "inline-block"}),
        dcc.Graph(id="scatter-chart", style={"width": "50%", "display": "inline-block"}),
    ]),
], style={"maxWidth": "1200px", "margin": "auto"})

# Callbacks
@app.callback(
    Output("bar-chart", "figure"),
    Output("scatter-chart", "figure"),
    Input("nutr-dd", "value"),
)
def update(selected_var):
    bar_df = (
        sb_top.groupby("top_word")[selected_var]
        .mean()
        .reset_index()
        .sort_values(selected_var, ascending=False)  # YOUR CODE HERE
    )
    bar_fig = px.bar(
        bar_df, x='top_word', y=selected_var,  # YOUR CODE HERE
        title=f"Mean {selected_var} by Top Menu Word",
        labels={"top_word": "Menu Word"},
        template="plotly_white",
        color="top_word",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    bar_fig.update_layout(height=420, showlegend=False)

    scatter_fig = px.scatter(
        sb_top, x='top_word', y=selected_var,  # YOUR CODE HERE
        color="Category",
        hover_data=["Item", "top_word"],
        title=f"Calories vs. {selected_var}",
        template="plotly_white",
        opacity=0.7,
    )
    scatter_fig.update_layout(height=420, hovermode="closest")

    return bar_fig, scatter_fig  # YOUR CODE HERE


if __name__ == "__main__":
    app.run(debug=True)

