from typing import Optional, List
import pandas as pd
from pyarrow import Table

from SanctionSightPy.filters.base_filter import BaseFilter
from SanctionSightPy.src._client import SanctionClient


class SanctionResult:
    """
    A wrapper class for sanction data results retrieved as a pyarrow Table.

    This class provides convenient methods for working with sanction data, including
    conversion to pandas DataFrames and passthrough access to underlying pyarrow.Table methods.

    Attributes:
        data (pyarrow.Table): The underlying pyarrow Table containing sanction data.
    """
    def __init__(self, data: Table):
        """
        Initialize the SanctionResult with a pyarrow Table.

        Args:
            data (Table): The pyarrow Table containing sanction data.
        """
        self.data = data

    def to_pandas(self, columns: Optional[list[str]] = None) -> pd.DataFrame:
        """
        Convert the sanction data to a pandas DataFrame.

        Optionally selects specific columns from the pyarrow Table.

        Args:
            columns (Optional[List[str]]): A list of column names to include in the DataFrame.
                If None, all columns are included.

        Returns:
            pd.DataFrame: A pandas DataFrame representation of the sanction data.
        """
        df = self.data.to_pandas()
        return df[columns] if columns else df

    def __getattr__(self, attr):
        """
        Delegate attribute access to the underlying pyarrow Table.

        This allows calling pyarrow.Table methods directly on the SanctionResult instance.

        Args:
            attr (str): The attribute name.

        Returns:
            Any: The corresponding attribute or method from the underlying pyarrow Table.
        """

        return getattr(self.data, attr)  # Allow passthrough to the pyarrow.Table object


class SanctionService:
    """A service class for retrieving and processing sanction data from SanctionSightPy.

    This class provides methods to fetch sanction data, apply filters, and convert
    the data to pandas DataFrames for easier analysis.

    Args:
        client (SanctionClient): An authenticated client for SanctionClient API access.
    """

    def __init__(self, client: SanctionClient) -> None:
        """Initialize the PropertyService with an EstateEdge client.

        Args:
            client: An authenticated EstateEdgeClient instance for API access.
        """
        self.client = client

    async def get_filtered(
            self,
            agency: str,
            filter_items: Optional[List[BaseFilter]] = None
    ) -> SanctionResult:
        """Retrieve property data for a state with optional filtering.

        Fetches property data from the API and applies the specified filters sequentially.
        Returns the data as a pyarrow Table for efficient processing.

        Args:
            agency: The sanction agency code (e.g., 'uk_sanctions') to fetch properties for.
            filter_items: Optional list of filter objects to apply to the data.

        Returns:
            A SanctionResult Table containing the filtered property data.

        Example:
            >>> from SanctionSightPy import SanctionService, EntityFilter, DateRangeFilter

            # use asynchronous flow and not synchronous flow
            >>> service = SanctionService(client)  # create an object of the client
            >>> all_filters = [DateRangeFilter(min_price=500000), EntityFilter(min_bedrooms=3)]
            >>> filtered_data = await service.get_filtered('canada_sanction', all_filters)
        """
        raw_data = await self.client.get_sanction_data(agency)
        if filter_items:
            for filter_item in filter_items:
                raw_data = filter_item.apply(raw_data)
        return SanctionResult(raw_data)
