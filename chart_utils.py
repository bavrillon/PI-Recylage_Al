import altair as alt
import pandas as pd
import typing as List



def build_strategy_chart(df: pd.DataFrame) -> alt.Chart:
    df2 = df.rename(columns={
        "cost": "Optimized cost (USD)",
        "co2":  "Optimized CO₂ (t)",
    })

    folded = (
        alt.Chart(df2)
        .transform_fold(
            ["Optimized cost (USD)", "Optimized CO₂ (t)"],
            as_=["metric", "value"],
        )
        .mark_bar()
        .encode(
            x=alt.X("strategy:N", title="Strategy"),
            y=alt.Y("value:Q", title=None),
            color=alt.Color("strategy:N", legend=None),
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