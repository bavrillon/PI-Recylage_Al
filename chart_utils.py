import altair as alt
import pandas as pd
import typing as List


def build_strategy_chart(df: pd.DataFrame) -> alt.Chart:
    df2 = df.rename(columns={
        "cost":  "Cost (USD)",
        "co2":   "CO₂ (t)",
        "scrap": "Scrap (%)",
    })

    folded = (
        alt.Chart(df2)
        .transform_fold(
            ["Cost (USD)", "CO₂ (t)", "Scrap (%)"],
            as_=["metric", "value"]
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "strategy:N",
                title=None,               
                axis=alt.Axis(labels=True, ticks=False)
            ),
            y=alt.Y("value:Q", title=None),
            color=alt.Color(
                "strategy:N",
                legend=None             
            ),
        )
        .properties(width=180)
    )

    chart = (
        folded
        .facet(
            column=alt.Column("metric:N", title=None,
                              header=alt.Header(labelAngle=0))
        )
        .resolve_scale(y="independent")
    )
    return chart


