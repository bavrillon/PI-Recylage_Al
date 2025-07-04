import altair as alt
import pandas as pd


def build_strategy_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Given a DataFrame with columns ['alloy','strategy','cost','co2','scrap'],
    returns a side-by-side bar chart of cost, CO₂ and scrap%.
    """
    return (
        alt.Chart(df)
        .transform_fold(
            ["cost", "co2", "scrap"],
            as_=["metric", "value"],
        )
        .mark_bar()
        .encode(
            y=alt.Y("value:Q", title="Value"),
            color=alt.Color("strategy:N", title="Strategy"),
            column=alt.Column("metric:N", title="Metric"),
        )
        .properties(width=100, height=200)
    )
