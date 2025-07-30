# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from typing import Union

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import NEWLINE, Platform
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class QueryGeneratorBase(ABC):

    """Abstract base class for query generation.

    This class defines the interface for generating database queries that are
    used by both MetadataExtractorBase and ScriptWriterBase implementations.
    """

    def __init__(self, platform: Platform):
        """Initialize the query generator with a platform.

        Args:
            platform (Platform): The platform enum value.

        """
        self.platform = platform

    def generate_schema_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract metadata for a specific table.

        This template method provides the common workflow for generating schema queries.
        Platform-specific implementations can override hook methods for customization.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract metadata for the specified table.

        """
        # Use the transformed name for query generation
        query = table_context.sql_generator.generate_table_metadata_sql(
            platform=self.platform.value,
            table_name=table_context.table_name,
            schema_name=table_context.schema_name,
            fully_qualified_name=table_context.fully_qualified_name,
            where_clause=table_context.where_clause,
            has_where_clause=table_context.has_where_clause,
            column_selection_list=table_context.columns_to_validate,
        )

        return query

    def generate_metrics_query(
        self,
        table_context: TableContext,
    ) -> str:
        """Generate the SQL query to extract metadata for specific columns in a table.

        This template method provides the common workflow for generating CTE-based metrics queries.
        Platform-specific implementations must implement the abstract CTE generation methods.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract column metadata for the specified columns.

        """
        cte_queries = []
        cte_names = []
        metrics = []

        for col in table_context.columns_to_validate:
            col_type = col.data_type

            # Apply Snowflake-specific TEXT -> VARCHAR transformation
            if self.platform == Platform.SNOWFLAKE and col_type == "TEXT":
                col_type = "VARCHAR"

            cte_query, cte_name, metric_list = self.cte_query_generator(
                metrics_templates=table_context.templates_loader_manager.metrics_templates,
                col_name=col.name,
                col_type=col_type,
                fully_qualified_name=table_context.fully_qualified_name,
                where_clause=table_context.where_clause,
                has_where_clause=table_context.has_where_clause,
                sql_generator=table_context.sql_generator,
            )
            if cte_query is None:
                continue
            cte_queries.append(cte_query)
            cte_names.append(cte_name)
            metrics.append(metric_list)

        if not cte_queries:
            error_message = (
                f"Metrics templates are missing for the column data types in "
                f"{table_context.fully_qualified_name}."
            )
            raise Exception(error_message)

        outer_query = self.outer_query_generator(cte_names, metrics)
        final_query = "WITH " + ", ".join(cte_queries) + NEWLINE + outer_query
        return final_query

    @abstractmethod
    def generate_compute_md5_query(
        self, table_context: TableContext, other_table_name: str
    ) -> Union[str, list[str]]:
        """Generate the SQL query to compute MD5 for a table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            other_table_name (str): The name of the table to compute MD5 for.

        Returns:
            Union[str, list[str]]: SQL query string or a list of SQL query strings to extract MD5 checksum information.

        """
        pass

    def generate_table_column_metadata_query(
        self, table_configuration: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract column information metadata for a given table.

        This template method provides the common workflow for generating table column metadata queries.

        Args:
            table_configuration (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract column information metadata.

        """
        query = context.sql_generator.extract_table_column_metadata(
            database_name=table_configuration.source_database,
            schema_name=table_configuration.source_schema,
            table_name=table_configuration.source_table,
            platform=self.platform.value,
        )

        return query

    @abstractmethod
    def generate_statement_table_chunks_md5(self, table_context: TableContext) -> str:
        """Generate the DDL statement to create a table for storing MD5 checksums of data chunks.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to create a table for storing MD5 checksums of data chunks.

        """
        pass

    @abstractmethod
    def generate_extract_chunks_md5_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract MD5 for all chunks of a table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract MD5 for all chunks of a table.

        """
        pass

    @abstractmethod
    def generate_extract_md5_rows_chunk_query(
        self, chunk_id: str, table_context: TableContext
    ) -> str:
        """Generate the SQL query to extract the MD5 rows for a specific chunk of a table.

        Args:
            chunk_id (str): The unique identifier for the chunk.
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract the MD5 rows for the specified chunk.

        """
        pass

    @abstractmethod
    def cte_query_generator(
        self,
        metrics_templates,
        col_name: str,
        col_type: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        sql_generator,
    ) -> Union[tuple[str, str, list[str]], tuple[None, None, None]]:
        """Generate a CTE query for a specific column.

        This method delegates to the platform-specific CTE generator.

        Args:
            metrics_templates: DataFrame containing metrics templates.
            col_name (str): Column name.
            col_type (str): Column data type.
            fully_qualified_name (str): Fully qualified table name.
            where_clause (str): WHERE clause.
            has_where_clause (bool): Whether WHERE clause is present.
            sql_generator: SQL template generator instance.

        Returns:
            Tuple containing CTE query, CTE name, and metrics list, or (None, None, None) if no query generated.

        """
        pass

    @abstractmethod
    def outer_query_generator(self, cte_names, metrics) -> str:
        """Generate an outer query combining CTEs.

        This method delegates to the platform-specific outer query generator.

        Args:
            cte_names: List of CTE names.
            metrics: List of metrics for each CTE.

        Returns:
            str: Generated outer query.

        """
        pass


