from typing import Any
import pandas as pd


class CSVHandler:
    path: str
    file: pd.DataFrame | None = None

    def __init__(self, path):
        self.path = path
        self.file = None

    def read(self):
        self.file = pd.read_csv(self.path, sep=";")

    def get(self, column: str, value: Any):
        if self.file is None:
            raise ValueError("File needs to be read first")
        return self.file[self.file[column] == value]

    def filter_by_column(self, column: str, value: str):
        if self.file is None:
            raise ValueError("File needs to be read first")
        return self.file[self.file[column] == value]

    def filter_by_columns(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        result = self.file
        for column, value in filters.items():
            result = result[result[column] == value]
        self.file = result

    def filter_by_columns_or(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        if not filters:
            return
        conditions = [
            self.file[column] == value for column, value in filters.items()
        ]
        combined_condition = conditions.pop()
        for condition in conditions:
            combined_condition |= condition
        self.file = self.file[combined_condition]

    def filter_by_columns_and(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        if not filters:
            return
        conditions = [
            self.file[column] == value for column, value in filters.items()
        ]
        combined_condition = conditions.pop()
        for condition in conditions:
            combined_condition &= condition
        self.file = self.file[combined_condition]

    def filter_by_columns_not(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        result = self.file
        for column, value in filters.items():
            result = result[result[column] != value]
        self.file = result

    def filter_by_columns_or_not(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        if not filters:
            return
        conditions = [
            self.file[column] != value for column, value in filters.items()
        ]
        combined_condition = conditions.pop()
        for condition in conditions:
            combined_condition |= condition
        self.file = self.file[combined_condition]

    def filter_by_columns_and_not(self, filters: dict):
        if self.file is None:
            raise ValueError("File needs to be read first")
        if not filters:
            return
        conditions = [
            self.file[column] != value for column, value in filters.items()
        ]
        combined_condition = conditions.pop()
        for condition in conditions:
            combined_condition &= condition
        self.file = self.file[combined_condition]

    def concat_dataframes(
        self, other_csv_path: str, common_column: str, excludent: bool = True
    ):
        if self.file is None:
            raise ValueError("File needs to be read first")

        other_df = pd.read_csv(other_csv_path)

        if excludent:
            self.file = pd.merge(
                self.file, other_df, on=common_column, how="inner"
            )
        else:
            self.file = pd.merge(
                self.file, other_df, on=common_column, how="outer"
            )

    def write(self):
        if self.file is None:
            raise ValueError("File needs to be read first")
        self.file.to_csv(self.path, index=False)
