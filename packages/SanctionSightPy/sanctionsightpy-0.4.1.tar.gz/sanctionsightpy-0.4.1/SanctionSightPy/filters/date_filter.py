import pyarrow as pa
import pyarrow.compute as pc
from datetime import datetime
from typing import Optional, Union

from SanctionSightPy.src.utils import parse_date
from SanctionSightPy.filters.base_filter import BaseFilter


class DateRangeFilter(BaseFilter):
    def __init__(
            self,
            date_column: str,
            date_format: str,
            start_date: Optional[Union[str, datetime]] = None,
            end_date: Optional[Union[str, datetime]] = None,
    ):
        self.date_column = date_column
        self.date_format = date_format
        self.start_date = parse_date(start_date)
        self.end_date = parse_date(end_date)

        # Validate date range
        if (self.start_date and self.end_date and
            self.start_date > self.end_date):
            raise ValueError(
                f"Invalid date range: start_date ({self.start_date}) "
                f"cannot be after end_date ({self.end_date})"
            )

    def apply(self, data: pa.Table) -> pa.Table:
        # Check if column exists
        if self.date_column not in data.column_names:
            raise ValueError(
                f"Column '{self.date_column}' not found in data. "
                f"Available columns: {data.column_names}"
            )

        # Convert string dates to datetime64[ms] if needed
        if pa.types.is_string(data[self.date_column].type):
            try:
                # First try ISO format (YYYY-MM-DD)
                timestamps = pc.strptime(data[self.date_column], format=self.date_format, unit="ms")
            except Exception as error:
                raise ValueError(
                    f"Failed to parse '{self.date_column}' with format '{self.date_format}'.\n"
                    f"Original error: {error}\n"
                    f"Check through the column to know the date format to pass."
                )
        else:
            timestamps = data[self.date_column].cast("timestamp[ms]")

        # Return original data if no filtering needed
        if self.start_date is None and self.end_date is None:
            return data

        mask = None

        if self.start_date:
            start_ts = pa.scalar(self.start_date, type=pa.timestamp("ms"))
            start_mask = pc.greater_equal(timestamps, start_ts)
            mask = start_mask if mask is None else pc.and_(mask, start_mask)

        if self.end_date:
            end_ts = pa.scalar(self.end_date, type=pa.timestamp("ms"))
            end_mask = pc.less_equal(timestamps, end_ts)
            mask = end_mask if mask is None else pc.and_(mask, end_mask)

        return data.filter(mask) if mask is not None else data
