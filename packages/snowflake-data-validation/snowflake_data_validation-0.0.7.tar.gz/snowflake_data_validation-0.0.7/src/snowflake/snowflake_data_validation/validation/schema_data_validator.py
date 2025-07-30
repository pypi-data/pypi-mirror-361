import logging

import pandas as pd

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    COLUMN_VALIDATED_KEY,
    COMMENTS_KEY,
    EVALUATION_CRITERIA_KEY,
    NOT_APPLICABLE_CRITERIA_VALUE,
    NOT_EXIST_TARGET,
    SNOWFLAKE_VALUE_KEY,
    SOURCE_VALUE_KEY,
    STATUS_KEY,
    TABLE_KEY,
    VALIDATION_TYPE_KEY,
    Result,
    ValidationLevel,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.validation.data_validator_base import (
    DataValidatorBase,
)
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    ValidationReportBuffer,
)


LOGGER = logging.getLogger(__name__)


class SchemaDataValidator(DataValidatorBase):
    @log
    def validate_table_metadata(
        self,
        object_name: str,
        target_df: pd.DataFrame,
        source_df: pd.DataFrame,
        context: Context,
    ) -> bool:
        """Validate the metadata of two tables by normalizing and comparing their dataframes.

        Args:
            object_name (str): The name of the object (e.g., table) being validated.
            target_df (pd.DataFrame): The dataframe representing the target table's metadata.
            source_df (pd.DataFrame): The dataframe representing the source table's metadata.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            bool: True if the normalized dataframes are equal, False otherwise.

        """
        LOGGER.info("Starting table metadata validation for: %s", object_name)
        context.output_handler.handle_message(
            message=f"Running Schema Validation for {object_name}",
            level=OutputMessageLevel.INFO,
        )

        LOGGER.debug("Normalizing target and source DataFrames")
        normalized_target = self.normalize_dataframe(target_df)
        normalized_source = self.normalize_dataframe(source_df)

        differences_data = pd.DataFrame(
            columns=[
                VALIDATION_TYPE_KEY,
                TABLE_KEY,
                COLUMN_VALIDATED_KEY,
                EVALUATION_CRITERIA_KEY,
                SOURCE_VALUE_KEY,
                SNOWFLAKE_VALUE_KEY,
                STATUS_KEY,
                COMMENTS_KEY,
            ]
        )

        target_validated_set = set(normalized_target[COLUMN_VALIDATED].values)

        for _, source_row in normalized_source.iterrows():
            source_validated_value = source_row[COLUMN_VALIDATED]

            # Handle missing columns in target
            if source_validated_value not in target_validated_set:
                LOGGER.debug(
                    "Column %s not found in target table", source_validated_value
                )
                new_row = self.create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=NOT_EXIST_TARGET,
                    status=Result.FAILURE.value,
                    comments="The column does not exist in the target table.",
                )
                differences_data = self.add_validation_row_to_data(
                    differences_data, new_row
                )
                continue

            # Validate existing columns
            target_row = normalized_target[
                normalized_target[COLUMN_VALIDATED] == source_validated_value
            ]
            column_has_differences = False

            for column in normalized_source.columns:
                # Skip irrelevant columns
                if column in {COLUMN_VALIDATED, TABLE_KEY}:
                    continue

                source_value = source_row[column]
                target_value = target_row[column].values[0]

                validation_row, field_success = self.validate_column_field(
                    column,
                    source_value,
                    target_value,
                    context,
                    object_name,
                    source_validated_value,
                )

                if not validation_row.empty:
                    differences_data = self.add_validation_row_to_data(
                        differences_data, validation_row
                    )

                if not field_success:
                    column_has_differences = True

            # Record overall column success if no field differences found
            if not column_has_differences:
                success_row = self.create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=source_validated_value,
                    status=Result.SUCCESS.value,
                    comments="Column exists in target table and all metadata matches.",
                )
                differences_data = self.add_validation_row_to_data(
                    differences_data, success_row
                )

        # Filter out rows where both SOURCE and TARGET are NOT_APPLICABLE_CRITERIA_VALUE
        # These represent validation criteria that don't apply to certain data types
        differences_data = differences_data[
            ~(
                (differences_data[SOURCE_VALUE_KEY] == NOT_APPLICABLE_CRITERIA_VALUE)
                & (
                    differences_data[SNOWFLAKE_VALUE_KEY]
                    == NOT_APPLICABLE_CRITERIA_VALUE
                )
            )
        ]

        # Determine if there are actual failures (excluding WARNING status)
        failure_rows = differences_data[
            differences_data[STATUS_KEY] == Result.FAILURE.value
        ]
        has_failures = len(failure_rows) > 0

        buffer = ValidationReportBuffer()
        buffer.add_data(differences_data)
        LOGGER.debug(
            "Added schema validation data for %s to buffer (queue size: %d)",
            object_name,
            buffer.get_queue_size(),
        )

        display_data = differences_data.drop(
            columns=[VALIDATION_TYPE_KEY, TABLE_KEY], errors="ignore"
        )

        context.output_handler.handle_message(
            header="Schema validation results:",
            dataframe=display_data,
            level=(
                OutputMessageLevel.WARNING if has_failures else OutputMessageLevel.INFO
            ),
        )

        return not has_failures
