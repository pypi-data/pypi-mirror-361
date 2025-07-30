from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.dataframe_ai_models import DataFrameQueryInput, DataFrameQueryOutput

__all__ = ["DataFrameQueryInput", "DataFrameQueryOutput", "query"]


def query(*, dataframe: Any, query: str) -> DataFrameQueryOutput:
    """
    Query a pandas DataFrame using natural language through pandas-ai.

    This tool uses pandas-ai with OpenAI as the LLM to execute natural language
    queries on pandas DataFrames. The output is restricted to exclude ChartResponse
    types and can return numbers, strings, DataFrames (as dict), or lists.

    Note: pandas-ai may have compatibility issues with certain numpy/pandas versions.
    If pandas-ai is not available due to import errors, this tool will provide
    a helpful error message.

    Args:
        input: DataFrameQueryInput containing the DataFrame and query

    Returns:
        DataFrameQueryOutput with the query result and metadata

    Raises:
        ValueError: If OpenAI API key is missing, or input is invalid
        RuntimeError: If the query execution fails
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DataFrameQueryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="dataframe_ai", name="query", input=input_model.model_dump()
    )
    return DataFrameQueryOutput.model_validate(output_model)
