from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import File
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

async def generate_visualization(
    file_id: int,
    viz_type: str,
    x_column: Optional[str],
    y_column: Optional[str],
    parameters: Dict[str, Any],
    user_id: int,
    db: Session
) -> dict:
    """
    Generate visualization data from uploaded files.
    """
    
    try:
        # Get file from database
        file = db.query(File).filter(
            File.id == file_id,
            File.user_id == user_id
        ).first()
        
        if not file:
            raise ValueError("File not found")
        
        # Load data
        file_path: str = str(file.file_path)  # type: ignore
        df = pd.read_csv(file_path)
        
        # Generate visualization based on type
        if viz_type == "bar":
            fig = px.bar(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "line":
            fig = px.line(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "scatter":
            fig = px.scatter(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "pie":
            fig = px.pie(df, names=x_column, values=y_column, **parameters)
        elif viz_type == "histogram":
            fig = px.histogram(df, x=x_column, **parameters)
        elif viz_type == "3d_scatter":
            # parameters may include 'z' or 'z_column', 'color'
            z_col = parameters.get("z") or parameters.get("z_column")
            if not z_col:
                raise ValueError("3d_scatter requires a 'z' (z-column) parameter")
            fig = px.scatter_3d(df, x=x_column, y=y_column, z=z_col, **{k: v for k, v in parameters.items() if k not in ("z", "z_column")})
        elif viz_type == "animated":
            # parameters must supply 'animation_frame' column name
            anim_col = parameters.get("animation_frame")
            if not anim_col:
                raise ValueError("animated visualization requires 'animation_frame' parameter")
            fig = px.scatter(df, x=x_column, y=y_column, animation_frame=anim_col, **{k: v for k, v in parameters.items() if k != "animation_frame"})
        elif viz_type == "choropleth":
            # parameters should include 'locations' and 'color'
            locations = parameters.get("locations")
            color = parameters.get("color")
            if not locations or not color:
                raise ValueError("choropleth requires 'locations' and 'color' parameters")
            fig = px.choropleth(df, locations=locations, color=color, geojson=parameters.get("geojson"), **{k: v for k, v in parameters.items() if k not in ("locations", "color", "geojson")})
        elif viz_type == "mapbox_bubble":
            # parameters should include lat/lon
            lat = parameters.get("lat")
            lon = parameters.get("lon")
            if not lat or not lon:
                raise ValueError("mapbox_bubble requires 'lat' and 'lon' parameters")
            fig = px.scatter_mapbox(df, lat=lat, lon=lon, size=parameters.get("size"), color=parameters.get("color"), zoom=parameters.get("zoom", 1), height=parameters.get("height"))
        elif viz_type == "network":
            # Expect parameters: source, target, optional value
            src = parameters.get("source")
            tgt = parameters.get("target")
            val = parameters.get("value")
            if not src or not tgt:
                raise ValueError("network visualization requires 'source' and 'target' parameters")
            # Build node list and link indices
            sources = df[src].astype(str).tolist()
            targets = df[tgt].astype(str).tolist()
            nodes = list(dict.fromkeys(sources + targets))
            node_index = {n: i for i, n in enumerate(nodes)}
            links = []
            for i in range(len(sources)):
                link = {"source": node_index[sources[i]], "target": node_index[targets[i]]}
                if val:
                    try:
                        link["value"] = float(df[val].iloc[i])
                    except Exception:
                        link["value"] = 1
                else:
                    link["value"] = 1
                links.append(link)

            sankey_data = go.Figure(data=[
                go.Sankey(node={"label": nodes}, link={"source": [l["source"] for l in links], "target": [l["target"] for l in links], "value": [l["value"] for l in links]})
            ])
            # For network-like visualization we return a sankey layout if requested
            fig = sankey_data
        elif viz_type == "sankey":
            # parameters: source, target, value
            src = parameters.get("source")
            tgt = parameters.get("target")
            val = parameters.get("value")
            if not src or not tgt or not val:
                raise ValueError("sankey requires 'source','target','value' parameters")
            sources = df[src].astype(str).tolist()
            targets = df[tgt].astype(str).tolist()
            values = df[val].astype(float).tolist()
            nodes = list(dict.fromkeys(sources + targets))
            node_index = {n: i for i, n in enumerate(nodes)}
            link_src = [node_index[s] for s in sources]
            link_tgt = [node_index[t] for t in targets]
            fig = go.Figure(data=[
                go.Sankey(node={"label": nodes}, link={"source": link_src, "target": link_tgt, "value": values})
            ])
        elif viz_type == "treemap":
            # parameters: path (list of columns) or use x_column as path
            path = parameters.get("path") or ([x_column] if x_column else None)
            values = parameters.get("values") or y_column
            if not path:
                raise ValueError("treemap requires 'path' parameter or an x_column")
            fig = px.treemap(df, path=path, values=values, **{k: v for k, v in parameters.items() if k not in ("path", "values")})
        else:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
        
        # Convert to JSON
        fig_json = fig.to_json()
        if fig_json is None:
            raise ValueError("Failed to serialize visualization")
        viz_json = json.loads(fig_json)
        
        return viz_json
        
    except Exception as e:
        raise ValueError(f"Error generating visualization: {str(e)}")
