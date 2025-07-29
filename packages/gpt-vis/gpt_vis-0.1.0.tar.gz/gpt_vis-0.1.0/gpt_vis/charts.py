import json
import subprocess
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

ChartType = Literal[
    "area", "bar", "boxplot", "column", "district-map", "dual-axes", "fishbone-diagram",
    "flow-diagram", "funnel", "histogram", "line", "liquid", "mind-map", "network-graph",
    "organization-chart", "path-map", "pie", "radar", "sankey", "scatter", "treemap",
    "venn", "violin", "word-cloud"
]


class Chart:
    def __init__(self, chart_type: ChartType, options: BaseModel, output_path: str):
        self.chart_type = chart_type
        self.options = options
        self.output_path = output_path

    def render(self):
        chart_options = {
            "type": self.chart_type,
            **self.options.dict(exclude_none=True),
        }
        json_options = json.dumps(chart_options)
        try:
            process = subprocess.run(
                ['npx', '-y', 'gpt-vis-cli', json_options],
                capture_output=True,
                check=True
            )
            with open(self.output_path, 'wb') as f:
                f.write(process.stdout)
            print(f"Visualization saved to {self.output_path}")
        except FileNotFoundError:
            print(f"Error: npx command not found. Please ensure Node.js and npm are installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing gpt-vis-cli: {e}")
            print(f"Stderr: {e.stderr.decode()}")


class AreaChartData(BaseModel):
    time: str = Field(..., description="Time for area chart data.")
    value: float = Field(..., description="Value for area chart data.")
    group: Optional[str] = Field(None, description="Group for area chart data.")


