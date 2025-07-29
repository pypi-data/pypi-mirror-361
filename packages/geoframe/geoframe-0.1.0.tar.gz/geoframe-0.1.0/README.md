# GeoFrame


## Geometry Representation

| Format          | Representation                                                                                                               |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **WKT**         | `POLYGON((0 0, 1 0, 1 1, 0 0))`                                                                                              |
| **WKB** (hex)   | `0103000000010000000400000000000000000000000000000000000000000000000000F03F000000000000F03F00000000000000000000000000000000` |
| **Coordinates** | `[[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]]`                                                                         |





## Geospatial File Formats

| Element (KML)       | Object (GeoJSON)      | Object (GeoArrow)   | Object (GeoParquet) | Description                                                                                           |
|---------------------|-----------------------|---------------------|---------------------|-------------------------------------------------------------------------------------------------------|
| **Placemark**       | **Feature**            | **Feature**          | **Feature**          | Represents a specific point, line, or polygon feature with associated attributes and geometry.         |
| **Document**        | **FeatureCollection**  | **FeatureCollection**| **FeatureCollection**| A container for multiple features, such as placemarks, that are grouped together.                      |
| **Folder**          | None                  | None                | None                | Organizes features or other folders within a KML document. It can be used to create hierarchical structures. |
| **LineString**      | **LineString**         | **LineString**       | **LineString**       | Represents a line or a set of connected line segments.                                                 |
| **Polygon**         | **Polygon**            | **Polygon**          | **Polygon**          | Represents a closed shape with a boundary formed by a series of connected straight lines.              |
| **MultiGeometry**   | **GeometryCollection** | **GeometryCollection**| **GeometryCollection**| Represents a collection of multiple geometries, such as points, lines, or polygons.                   |
| **Style**           | **Style**              | None                 | None                 | Defines the visual appearance of features, such as colors, line styles, and icons.                     |
| **ExtendedData**    | **Properties**         | **Properties**       | **Properties**       | Allows additional custom data to be associated with a feature. In GeoJSON, properties are used similarly. |
| **Coordinates**     | **Coordinates**        | **Coordinates**      | **Coordinates**      | Specifies a single point in latitude, longitude, and optionally, altitude. Coordinates in GeoJSON have a similar structure. |
| **TimeStamp/TimeSpan** | None                | None                 | None                 | Provides the ability to visualize time-based geographic data.                                          |



