import base64
import io
import tempfile

import altair
import mcp
import pandas as pd


def build_chart(vega_lite_json_spec: str, sql_query: str, connection_name: str):
    """Refer to data source as file://data.csv"""
    # Json schema https://vega.github.io/schema/vega-lite/v5.json is huge, need RAG for it.

    df = pd.read_sql(sql_query, connection_name)  # get engine for connection
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        vega_lite_json_spec.replace("file://data.csv", tmp.name)
        df.to_csv(tmp.name, index=False)
        chart = altair.Chart.from_json(vega_lite_json_spec)
        # Consider using chart.data = df or chart.data = {"values": df.to_dict(orient='records')}
        io_bytes = io.BytesIO()
        chart.save(io_bytes, format="png")
        io_bytes.seek(0)

    image = mcp.types.ImageContent(
        data=base64.b64encode(io_bytes.read()).decode(),
        mimeType="image/png",
    )
    return image

    vega_lite_json_string = """
    {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "A simple bar chart of category and value from a Pandas DataFrame.",
    "data": {
        "values": [
        {"category": "A", "value": 20, "group": "Group1"},
        {"category": "B", "value": 45, "group": "Group1"},
        {"category": "C", "value": 15, "group": "Group2"},
        {"category": "D", "value": 30, "group": "Group2"},
        {"category": "E", "value": 50, "group": "Group1"}
        ]
    },
    "mark": "bar",
    "encoding": {
        "x": {"field": "category", "type": "nominal", "title": "Category"},
        "y": {"field": "value", "type": "quantitative", "title": "Value"},
        "color": {"field": "group", "type": "nominal", "title": "Group"}
    },
    "title": "My Pandas DataFrame Bar Chart",
    "width": 400,
    "height": 300
    }
    """
    chart = altair.Chart.from_json(vega_lite_json_string)
