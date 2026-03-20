from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st

from main import SearchService

st.set_page_config(page_title="Western Cape Car Parts Finder", page_icon="🚗", layout="wide")


@dataclass
class AppText:
    title: str = "Western Cape Car Parts Finder"
    subtitle: str = "Search real scraped car-part listings available in the Western Cape or deliverable to the Western Cape."


TEXT = AppText()


@st.cache_resource(show_spinner=False)
def get_service() -> SearchService:
    return SearchService()


@st.cache_data(show_spinner=False, ttl=600)
def run_search(query: str, use_cache: bool) -> list[dict[str, Any]]:
    return get_service().search(query, use_cache=use_cache)


def price_for_sort(value: str | None) -> float:
    if not value:
        return float("inf")
    cleaned = "".join(ch for ch in str(value) if ch.isdigit() or ch in {".", ","}).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return float("inf")


def availability_label(location: str | None) -> str:
    if not location:
        return "Deliverable / not stated"
    lowered = location.lower()
    wc_words = [
        "cape town",
        "western cape",
        "goodwood",
        "bellville",
        "stellenbosch",
        "paarl",
        "somerset west",
        "milnerton",
        "montague gardens",
    ]
    if any(word in lowered for word in wc_words):
        return "Western Cape source"
    return "Deliverable / national retailer"


def build_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["Price"] = df["price"].fillna("N/A")
    df["Location"] = df["location"].fillna("Not stated")
    df["Availability"] = df["location"].apply(availability_label)
    df["_price_sort"] = df["price"].apply(price_for_sort)
    df["Direct Link"] = df["url"]

    return df.rename(
        columns={
            "source": "Source",
            "part_name": "Part",
            "car_model": "Vehicle",
            "date_scraped": "Scraped At",
        }
    )[
        ["Source", "Part", "Vehicle", "Price", "Location", "Availability", "Direct Link", "url", "Scraped At", "_price_sort"]
    ]


st.title(TEXT.title)
st.caption(TEXT.subtitle)

query = st.text_input("Part and vehicle", placeholder="radiator polo vivo")
use_cache = st.checkbox("Use 10-minute cache", value=True)
only_wc = st.checkbox("Western Cape sources only", value=False)
sort_by = st.selectbox("Sort by", ["Best match", "Lowest price", "Source"])
search_clicked = st.button("Search", type="primary")

if search_clicked:
    if not query.strip():
        st.warning("Enter a part and vehicle first.")
        st.stop()

    with st.spinner("Searching live sources..."):
        rows = run_search(query.strip(), use_cache=use_cache)

    if not rows:
        st.error("No parts found for this query.")
        st.stop()

    df = build_table(rows)

    if only_wc:
        df = df[df["Availability"] == "Western Cape source"]

    if sort_by == "Lowest price":
        df = df.sort_values(by=["_price_sort", "Source", "Part"], ascending=[True, True, True])
    elif sort_by == "Source":
        df = df.sort_values(by=["Source", "Part"], ascending=[True, True])

    if df.empty:
        st.warning("No results matched the selected filters.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    c1.metric("Results", len(df))
    c2.metric("Sources", df["Source"].nunique())
    c3.metric("Western Cape listings", int((df["Availability"] == "Western Cape source").sum()))

    csv_bytes = df.drop(columns=["url", "_price_sort"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv_bytes,
        file_name="western_cape_car_parts_results.csv",
        mime="text/csv",
    )

    st.dataframe(
        df.drop(columns=["url", "_price_sort"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Direct Link": st.column_config.LinkColumn("Direct Link", display_text="Open listing"),
        },
    )

    with st.expander("Raw URLs"):
        st.dataframe(df[["Source", "Part", "url"]].rename(columns={"url": "URL"}), use_container_width=True, hide_index=True)
else:
    st.info("Enter a query, then click Search.")
