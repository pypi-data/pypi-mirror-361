import polars as pl
import pyarrow as pa

class GeoArrow:
    def __init__(self, arrow_table: pa.Table = None):
        self.arrow_table = arrow_table  # Store the PyArrow table directly

    def __repr__(self):
        """Return a string representation of the GeoArrow as a PyArrow table."""
        if self.arrow_table is None:
            return "GeoArrow(arrow_table=None)"
        
        return f"{self.arrow_table}"

    def to_dataframe(self) -> pl.DataFrame:
        """Converts the PyArrow table to a Polars DataFrame."""
        # Convert the PyArrow table to a Polars DataFrame
        self.geom_df = pl.from_arrow(self.arrow_table)
        return self.geom_df

    def add_column(self, name: str, values: pa.Array) -> None:
        """Add a column to the PyArrow table."""
        if self.arrow_table is not None:
            # Add the new column to the PyArrow table
            self.arrow_table = self.arrow_table.append_column(name, values)
        else:
            raise ValueError("Arrow table is not initialized.")
    
    def filter_rows(self, condition: pl.Expr) -> pl.DataFrame:
        """Filter rows based on a condition using Polars expressions."""
        if self.arrow_table is not None:
            df = pl.from_arrow(self.arrow_table)
            return df.filter(condition)
        else:
            raise ValueError("Arrow table is not initialized.")
