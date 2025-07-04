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
            x=alt.X("alloy:N", title="Alloy"),
            y=alt.Y("value:Q", title="Value"),
            color=alt.Color("strategy:N", title="Strategy"),
            column=alt.Column("metric:N", title="Metric"),
        )
        .properties(width=100, height=200)
    )


###### dans interface.py, bloc séparé à la fin : 


# ------------------------------------------------------------------------
# Chart block
# ------------------------------------------------------------------------
from chart_utils import build_strategy_chart
import pandas as pd
from data.db_tools import Database

optimised_co2_scrap = db.optimise_co2_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
optimised_co2_no_scrap = db.optimise_co2_without_scrap(ID_SITE, ID_ALLOY)

cost_with = db.get_total_cost(comp_with, ID_SITE, ID_SCRAP)[-1]
co2_with = db.get_total_co2(comp_with)[-1]
scrap_with = comp_with[-1] * 100  

cost_without = db.get_total_cost(comp_without, ID_SITE)[-1]
co2_without = db.get_total_co2(comp_without)[-1]
scrap_without = 0.0



st.subheader("Comparaison")

df = pd.DataFrame([
    {
        "alloy": ID_ALLOY,
        "strategy": "with scrap",
        "cost": cost_with,
        "co2": co2_with,
        "scrap": scrap_with,
    },
    {
        "alloy": ID_ALLOY,
        "strategy": "no scrap",
        "cost": cost_without,
        "co2": co2_without,
        "scrap": scrap_without,
    },
])

st.altair_chart(
    build_strategy_chart(df),
    use_container_width=True
)
)





