from .geojson import GeoJSON
from .geoparquet import GeoParquet
from .geoarrow import GeoArrow
from .kml import KML

import json
from urllib.request import urlopen
import pyarrow.parquet as pq
import pyarrow.feather as pf
import xml.etree.ElementTree as ET
from shapely import wkb, wkt
import pyarrow as pa




def write_geojson(geojson: GeoJSON, filename: str, indent=None):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(geojson.to_dict(), f, indent=indent)

def read_geojson(file_path: str) -> GeoJSON:
    with open(file_path) as response:
        geo_json_data = json.load(response)
    return GeoJSON.from_dict(geo_json_data)

def read_geojson_url(url: str) -> GeoJSON:
    with urlopen(url) as response:
        geo_json_data = json.load(response)
    return GeoJSON.from_dict(geo_json_data)

def read_kml(file_path: str) -> KML:
    """
    Convert KML file to a KML object by parsing the contents of the KML file.
    
    Args:
    file_path (str): Path to the KML file.

    Returns:
    KML: KML object representing the contents of the KML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_kml = file.read()  # Read the raw KML content

    tree = ET.ElementTree(ET.fromstring(raw_kml))
    root = tree.getroot()
    
    kml_data = KML(raw_kml)  # Create a new KML object with raw content
    
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

    for placemark in root.findall('.//kml:Placemark', namespace):
        name_elem = placemark.find('kml:name', namespace)
        description_elem = placemark.find('kml:description', namespace)
        
        point_elem = placemark.find('kml:Point/kml:coordinates', namespace)
        line_elem = placemark.find('kml:LineString/kml:coordinates', namespace)
        polygon_elem = placemark.find('kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespace)

        # Extract coordinates
        if point_elem is not None:
            coordinates = list(map(float, point_elem.text.strip().split(',')))
            kml_data.add_placemark(
                name=name_elem.text if name_elem is not None else 'Unnamed',
                description=description_elem.text if description_elem is not None else '',
                coordinates=[[coordinates[0],coordinates[1]]],  # Wrap in a list for consistency
                feature_type='Point'
            )
        elif line_elem is not None:
            coordinates = [list(map(float, coord.split(','))) for coord in line_elem.text.strip().split()]
            kml_data.add_placemark(
                name=name_elem.text if name_elem is not None else 'Unnamed LineString',
                description=description_elem.text if description_elem is not None else '',
                coordinates=coordinates,
                feature_type='LineString'
            )
        elif polygon_elem is not None:
            coordinates = [list(map(float, coord.split(','))) for coord in polygon_elem.text.strip().split()]
            kml_data.add_placemark(
                name=name_elem.text if name_elem is not None else 'Unnamed Polygon',
                description=description_elem.text if description_elem is not None else '',
                coordinates=[coordinates],  # Wrap in another list to represent a polygon
                feature_type='Polygon'
            )


    return kml_data


def read_parquet(file_path: str) -> GeoParquet:
    arrow_table = pq.read_table(file_path)
    geometries = arrow_table['geometry'].to_pylist()

    if geometries is None:
        raise ValueError("Geometries have not been loaded. Call the 'read_parquet' function first.")
    else:
        wkt_geometries = [wkb.loads(geom).wkt for geom in geometries]
        new_data = {col: arrow_table[col] for col in arrow_table.column_names}
        new_data['geometry'] = wkt_geometries
        new_arrow_table = pa.Table.from_pydict(new_data)
        geo_parquet = GeoParquet(new_arrow_table)

    return geo_parquet

def read_geoarrow(file_path: str, geometry_format: str ='wkb') -> GeoArrow:
    arrow_table = pf.read_table(file_path)
    
    if geometry_format == 'wkb':
        geometries = arrow_table['geometry'].to_pylist()

        if geometries is None:
            raise ValueError("Geometries have not been loaded. Call the 'read_parquet' function first.")

        else:
            wkt_geometries = [wkb.loads(geom).wkt for geom in geometries]
            new_data = {col: arrow_table[col] for col in arrow_table.column_names}
            new_data['geometry'] = wkt_geometries
            new_arrow_table = pa.Table.from_pydict(new_data)
            geo_arrow = GeoArrow(new_arrow_table)


    elif geometry_format == 'interleaved':
        geometries = arrow_table['geometry'].to_pylist()

        if geometries is None:
            raise ValueError("Geometries have not been loaded. Call the 'read_parquet' function first.")

        else:
            wkt_geometries = [print(geom) for geom in geometries]
            new_data = {col: arrow_table[col] for col in arrow_table.column_names}
            new_data['geometry'] = wkt_geometries
            new_arrow_table = pa.Table.from_pydict(new_data)
            geo_arrow = GeoArrow(new_arrow_table)

    elif geometry_format == 'arrow':
        geo_arrow = GeoArrow(arrow_table)
        # geo_arrow = arrow_table

    elif geometry_format == 'wkt':
        geometries = arrow_table['geometry'].to_pylist()

        if geometries is None:
            raise ValueError("Geometries have not been loaded. Call the 'read_parquet' function first.")
        else:
            wkt_geometries = [wkt.loads(geom).wkt for geom in geometries]
            new_data = {col: arrow_table[col] for col in arrow_table.column_names}
            new_data['geometry'] = wkt_geometries
            new_arrow_table = pa.Table.from_pydict(new_data)
            geo_arrow = GeoArrow(new_arrow_table)


    return geo_arrow
