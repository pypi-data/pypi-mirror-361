import polars as pl
import pyarrow as pa

class GeoParquet:
    def __init__(self, arrow_table: pa.Table = None):
        self.arrow_table = arrow_table  # Store the PyArrow table directly

    def __repr__(self):
        """Return a string representation of the GeoParquet as a PyArrow table."""
        if self.arrow_table is None:
            return "GeoParquet(arrow_table=None)"
        
        return f"{self.arrow_table}"

    def to_dataframe(self) -> pl.DataFrame:
        """Converts the geometries to a Polars DataFrame."""
        # Create a Polars DataFrame from the list of geometries
        self.geom_df = pl.from_arrow(self.arrow_table)
        return self.geom_df