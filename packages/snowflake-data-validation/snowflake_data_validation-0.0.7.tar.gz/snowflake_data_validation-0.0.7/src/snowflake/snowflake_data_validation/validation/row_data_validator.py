import os

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    CHUNK_ID_COLUMN_KEY,
    CHUNK_MD5_VALUE_COLUMN_KEY,
    NEWLINE,
    RESULT_COLUMN_KEY,
    ROW_NUMBER_COLUMN_KEY,
    SOURCE_QUERY_COLUMN_KEY,
    TABLE_NAME_COLUMN_KEY,
    TARGET_QUERY_COLUMN_KEY,
    UNDERSCORE_MERGE_COLUMN_KEY,
    Platform,
    Result,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.validation.data_validator_base import (
    DataValidatorBase,
)


SOURCE_SUFFIX = "_SOURCE"
TARGET_SUFFIX = "_TARGET"
ROW_MD5_KEY = "ROW_MD5"
ROW_VALIDATION_REPORT_NAME = "{fully_qualified_name}_row_validation_report.csv"
ROW_VALIDATION_DIFF_QUERY_NAME = (
    "{fully_qualified_name}_{platform}_row_validation_diff_query.sql"
)
MD5_REPORT_QUERY_TEMPLATE = "SELECT * FROM {fully_qualified_name} WHERE {clause}"