class AreaChartOptions(BaseModel):
    data: List[AreaChartData] = Field(..., min_items=1,
                                      description="Data for area chart, such as, [{ time: '2018', value: 99.9 }].")
    stack: bool = Field(False,
                        description="Whether stacking is enabled. When enabled, area charts require a 'group' field in the data.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class BarChartData(BaseModel):
    category: str = Field(..., description="Category for bar chart data.")
    value: float = Field(..., description="Value for bar chart data.")
    group: Optional[str] = Field(None, description="Group for bar chart data.")


class BarChartOptions(BaseModel):
    data: List[BarChartData] = Field(..., min_items=1,
                                     description="Data for bar chart, such as, [{ category: '分类一', value: 10 }].")
    group: bool = Field(False,
                        description="Whether grouping is enabled. When enabled, bar charts require a 'group' field in the data. When `group` is true, `stack` should be false.")
    stack: bool = Field(True,
                        description="Whether stacking is enabled. When enabled, bar charts require a 'group' field in the data. When `stack` is true, `group` should be false.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class BoxPlotData(BaseModel):
    category: str = Field(..., description="Category of the data point, such as '分类一'.")
    value: float = Field(..., description="Value of the data point, such as 10.")
    group: Optional[str] = Field(None,
                                 description="Optional group for the data point, used for grouping in the boxplot.")


class BoxPlotOptions(BaseModel):
    data: List[BoxPlotData] = Field(..., min_items=1,
                                    description="Data for boxplot chart, such as, [{ category: '分类一', value: 10 }] or [{ category: '分类二', value: 20, group: '组别一' }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class ColumnChartData(BaseModel):
    category: str = Field(..., description="Category for column chart data.")
    value: float = Field(..., description="Value for column chart data.")
    group: Optional[str] = Field(None, description="Group for column chart data.")


class ColumnChartOptions(BaseModel):
    data: List[ColumnChartData] = Field(..., min_items=1,
                                        description="Data for column chart, such as, [{ category: '北京', value: 825, group: '油车' }].")
    group: bool = Field(True,
                        description="Whether grouping is enabled. When enabled, column charts require a 'group' field in the data. When `group` is true, `stack` should be false.")
    stack: bool = Field(False,
                        description="Whether stacking is enabled. When enabled, column charts require a 'group' field in the data. When `stack` is true, `group` should be false.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class DistrictMapStyle(BaseModel):
    fillColor: Optional[str] = Field(None, description="Fill color, rgb or rgba format.")


class DistrictMapSubdistrict(BaseModel):
    name: str = Field(...,
                      description="""Keywords for the Chinese name of an administrative region (must be within China), and must be one of China, province, city, district, or county. The name should be more specific and add attributive descriptions, for example, "西安市" is better than "西安", "杭州西湖区" is better than "西湖区". It cannot be a specific place name or a vague name, such as "其它".""")
    dataValue: Optional[str] = Field(None, description="Data value, numeric string or enumeration string.")
    style: Optional[DistrictMapStyle] = Field(None, description="Style settings.")


class DistrictMapData(BaseModel):
    name: str = Field(...,
                      description="""Keywords for the Chinese name of an administrative region (must be within China), and must be one of China, province, city, district, or county. The name should be more specific and add attributive descriptions, for example, "西安市" is better than "西安", "杭州西湖区" is better than "西湖区". It cannot be a specific place name or a vague name, such as "其它".""")
    style: Optional[DistrictMapStyle] = Field(None, description="Style settings.")
    colors: List[str] = Field([
        "#1783FF",
        "#00C9C9",
        "#F0884D",
        "#D580FF",
        "#7863FF",
        "#60C42D",
        "#BD8F24",
        "#FF80CA",
        "#2491B3",
        "#17C76F",
    ], description="Data color list, in rgb or rgba format.")
    dataType: Optional[Literal["number", "enum"]] = Field(None,
                                                          description="The type of the data value, numeric or enumeration type")
    dataLabel: Optional[str] = Field(None, description="""Data label, such as "GDP""""")
    dataValue: Optional[str] = Field(None, description="Data value, numeric string or enumeration string.")
    dataValueUnit: Optional[str] = Field(None, description="""Data unit, such as "万亿""""")
    showAllSubdistricts: bool = Field(False, description="Whether to display all subdistricts.")
    subdistricts: Optional[List[DistrictMapSubdistrict]] = Field(None,
                                                                 description="Sub-administrative regions are used to display the regional composition or regional distribution of related data.")


class DistrictMapOptions(BaseModel):
    title: str = Field(...,
                       description="The map title should not exceed 16 characters. The content should be consistent with the information the map wants to convey and should be accurate, rich, creative, and attractive.")
    data: DistrictMapData = Field(...,
                                  description="""Administrative division data, lower-level administrative divisions are optional. There are usually two scenarios: one is to simply display the regional composition, only `fillColor` needs to be configured, and all administrative divisions are consistent, representing that all blocks are connected as one; the other is the regional data distribution scenario, first determine the `dataType`, `dataValueUnit` and `dataLabel` configurations, `dataValue` should be a meaningful value and consistent with the meaning of dataType, and then determine the style configuration. The `fillColor` configuration represents the default fill color for areas without data. Lower-level administrative divisions do not need `fillColor` configuration, and their fill colors are determined by the `colors` configuration (If `dataType` is "number", only one base color (warm color) is needed in the list to calculate the continuous data mapping color band; if `dataType` is "enum", the number of color values in the list is equal to the number of enumeration values (contrast colors)). If `subdistricts` has a value, `showAllSubdistricts` must be set to true. For example, {"title": "陕西省地级市分布图", "data": {"name": "陕西省", "showAllSubdistricts": true, "dataLabel": "城市", "dataType": "enum", "colors": ["#4ECDC4", "#A5D8FF"]", "subdistricts": [{"name": "西安市", "dataValue": "省会"}, {"name": "宝鸡市", "dataValue": "地级市"}, {"name": "咸阳市", "dataValue": "地级市"}, {"name": "铜川市", "dataValue": "地级市"}, {"name": "渭南市", "dataValue": "地级市"}, {"name": "延安市", "dataValue": "地级市"}, {"name": "榆林市", "dataValue": "地级市"}, {"name": "汉中市", "dataValue": "地级市"}, {"name": "安康市", "dataValue": "地级市"}, {"name": "商洛市", "dataValue": "地级市"}]}, "width": 1000, "height": 1000.}""")
    width: int = Field(1600, description="Set the width of map, default is 1600.")
    height: int = Field(1000, description="Set the height of map, default is 1000.")


class DualAxesSeries(BaseModel):
    type: Literal["column", "line"] = Field(..., description="The optional value can be 'column' or 'line'.")
    data: List[float] = Field(...,
                              description="When type is column, the data represents quantities, such as [91.9, 99.1, 101.6, 114.4, 121]. When type is line, the data represents ratios and its values are recommended to be less than 1, such as [0.055, 0.06, 0.062, 0.07, 0.075].")
    axisYTitle: str = Field("", description="Set the y-axis title of the chart series, such as, axisYTitle: '销售额'.")


class DualAxesOptions(BaseModel):
    categories: List[str] = Field(..., min_items=1,
                                  description="Categories for dual axes chart, such as, ['2015', '2016', '2017'].")
    series: List[DualAxesSeries] = Field(..., min_items=1,
                                         description="Series for dual axes chart, such as, [{ type: 'column', data: [91.9, 99.1, 101.6, 114.4, 121], axisYTitle: '销售额' }, { type: 'line', data: [0.055, 0.06, 0.062, 0.07, 0.075], 'axisYTitle': '利润率' }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")


class FishboneDiagramData(BaseModel):
    name: str = Field(..., description="Name of the topic.")
    children: Optional[List["FishboneDiagramData"]] = Field(None, description="Children topics.")


class FishboneDiagramOptions(BaseModel):
    data: FishboneDiagramData = Field(...,
                                      description="Data for fishbone diagram chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name: 'subtopic 1-1' }] }.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")


class FlowDiagramNode(BaseModel):
    name: str = Field(..., description="Name of the node.")


class FlowDiagramEdge(BaseModel):
    name: str = Field("", description="Name of the edge.")
    source: str = Field(..., description="Source node of the edge.")
    target: str = Field(..., description="Target node of the edge.")


class FlowDiagramData(BaseModel):
    nodes: List[FlowDiagramNode] = Field(..., min_items=1, description="Nodes for flow diagram chart.")
    edges: List[FlowDiagramEdge] = Field(..., description="Edges for flow diagram chart.")


class FlowDiagramOptions(BaseModel):
    data: FlowDiagramData = Field(...,
                                  description="Data for flow diagram chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")


class FunnelChartData(BaseModel):
    category: str = Field(..., description="Category for funnel chart data.")
    value: float = Field(..., description="Value for funnel chart data.")


class FunnelChartOptions(BaseModel):
    data: List[FunnelChartData] = Field(..., min_items=1,
                                        description="Data for funnel chart, such as, [{ category: '浏览网站', value: 50000 }, { category: '放入购物车', value: 35000 }, { category: '生成订单', value: 25000 }, { category: '支付订单', value: 15000 }, { category: '完成交易', value: 8000 }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class HistogramOptions(BaseModel):
    data: List[float] = Field(..., min_items=1, description="Data for histogram chart, such as, [78, 88, 60, 100, 95].")
    binNumber: Optional[int] = Field(None,
                                     description="Number of intervals to define the number of intervals in a histogram.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class LineChartData(BaseModel):
    time: str = Field(..., description="Time for line chart data.")
    value: float = Field(..., description="Value for line chart data.")


class LineChartOptions(BaseModel):
    data: List[LineChartData] = Field(..., min_items=1,
                                      description="Data for line chart, such as, [{ time: '2015', value: 23 }].")
    stack: bool = Field(False,
                        description="Whether stacking is enabled. When enabled, line charts require a 'group' field in the data.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class LiquidChartOptions(BaseModel):
    percent: float = Field(..., ge=0, le=1,
                           description="The percentage value to display in the liquid chart, should be a number between 0 and 1, where 1 represents 100%. For example, 0.75 represents 75%.")
    shape: Literal["circle", "rect", "pin", "triangle"] = Field("circle",
                                                                description="The shape of the liquid chart, can be 'circle', 'rect', 'pin', or 'triangle'. Default is 'circle'.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class MindMapData(BaseModel):
    name: str = Field(..., description="Name of the topic.")
    children: Optional[List["MindMapData"]] = Field(None, description="Children topics.")


class MindMapOptions(BaseModel):
    data: MindMapData = Field(...,
                              description="Data for mind map chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name:'subtopic 1-1' }] }.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")


class NetworkGraphNode(BaseModel):
    name: str = Field(..., description="Name of the node.")


class NetworkGraphEdge(BaseModel):
    name: str = Field("", description="Name of the edge.")
    source: str = Field(..., description="Source node of the edge.")
    target: str = Field(..., description="Target node of the edge.")


class NetworkGraphData(BaseModel):
    nodes: List[NetworkGraphNode] = Field(..., min_items=1, description="Nodes for network graph chart.")
    edges: List[NetworkGraphEdge] = Field(..., description="Edges for network graph chart.")


class NetworkGraphOptions(BaseModel):
    data: NetworkGraphData = Field(...,
                                   description="Data for network graph chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")


class OrganizationChartData(BaseModel):
    name: str = Field(..., description="Name of the person or role.")
    description: Optional[str] = Field(None, description="Description of the person or role.")
    children: Optional[List["OrganizationChartData"]] = Field(None, description="Children in the organization chart.")


class OrganizationChartOptions(BaseModel):
    data: OrganizationChartData = Field(...,
                                        description="Data for organization chart, such as, { name: 'CEO', description: 'Chief Executive Officer', children: [{ name: 'CTO', description: 'Chief Technology Officer', children: [{ name: 'Dev Manager', description: 'Development Manager' }] }] }.")
    orient: Literal["horizontal", "vertical"] = Field("vertical",
                                                      description="Orientation of the organization chart, either horizontal or vertical. Default is vertical, when the level of the chart is more than 3, it is recommended to use horizontal orientation.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")


class PathMapData(BaseModel):
    data: List[str] = Field(..., min_items=1, description="""
    A list of keywords for the names of points of interest (POIs) in Chinese. These POIs usually contain a group of places with similar locations, so the names should be more descriptive, must adding attributives to indicate that they are different places in the same area, such as "北京市" is better than "北京", "杭州西湖" is better than "西湖"; in addition, if you can determine that a location may appear in multiple areas, you can be more specific, such as "杭州西湖的苏堤春晓" is better than "苏堤春晓". The tool will use these keywords to search for specific POIs and query their detailed data, such as latitude and longitude, location photos, etc. For example, ["西安钟楼", "西安大唐不夜城", "西安大雁塔"]""
    """)


class PathMapOptions(BaseModel):
    title: str = Field(...,
                       description="The map title should not exceed 16 characters. The content should be consistent with the information the map wants to convey and should be accurate, rich, creative, and attractive.")
    data: List[PathMapData] = Field(..., min_items=1, description="""
    Routes, each group represents all POIs along a route. For example, [{ "data": ["西安钟楼", "西安大唐不夜城", "西安大雁塔"] }, { "data": ["西安曲江池公园", "西安回民街"] }]
    """)
    width: int = Field(1600, description="Set the width of map, default is 1600.")
    height: int = Field(1000, description="Set the height of map, default is 1000.")


class PieChartData(BaseModel):
    category: str = Field(..., description="Category for pie chart data.")
    value: float = Field(..., description="Value for pie chart data.")


class PieChartOptions(BaseModel):
    data: List[PieChartData] = Field(..., min_items=1,
                                     description="Data for pie chart, such as, [{ category: '分类一', value: 27 }].")
    innerRadius: float = Field(0, ge=0, le=1,
                               description="Set the innerRadius of pie chart, the value between 0 and 1. Set the pie chart as a donut chart. Set the value to 0.6 or number in [0 ,1] to enable it.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class PinMapMarkerPopup(BaseModel):
    type: str = Field("image", description="""Must be "image".""")
    width: int = Field(40, description="Width of the photo.")
    height: int = Field(40, description="Height of the photo.")
    borderRadius: int = Field(8, description="Border radius of the photo.")


class PinMapOptions(BaseModel):
    title: str = Field(...,
                       description="The map title should not exceed 16 characters. The content should be consistent with the information the map wants to convey and should be accurate, rich, creative, and attractive.")
    data: List[str] = Field(..., min_items=1, description="""
    A list of keywords for the names of points of interest (POIs) in Chinese. These POIs usually contain a group of places with similar locations, so the names should be more descriptive, must adding attributives to indicate that they are different places in the same area, such as "北京市" is better than "北京", "杭州西湖" is better than "西湖"; in addition, if you can determine that a location may appear in multiple areas, you can be more specific, such as "杭州西湖的苏堤春晓" is better than "苏堤春晓". The tool will use these keywords to search for specific POIs and query their detailed data, such as latitude and longitude, location photos, etc. For example, ["西安钟楼", "西安大唐不夜城", "西安大雁塔"]
    """)
    markerPopup: Optional[PinMapMarkerPopup] = Field(None,
                                                     description="Marker type, one is simple mode, which is just an icon and does not require `markerPopup` configuration; the other is image mode, which displays location photos and requires `markerPopup` configuration. Among them, `width`/`height`/`borderRadius` can be combined to realize rectangular photos and square photos. In addition, when `borderRadius` is half of the width and height, it can also be a circular photo.")
    width: int = Field(1600, description="Set the width of map, default is 1600.")
    height: int = Field(1000, description="Set the height of map, default is 1000.")


class RadarChartData(BaseModel):
    name: str = Field(..., description="Name for radar chart data.")
    value: float = Field(..., description="Value for radar chart data.")
    group: Optional[str] = Field(None, description="Group for radar chart data.")


class RadarChartOptions(BaseModel):
    data: List[RadarChartData] = Field(..., min_items=1,
                                       description="Data for radar chart, such as, [{ name: 'Design', value: 70 }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class SankeyChartData(BaseModel):
    source: str = Field(..., description="Source node of the link.")
    target: str = Field(..., description="Target node of the link.")
    value: float = Field(..., description="Value of the link.")


class SankeyChartOptions(BaseModel):
    data: List[SankeyChartData] = Field(..., min_items=1,
                                        description="Date for sankey chart, such as, [{ source: 'Landing Page', target: 'Product Page', value: 50000 }, { source: 'Product Page', target: 'Add to Cart', value: 35000 }, { source: 'Add to Cart', target: 'Checkout', value: 25000 }, { source: 'Checkout', target: 'Payment', value: 15000 }, { source: 'Payment', target: 'Purchase Completed', value: 8000 }].")
    nodeAlign: Literal["left", "right", "justify", "center"] = Field("center",
                                                                     description="Alignment of nodes in the sankey chart, such as, 'left', 'right', 'justify', or 'center'.")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class ScatterChartData(BaseModel):
    x: float = Field(..., description="X-coordinate for scatter chart data.")
    y: float = Field(..., description="Y-coordinate for scatter chart data.")


class ScatterChartOptions(BaseModel):
    data: List[ScatterChartData] = Field(..., min_items=1,
                                         description="Data for scatter chart, such as, [{ x: 10, y: 15 }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class TreemapChartData(BaseModel):
    name: str = Field(..., description="Name for treemap chart data.")
    value: float = Field(..., description="Value for treemap chart data.")
    children: Optional[List["TreemapChartData"]] = Field(None, description="Children for treemap chart data.")


class TreemapChartOptions(BaseModel):
    data: List[TreemapChartData] = Field(..., min_items=1,
                                         description="Data for treemap chart, such as, [{ name: 'Design', value: 70, children: [{ name: 'Tech', value: 20 }] }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class VennChartData(BaseModel):
    label: Optional[str] = Field(None, description="Label for the venn chart segment, such as 'A', 'B', or 'C'.")
    value: float = Field(..., description="Value for the venn chart segment, such as 10, 20, or 30.")
    sets: List[str] = Field(...,
                            description="Array of set names that this segment belongs to, such as ['A', 'B'] for an intersection between sets A and B.")


class VennChartOptions(BaseModel):
    data: List[VennChartData] = Field(..., min_items=1,
                                      description="Data for venn chart, such as, [{ label: 'A', value: 10, sets: ['A'] }, { label: 'B', value: 20, sets: ['B'] }, { label: 'C', value: 30, sets: ['C'] }, { label: 'AB', value: 5, sets: ['A', 'B'] }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


class ViolinPlotData(BaseModel):
    category: str = Field(..., description="Category of the data point, such as '分类一'.")
    value: float = Field(..., description="Value of the data point, such as 10.")
    group: Optional[str] = Field(None,
                                 description="Optional group for the data point, used for grouping in the violin chart.")


class ViolinPlotOptions(BaseModel):
    data: List[ViolinPlotData] = Field(..., min_items=1,
                                       description="Data for violin chart, such as, [{ category: '分类一', value: 10 }] or [{ category: '分类二', value: 20, group: '组别一' }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")
    axisXTitle: str = Field("", description="Set the x-axis title of chart.")
    axisYTitle: str = Field("", description="Set the y-axis title of chart.")


class WordCloudChartData(BaseModel):
    value: float = Field(..., description="Value for word cloud chart data.")
    text: str = Field(..., description="Text for word cloud chart data.")


class WordCloudChartOptions(BaseModel):
    data: List[WordCloudChartData] = Field(..., min_items=1,
                                           description="Data for word cloud chart, such as, [{ value: 4.272, text: '形成' }].")
    theme: Literal["default", "academy"] = Field("default",
                                                 description="Set the theme for the chart, optional, default is 'default'.")
    texture: Literal["default", "rough"] = Field("default",
                                                 description="Set the texture for the chart, optional, default is 'default'. 'rough' refers to hand-drawn style.")
    width: int = Field(600, description="Set the width of chart, default is 600.")
    height: int = Field(400, description="Set the height of chart, default is 400.")
    title: str = Field("", description="Set the title of chart.")


def render_chart(chart_type: ChartType, options: BaseModel, output_path: str):
    chart = Chart(chart_type, options, output_path)
    chart.render()


def render_area_chart(options: AreaChartOptions, output_path: str):
    render_chart('area', options, output_path)


def render_bar_chart(options: BarChartOptions, output_path: str):
    render_chart('bar', options, output_path)


def render_boxplot_chart(options: BoxPlotOptions, output_path: str):
    render_chart('boxplot', options, output_path)


def render_column_chart(options: ColumnChartOptions, output_path: str):
    render_chart('column', options, output_path)


def render_district_map_chart(options: DistrictMapOptions, output_path: str):
    render_chart('district-map', options, output_path)


def render_dual_axes_chart(options: DualAxesOptions, output_path: str):
    render_chart('dual-axes', options, output_path)


def render_fishbone_diagram_chart(options: FishboneDiagramOptions, output_path: str):
    render_chart('fishbone-diagram', options, output_path)


def render_flow_diagram_chart(options: FlowDiagramOptions, output_path: str):
    render_chart('flow-diagram', options, output_path)


def render_funnel_chart(options: FunnelChartOptions, output_path: str):
    render_chart('funnel', options, output_path)


def render_histogram_chart(options: HistogramOptions, output_path: str):
    render_chart('histogram', options, output_path)


def render_line_chart(options: LineChartOptions, output_path: str):
    render_chart('line', options, output_path)


def render_liquid_chart(options: LiquidChartOptions, output_path: str):
    render_chart('liquid', options, output_path)


def render_mind_map_chart(options: MindMapOptions, output_path: str):
    render_chart('mind-map', options, output_path)


def render_network_graph_chart(options: NetworkGraphOptions, output_path: str):
    render_chart('network-graph', options, output_path)


def render_organization_chart(options: OrganizationChartOptions, output_path: str):
    render_chart('organization-chart', options, output_path)


def render_path_map_chart(options: PathMapOptions, output_path: str):
    render_chart('path-map', options, output_path)


def render_pie_chart(options: PieChartOptions, output_path: str):
    render_chart('pie', options, output_path)


def render_pin_map_chart(options: PinMapOptions, output_path: str):
    render_chart('pin-map', options, output_path)


def render_radar_chart(options: RadarChartOptions, output_path: str):
    render_chart('radar', options, output_path)


def render_sankey_chart(options: SankeyChartOptions, output_path: str):
    render_chart('sankey', options, output_path)


def render_scatter_chart(options: ScatterChartOptions, output_path: str):
    render_chart('scatter', options, output_path)


def render_treemap_chart(options: TreemapChartOptions, output_path: str):
    render_chart('treemap', options, output_path)


def render_venn_chart(options: VennChartOptions, output_path: str):
    render_chart('venn', options, output_path)


def render_violin_chart(options: ViolinPlotOptions, output_path: str):
    render_chart('violin', options, output_path)


def render_word_cloud_chart(options: WordCloudChartOptions, output_path: str):
    render_chart('word-cloud', options, output_path)
