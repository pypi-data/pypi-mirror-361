import logging
import re

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPE,
    COLUMN_VALIDATED_KEY,
    COMMENTS_KEY,
    EVALUATION_CRITERIA_KEY,
    NOT_APPLICABLE_CRITERIA_VALUE,
    SNOWFLAKE_VALUE_KEY,
    SOURCE_VALUE_KEY,
    STATUS_KEY,
    TABLE_KEY,
    VALIDATION_TYPE_KEY,
    Result,
    ValidationLevel,
)
from snowflake.snowflake_data_validation.utils.context import Context


LOGGER = logging.getLogger(__name__)
IS_NUMERIC_REGEX = r"^-?\d+(\.\d+)?$"


class DataValidatorBase:

    """Abstract base class for data validators."""

    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize the DataFrame by standardizing column names and types.

        Args:
            df (pd.DataFrame): The DataFrame to normalize.

        Returns:
            pd.DataFrame: A normalized DataFrame with uppercase column names, NaN values filled with
                        NOT_APPLICABLE_CRITERIA_VALUE, and rows sorted by all columns.

        """
        df.columns = [
            col.upper() for col in df.columns
        ]  # WIP in the future we should generate the columns names from a column mapping if provided
        df_copy = df.fillna(NOT_APPLICABLE_CRITERIA_VALUE, inplace=False)
        return df_copy.sort_values(by=list(df_copy.columns)).reset_index(drop=True)

    def create_validation_row(
        self,
        validation_type: str,
        table_name: str,
        column_validated: str,
        evaluation_criteria: str,
        source_value: any,
        snowflake_value: any,
        status: str,
        comments: str,
    ) -> pd.DataFrame:
        """Create a standardized validation result row.

        Args:
            validation_type (str): The type of validation being performed.
            table_name (str): The name of the table being validated.
            column_validated (str): The column being validated.
            evaluation_criteria (str): The criteria used for evaluation.
            source_value (any): The value from the source.
            snowflake_value (any): The value from Snowflake.
            status (str): The validation status (SUCCESS/FAILURE).
            comments (str): Additional comments about the validation.

        Returns:
            pd.DataFrame: A single-row DataFrame with the validation result.

        """
        return pd.DataFrame(
            {
                VALIDATION_TYPE_KEY: [validation_type],
                TABLE_KEY: [table_name],
                COLUMN_VALIDATED_KEY: [column_validated],
                EVALUATION_CRITERIA_KEY: [evaluation_criteria],
                SOURCE_VALUE_KEY: [source_value],
                SNOWFLAKE_VALUE_KEY: [snowflake_value],
                STATUS_KEY: [status],
                COMMENTS_KEY: [comments],
            }
        )

    def add_validation_row_to_data(
        self, differences_data: pd.DataFrame, validation_row: pd.DataFrame
    ) -> pd.DataFrame:
        """Add a validation row to the differences data."""
        return pd.concat([differences_data, validation_row], ignore_index=True)

    def validate_column_field(
        self,
        column: str,
        source_value: any,
        target_value: any,
        context: Context,
        object_name: str,
        source_validated_value: str,
    ) -> tuple[pd.DataFrame, bool]:
        """Validate a single column field and return validation row and success status.

        Args:
            column (str): The column being validated.
            source_value (any): The value from the source.
            target_value (any): The value from the target.
            context (Context): The context.
            object_name (str): The name of the object being validated.
            source_validated_value (str): The validated value from the source.

        Returns:
            tuple: (validation_row_df, is_success)

        """
        # Skip if both values are NaN or identical
        if pd.isna(source_value) and pd.isna(target_value):
            return pd.DataFrame(), True  # No validation row needed, but success

        if source_value == target_value:
            return (
                self.create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status=Result.SUCCESS.value,
                    comments=f"Values match: source({source_value}), Snowflake({target_value})",
                ),
                True,
            )

        # Handle datatype validation with special logic
        if column == COLUMN_DATATYPE:
            return self.validate_datatype_field(
                source_value,
                target_value,
                context,
                object_name,
                source_validated_value,
                column,
            )

        # Handle specific precision/scale/length criteria with WARNING status
        warning_criteria = {
            "NUMERIC_PRECISION",
            "NUMERIC_SCALE",
            "CHARACTER_MAXIMUM_LENGTH",
        }
        if column in warning_criteria:

            if self.is_numeric(source_value) and self.is_numeric(target_value):
                if float(source_value) < float(target_value):
                    return (
                        self.create_validation_row(
                            validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                            table_name=object_name,
                            column_validated=source_validated_value,
                            evaluation_criteria=column,
                            source_value=source_value,
                            snowflake_value=target_value,
                            status=Result.WARNING.value,
                            comments=f"Source value ({source_value}) is lower than target value ({target_value})",
                        ),
                        True,  # Consider WARNING as success
                    )

        # Handle FAILURE status
        LOGGER.debug(
            "Value mismatch for column %s in %s: source=%s, target=%s",
            source_validated_value,
            column,
            source_value,
            target_value,
        )
        return (
            self.create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=column,
                source_value=source_value,
                snowflake_value=target_value,
                status=Result.FAILURE.value,
                comments=f"Values differ: source({source_value}), Snowflake({target_value})",
            ),
            False,
        )

    def validate_datatype_field(
        self,
        source_value: str,
        target_value: str,
        context: Context,
        object_name: str,
        source_validated_value: str,
        column: str,
    ) -> tuple[pd.DataFrame, bool]:
        """Validate datatype field with mapping logic.

        Args:
            source_value (str): The datatype from the source.
            target_value (str): The datatype from the target.
            context (Context): The context.
            object_name (str): The name of the object being validated.
            source_validated_value (str): The validated value from the source.
            column (str): The column being validated.

        Returns:
            tuple: (validation_row_df, is_success)

        """
        if context.datatypes_mappings:
            mapped_value = context.datatypes_mappings.get(source_value.upper(), None)
            if mapped_value and self.normalize_datatype(
                target_value
            ) == self.normalize_datatype(mapped_value):
                success_message = (
                    f"Values match: source({source_value}) "
                    f"has a mapping to Snowflake({target_value})"
                )
                return (
                    self.create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status=Result.SUCCESS.value,
                        comments=success_message,
                    ),
                    True,
                )
            else:
                comment = (
                    f"No mapping found for datatype '{source_value}': "
                    f"source({source_value}), Snowflake({target_value})"
                    if not mapped_value
                    else f"Values differ: source({source_value}), Snowflake({target_value})"
                )
                LOGGER.debug(
                    "Datatype mismatch for column %s: source=%s, target=%s",
                    source_validated_value,
                    source_value,
                    target_value,
                )
                return (
                    self.create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status=Result.FAILURE.value,
                        comments=comment,
                    ),
                    False,
                )
        else:
            # No mappings available - direct comparison
            if source_value.upper() == target_value.upper():
                return (
                    self.create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status=Result.SUCCESS.value,
                        comments=f"Values match: source({source_value}), Snowflake({target_value})",
                    ),
                    True,
                )
            else:
                LOGGER.debug(
                    "Datatype mismatch for column %s: source=%s, target=%s",
                    source_validated_value,
                    source_value,
                    target_value,
                )
                return (
                    self.create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status=Result.FAILURE.value,
                        comments=f"Values differ: source({source_value}), Snowflake({target_value})",
                    ),
                    False,
                )

    def is_numeric(self, value: any) -> bool:
        """Determine if the given value is numeric.

        A value is considered numeric if it is an instance of int or float,
        or if it matches the numeric pattern (including integers and decimals).
        As a safety net, if the regex check passes, we also verify that the
        value can actually be converted to float.

        Args:
            value: The value to check. Can be of any type.

        Returns:
            bool: True if the value is numeric, False otherwise.

        """
        if isinstance(value, (int, float)):
            return True

        if bool(re.match(IS_NUMERIC_REGEX, str(value))):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False

        return False

    def normalize_datatype(self, datatype: str) -> str:
        """Normalize data types to handle equivalent types.

        This is a temporary fix for the issue where Snowflake displays "TEXT" instead of "VARCHAR".
        TODO: Remove this once the issue is fixed.

        Args:
            datatype (str): The data type to normalize.

        Returns:
            str: The normalized data type.

        """
        # Treat VARCHAR and TEXT as equivalent
        if datatype.upper() in {"VARCHAR", "TEXT"}:
            return "VARCHAR"
        return datatype.upper()
