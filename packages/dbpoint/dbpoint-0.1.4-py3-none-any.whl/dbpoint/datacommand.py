import loguru
from .datacolumn import DataColumn
from datetime import datetime

class DataCommand():

    def __init__(self, sql_command: str | None = None):
        self.command: str = sql_command
        self.query_cols: list[DataColumn] | None = None 
        self.command_with_error: str = None
        self.profile_name: str = None
        self.last_run_datetime: datetime = None
        # last_error
        # last erroneous command
        # last time used
        # count of rows
        # name of profile (alias)

