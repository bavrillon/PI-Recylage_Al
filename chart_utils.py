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


def build_composition_bar(
    elements: List[str],
    optimised_co2_scrap: List[float],
    optimised_co2_no_scrap: List[float],
    ) -> alt.Chart:

    with_vals = optimised_co2_scrap[: len(elements)]
    without_vals = optimised_co2_no_scrap[: len(elements)]

    df = pd.DataFrame({
        "element": elements * 2,
        "fraction": with_vals + without_vals,
        "strategy": ["with scrap"] * len(elements) + ["no scrap"] * len(elements),
    })

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("element:N", title="Element", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("fraction:Q", title="Fraction"),
            color=alt.Color("strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("element:N", title="Element"),
                alt.Tooltip("strategy:N", title="Strategy"),
                alt.Tooltip("fraction:Q", title="Fraction", format=".1%")
            ],
        )
        .properties(width=400, height=300)
    )



##### interface.py
from chart_utils import build_composition_bar

st.subheader("Composition par élément (bar chart)")

# Build and display the bar chart
bar_chart = build_composition_bar(
    elements=db.elements,
    optimised_co2_scrap=optimised_co2_scrap,
    optimised_co2_no_scrap=optimised_co2_no_scrap,
)
st.altair_chart(bar_chart, use_container_width=True)