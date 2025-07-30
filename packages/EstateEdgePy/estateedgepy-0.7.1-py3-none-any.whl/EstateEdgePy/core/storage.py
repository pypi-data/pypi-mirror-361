from typing import Optional, List
import pandas as pd
from pyarrow import Table

from EstateEdgePy.filters._base_filter_ import BaseFilter
from EstateEdgePy.src._client import EstateEdgeClient


class PropertyResult:
    """
    A wrapper class for property data results retrieved as a pyarrow Table.

    This class provides convenient methods for working with property data, including
    conversion to pandas DataFrames and passthrough access to underlying pyarrow.Table methods.

    Attributes:
        data (pyarrow.Table): The underlying pyarrow Table containing property data.
    """
    def __init__(self, data: Table):
        """
        Initialize the PropertyResult with a pyarrow Table.

        Args:
            data (Table): The pyarrow Table containing property data.
        """
        self.data = data

    def to_pandas(self, columns: Optional[list[str]] = None) -> pd.DataFrame:
        """
        Convert the property data to a pandas DataFrame.

        Optionally selects specific columns from the pyarrow Table.

        Args:
            columns (Optional[List[str]]): A list of column names to include in the DataFrame.
                If None, all columns are included.

        Returns:
            pd.DataFrame: A pandas DataFrame representation of the property data.
        """
        df = self.data.to_pandas()
        return df[columns] if columns else df

    def __getattr__(self, attr):
        """
        Delegate attribute access to the underlying pyarrow Table.

        This allows calling pyarrow.Table methods directly on the PropertyResult instance.

        Args:
            attr (str): The attribute name.

        Returns:
            Any: The corresponding attribute or method from the underlying pyarrow Table.
        """

        return getattr(self.data, attr)  # Allow passthrough to the pyarrow.Table object


class PropertyService:
    """A service class for retrieving and processing property data from EstateEdge.

    This class provides methods to fetch property data, apply filters, and convert
    the data to pandas DataFrames for easier analysis.

    Args:
        client (EstateEdgeClient): An authenticated client for EstateEdge API access.
    """

    def __init__(self, client: EstateEdgeClient) -> None:
        """Initialize the PropertyService with an EstateEdge client.

        Args:
            client: An authenticated EstateEdgeClient instance for API access.
        """
        self.client = client

    async def get_filtered(
            self,
            state: str,
            filter_items: Optional[List[BaseFilter]] = None
    ) -> PropertyResult:
        """Retrieve property data for a state with optional filtering.

        Fetches property data from the API and applies the specified filters sequentially.
        Returns the data as a pyarrow Table for efficient processing.

        Args:
            state: The state code (e.g., 'CA') to fetch properties for.
            filter_items: Optional list of filter objects to apply to the data.

        Returns:
            A pyarrow Table containing the filtered property data.

        Example:
            >>> from EstateEdgePy import PropertyService, PriceRangeFilter

            >>> service = PropertyService(client)  # create an object of the client
            >>> all_filters = [PriceRangeFilter(min_price=500000)]
            >>> filtered_data = await service.get_filtered('CA', all_filters)
        """
        raw_data = await self.client.get_property_table(state)
        if filter_items:
            for filter_item in filter_items:
                raw_data = filter_item.apply(raw_data)
        return PropertyResult(raw_data)
