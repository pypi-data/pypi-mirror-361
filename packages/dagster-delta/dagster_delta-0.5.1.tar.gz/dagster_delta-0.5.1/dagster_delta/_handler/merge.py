import logging
from typing import Any, Optional, TypeVar, Union

from arro3.core.types import ArrowArrayExportable, ArrowStreamExportable
from deltalake import CommitProperties, DeltaTable, WriterProperties
from deltalake.table import FilterLiteralType, TableMerger

from dagster_delta._handler.utils import create_predicate
from dagster_delta.config import MergeConfig, MergeOperationsConfig, MergeType

T = TypeVar("T")


def merge_execute(
    dt: DeltaTable,
    data: Union[ArrowStreamExportable, ArrowArrayExportable],
    merge_config: MergeConfig,
    writer_properties: Optional[WriterProperties],
    commit_properties: Optional[CommitProperties],
    merge_predicate_from_metadata: Optional[str],
    merge_operations_config: Optional[MergeOperationsConfig],
    partition_filters: Optional[list[FilterLiteralType]] = None,
) -> dict[str, Any]:
    merge_type = merge_config.merge_type
    error_on_type_mismatch = merge_config.error_on_type_mismatch

    if merge_predicate_from_metadata is not None:
        predicate = merge_predicate_from_metadata
    elif merge_config.predicate is not None:
        predicate = merge_config.predicate
    else:
        raise Exception("merge predicate was not provided")

    target_alias = merge_config.target_alias

    if partition_filters is not None:
        partition_predicate = create_predicate(partition_filters, target_alias=target_alias)

        predicate = f"{predicate} AND {partition_predicate}"
        logger = logging.getLogger()
        logger.setLevel("DEBUG")
        logger.debug("Using explicit MERGE partition predicate: \n%s", predicate)

    merger = dt.merge(
        source=data,
        predicate=predicate,
        source_alias=merge_config.source_alias,
        target_alias=target_alias,
        error_on_type_mismatch=error_on_type_mismatch,
        writer_properties=writer_properties,
        commit_properties=commit_properties,
    )

    if merge_type == MergeType.update_only:
        return merger.when_matched_update_all().execute()
    elif merge_type == MergeType.deduplicate_insert:
        return merger.when_not_matched_insert_all().execute()
    elif merge_type == MergeType.upsert:
        return merger.when_matched_update_all().when_not_matched_insert_all().execute()
    elif merge_type == MergeType.replace_delete_unmatched:
        return merger.when_matched_update_all().when_not_matched_by_source_delete().execute()
    elif merge_type == MergeType.custom:
        if merge_operations_config is not None:
            operations_config = merge_operations_config
        elif merge_config.merge_operations_config is not None:
            operations_config = merge_config.merge_operations_config
        else:
            raise Exception("merge operations config was not provided")
        operations_config = MergeOperationsConfig.model_validate(operations_config)
        return apply_merge_operations(merger, operations_config).execute()
    else:
        raise NotImplementedError


def apply_merge_operations(
    merger: TableMerger,
    operations_config: MergeOperationsConfig,
) -> TableMerger:
    if operations_config.when_not_matched_insert is not None:
        for match in operations_config.when_not_matched_insert:
            merger = merger.when_not_matched_insert(
                predicate=match.predicate,
                updates=match.updates,
            )
    if operations_config.when_not_matched_insert_all is not None:
        for match in operations_config.when_not_matched_insert_all:
            merger = merger.when_not_matched_insert_all(
                predicate=match.predicate,
                except_cols=match.except_cols,
            )
    if operations_config.when_matched_update is not None:
        for match in operations_config.when_matched_update:
            merger = merger.when_matched_update(
                predicate=match.predicate,
                updates=match.updates,
            )

    if operations_config.when_matched_update_all is not None:
        for match in operations_config.when_matched_update_all:
            merger = merger.when_matched_update_all(
                predicate=match.predicate,
                except_cols=match.except_cols,
            )

    if operations_config.when_matched_delete is not None:
        for match in operations_config.when_matched_delete:
            merger = merger.when_matched_delete(
                predicate=match.predicate,
            )

    if operations_config.when_not_matched_by_source_delete is not None:
        for match in operations_config.when_not_matched_by_source_delete:
            merger = merger.when_not_matched_by_source_delete(
                predicate=match.predicate,
            )

    if operations_config.when_not_matched_by_source_update is not None:
        for match in operations_config.when_not_matched_by_source_update:
            merger = merger.when_not_matched_by_source_update(
                updates=match.updates,
                predicate=match.predicate,
            )

    return merger