class RowDataValidator(DataValidatorBase):
    def get_diff_md5_chunks(
        self,
        source_md5_df: pd.DataFrame,
        target_md5_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Get the differences in MD5 between source and target DataFrames.

        This function compares the MD5 of two DataFrames and returns a DataFrame containing
        the differences found, including chunk IDs and MD5 value.

        Args:
            source_md5_df (pd.DataFrame): The source DataFrame containing MD5.
            target_md5_df (pd.DataFrame): The target DataFrame containing MD5.

        Returns:
            pd.DataFrame: A DataFrame containing the differences in MD5.

        """
        source_intersection_target = pd.merge(
            source_md5_df,
            target_md5_df,
            on=[CHUNK_ID_COLUMN_KEY, CHUNK_MD5_VALUE_COLUMN_KEY],
            how="inner",
        )

        source_except_intersection = source_md5_df[
            ~source_md5_df[CHUNK_ID_COLUMN_KEY].isin(
                source_intersection_target[CHUNK_ID_COLUMN_KEY]
            )
        ]
        target_except_intersection = target_md5_df[
            ~target_md5_df[CHUNK_ID_COLUMN_KEY].isin(
                source_intersection_target[CHUNK_ID_COLUMN_KEY]
            )
        ]

        diff_df = pd.merge(
            source_except_intersection,
            target_except_intersection,
            on=[CHUNK_ID_COLUMN_KEY],
            how="left",
            suffixes=(SOURCE_SUFFIX, TARGET_SUFFIX),
        )

        return diff_df

    def get_diff_md5_rows_chunk(
        self,
        source_md5_rows_chunk: pd.DataFrame,
        target_md5_rows_chunk: pd.DataFrame,
        source_index_column_collection: list[str],
        target_index_column_collection: list[str],
    ) -> pd.DataFrame:
        """Get the differences in MD5 for a specific chunk row.

        Args:
            source_md5_rows_chunk (pd.DataFrame): The source DataFrame
            containing MD5 for a specific chunk row.
            target_md5_rows_chunk (pd.DataFrame): The target DataFrame
            containing MD5 for a specific chunk row.
            source_index_column_collection (list[str]): A list of index columns for the source DataFrame.
            target_index_column_collection (list[str]): A list of index columns for the target DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the differences in MD5 for the specified chunk row.

        """
        source_merge_target = pd.merge(
            source_md5_rows_chunk,
            target_md5_rows_chunk,
            left_on=source_index_column_collection,
            right_on=target_index_column_collection,
            how="outer",
            suffixes=(SOURCE_SUFFIX, TARGET_SUFFIX),
            indicator=True,
        )

        not_found_df = source_merge_target[
            source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] != "both"
        ]
        not_found_df_copy = not_found_df.copy()
        not_found_df_copy[RESULT_COLUMN_KEY] = Result.NOT_FOUND.value

        failed_df = source_merge_target[
            (source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] == "both")
            & (
                source_merge_target[ROW_MD5_KEY + SOURCE_SUFFIX]
                != source_merge_target[ROW_MD5_KEY + TARGET_SUFFIX]
            )
        ]
        failed_df_copy = failed_df.copy()
        failed_df_copy[RESULT_COLUMN_KEY] = Result.FAILURE.value

        columns = source_index_column_collection + [RESULT_COLUMN_KEY]
        diff_df = pd.concat([not_found_df_copy, failed_df_copy], ignore_index=True)[
            columns
        ]
        diff_df_ordered = diff_df.sort_values(by=source_index_column_collection)
        return diff_df_ordered

    def generate_row_validation_report(
        self,
        compared_df: pd.DataFrame,
        fully_qualified_name: str,
        target_fully_qualified_name: str,
        source_index_column_collection: list[str],
        target_index_column_collection: list[str],
        context: Context,
    ) -> None:
        """Store a report for MD5 rows chunk validation.

        Args:
            compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
            fully_qualified_name (str): The fully qualified name of the table being validated.
            target_fully_qualified_name (str): The fully qualified name of the target table being validated.
            source_index_column_collection (list[str]): A list of index columns for the source DataFrame.
            target_index_column_collection (list[str]): A list of index columns for the target DataFrame
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        result_columns = (
            [ROW_NUMBER_COLUMN_KEY, TABLE_NAME_COLUMN_KEY]
            + source_index_column_collection
            + [
                RESULT_COLUMN_KEY,
                SOURCE_QUERY_COLUMN_KEY,
                TARGET_QUERY_COLUMN_KEY,
            ]
        )

        result_df = pd.DataFrame(data=[], columns=result_columns)
        for _, row in compared_df.iterrows():
            values = []
            row_number = context.get_row_number()
            values.append(row_number)
            values.append(fully_qualified_name)

            for index_column in source_index_column_collection:
                values.append(row[index_column])

            values.append(row[RESULT_COLUMN_KEY])

            source_query = self._generate_select_all_columns_query(
                fully_qualified_name=fully_qualified_name,
                index_column_collection=source_index_column_collection,
                df_row=row,
            )

            values.append(source_query)

            target_query = self._generate_select_all_columns_query(
                fully_qualified_name=target_fully_qualified_name,
                index_column_collection=target_index_column_collection,
                df_row=row,
            )

            values.append(target_query)

            result_df.loc[len(result_df)] = values

        report_name = ROW_VALIDATION_REPORT_NAME.format(
            fully_qualified_name=fully_qualified_name
        )

        report_file = os.path.join(
            context.report_path, f"{context.run_start_time}_{report_name}"
        )

        result_df.to_csv(report_file, index=False)

    def generate_row_validation_queries(
        self,
        compared_df: pd.DataFrame,
        fully_qualified_name: str,
        target_fully_qualified_name: str,
        source_index_column_collection: list[str],
        target_index_column_collection: list[str],
        context: Context,
    ) -> None:
        """Generate SQL queries to validate MD5 checksums for a given DataFrame.

        This function constructs SQL queries to validate the MD5 checksums of the source and target DataFrames
        based on the provided compared DataFrame and index columns.

        Args:
            compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
            fully_qualified_name (str): The fully qualified name of the source table being validated.
            target_fully_qualified_name (str): The fully qualified name of the target table being validated.
            source_index_column_collection (list[str]): A list of index columns used
            for comparison in the source DataFrame.
            target_index_column_collection (list[str]): A list of index columns used
            for comparison in the target DataFrame.
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        source_clause_collection = []
        target_clause_collection = []
        for _, row in compared_df.iterrows():
            source_clause = self._generate_where_clause(
                index_column_collection=source_index_column_collection, df_row=row
            )
            source_clause_newline = source_clause + NEWLINE
            source_clause_collection.append(source_clause_newline)

            target_clause = self._generate_where_clause(
                index_column_collection=target_index_column_collection, df_row=row
            )
            target_clause_newline = target_clause + NEWLINE
            target_clause_collection.append(target_clause_newline)

        self._generate_row_validation_query(
            clause_collection=source_clause_collection,
            fully_qualified_name=fully_qualified_name,
            platform=context.source_platform,
            report_path=context.report_path,
            run_start_time=context.run_start_time,
        )

        self._generate_row_validation_query(
            clause_collection=target_clause_collection,
            fully_qualified_name=target_fully_qualified_name,
            platform=context.target_platform,
            report_path=context.report_path,
            run_start_time=context.run_start_time,
        )

    def _generate_row_validation_query(
        self,
        clause_collection: list[str],
        fully_qualified_name: str,
        platform: Platform,
        report_path: str,
        run_start_time: str,
    ) -> None:

        joined_clause = " OR ".join(clause_collection)

        query = MD5_REPORT_QUERY_TEMPLATE.format(
            fully_qualified_name=fully_qualified_name, clause=joined_clause
        )

        report_name = ROW_VALIDATION_DIFF_QUERY_NAME.format(
            platform=platform,
            fully_qualified_name=fully_qualified_name,
        )

        report_file_path = os.path.join(
            report_path,
            f"{run_start_time}_{report_name}",
        )

        self._write_to_file(
            file_path=report_file_path,
            content=query,
        )

    def _generate_select_all_columns_query(
        self,
        fully_qualified_name: str,
        index_column_collection: list[str],
        df_row: pd.Series,
    ) -> str:
        where_clause = self._generate_where_clause(
            index_column_collection=index_column_collection, df_row=df_row
        )

        query = MD5_REPORT_QUERY_TEMPLATE.format(
            fully_qualified_name=fully_qualified_name, clause=where_clause
        )

        return query

    def _generate_where_clause(
        self, index_column_collection: list[str], df_row: pd.Series
    ) -> str:
        clause = [
            self._generate_clause(column_name=index_column, value=df_row[index_column])
            for index_column in index_column_collection
        ]

        joined_clause = " AND ".join(clause)

        return joined_clause

    def _generate_clause(
        self, column_name: str, value: any, operator: str = "="
    ) -> str:
        if self.is_numeric(value):
            return f""""{column_name}" {operator} {value}"""
        else:
            return f""""{column_name}" {operator} '{value}'"""

    def _write_to_file(self, file_path: str, content: str) -> None:
        """Write content to a file with UTF-8 encoding.

        Creates the directory if it doesn't exist.

        Args:
            file_path (str): The full path to the file including directory and filename.
            content (str): The content to write to the file.

        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
