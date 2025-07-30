"""
Models for dataframe tools using pandas-ai
"""

from typing import Any

from pydantic import BaseModel, Field

from . import ToolOutput


class DataFrameQueryInput(BaseModel):
    """Input for querying a pandas DataFrame using natural language"""

    dataframe: Any = Field(description="The pandas DataFrame to query")
    query: str = Field(description="Natural language query to execute on the dataframe")

    class Config:
        arbitrary_types_allowed = True


class DataFrameQueryOutput(ToolOutput):
    """Output from DataFrame query execution"""

    result: Any = Field(
        description=(
            "The result of the query execution - can be a string, number, "
            "dataframe as dict, or dataframe"
        )
    )
    result_type: str = Field(
        description="The type of result returned (string, number, dataframe, list)"
    )
    query_executed: str = Field(description="The original query that was executed")
