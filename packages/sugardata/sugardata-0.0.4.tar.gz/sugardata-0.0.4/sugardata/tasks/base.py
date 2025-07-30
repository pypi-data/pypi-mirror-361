import pandas as pd
from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class NlpTask(ABC):

    def __init__(self, config: BaseModel):
        self.config = config

    @abstractmethod
    def generate(self, *args, **kwargs) -> None:
        pass

    def _convert_to_output(self, parsed_data: List[Dict[str, Any]], obj: BaseModel) -> Any:
        export_type = self.config.export_type
        if export_type == "dataframe":
            return pd.DataFrame(parsed_data)
        if export_type == "default":
            return parsed_data
        if export_type == "hg":
            try:
                from datasets import Dataset
            except ImportError:
                raise ImportError("Please install `datasets` package to use this feature.")
            return Dataset.from_pandas(pd.DataFrame(parsed_data))
        if export_type == "pydantic":
            return [obj(**item) for item in parsed_data]
        raise ValueError(f"Unsupported output type: {export_type}")
    
    async def _convert_to_output_async(self, parsed_data: List[Dict[str, Any]], obj: BaseModel) -> Any:
        export_type = self.config.export_type
        if export_type == "dataframe":
            return pd.DataFrame(parsed_data)
        if export_type == "default":
            return parsed_data
        if export_type == "hg":
            try:
                from datasets import Dataset
            except ImportError:
                raise ImportError("Please install `datasets` package to use this feature.")
            return Dataset.from_pandas(pd.DataFrame(parsed_data))
        if export_type == "pydantic":
            return [obj(**item) for item in parsed_data]
        raise ValueError(f"Unsupported output type: {export_type}")
