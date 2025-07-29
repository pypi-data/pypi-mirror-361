# gpt-vis

A Python wrapper for [gpt-vis-cli](https://github.com/connect-a-sketch/gpt-vis-cli), enabling programmatic and command-line chart generation.

## Installation

Install the package using pip:

```bash
pip install gpt-vis
```

Or, if you have cloned the repository, you can install it in editable mode using Poetry:

```bash
poetry install
```

## Usage

### As a Python Library

You can use `gpt-vis` to generate charts programmatically within your Python applications.

```python
from gpt_vis_python.charts import render_bar_chart, BarChartOptions, BarChartData

# Define options for a bar chart
bar_chart_options = BarChartOptions(
    data=[
        BarChartData(category="A", value=10),
        BarChartData(category="B", value=20),
        BarChartData(category="C", value=15),
    ],
    title="Sample Bar Chart",
    axisXTitle="Category",
    axisYTitle="Value",
)

# Render the bar chart and save it to a file
render_bar_chart(options=bar_chart_options, output_path="bar_chart.png")
```

### As a Command-Line Tool

`gpt-vis` also provides a command-line interface for quick chart generation.

```bash
gpt-vis '''{"type": "bar", "data": [{"category": "A", "value": 10}, {"category": "B", "value": 20}], "title": "My Chart"}''' output.png
```

## Available Charts

`gpt-vis` supports a wide variety of chart types:

- Area
- Bar
- Boxplot
- Column
- District Map
- Dual Axes
- Fishbone Diagram
- Flow Diagram
- Funnel
- Histogram
- Line
- Liquid
- Mind Map
- Network Graph
- Organization Chart
- Path Map
- Pie
- Radar
- Sankey
- Scatter
- Treemap
- Venn
- Violin
- Word Cloud

For detailed options for each chart type, please refer to the `gpt_vis_python/charts.py` file.

## Development

To run the tests, execute the following command:

```bash
poetry run pytest
```

To run the demo, which generates a variety of chart images in the `output` directory:

```bash
poetry run python run.py
```