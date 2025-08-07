import json
import os
from typing import Dict, Any
from utils.logger import logger

class DataService:
    def __init__(self, data_file_path: str = "dummyData.json"):
        self.data_file_path = data_file_path
        self.sales_data = self._load_sales_data()

    def _load_sales_data(self) -> Dict[str, Any]:
        try:
            with open(self.data_file_path, "r") as f:
                data = json.load(f)
                logger.log_sync("SERVER", "DATA_LOADED", extra=f"Loaded {len(data.get('salesReps', []))} sales reps")
                return data
        except FileNotFoundError:
            logger.log_sync("SERVER", "DATA_ERROR", extra=f"File {self.data_file_path} not found")
            return {"salesReps": []}
        except Exception as e:
            logger.log_sync("SERVER", "DATA_ERROR", extra=f"Error loading data: {str(e)}")
            return {"salesReps": []}

    def get_sales_data(self) -> Dict[str, Any]:
        return self.sales_data

    def get_sales_reps(self) -> list:
        return self.sales_data.get("salesReps", [])

    def reload_data(self) -> Dict[str, Any]:
        self.sales_data = self._load_sales_data()
        return self.sales_data
