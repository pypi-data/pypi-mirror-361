import os

import pyarrow as pa
import pytest
from dagster import (
    OpExecutionContext,
    Out,
    graph,
    op,
)
from deltalake import DeltaTable

from dagster_delta import (
    DeltaLakePyarrowIOManager,
    LocalConfig,
    MergeConfig,
    MergeOperationsConfig,
    MergeType,
    WriteMode,
)
from dagster_delta.config import WhenMatchedUpdateAll, WhenNotMatchedInsertAll


@op(out=Out(metadata={"schema": "a_df2"}))
def a_df2(context: OpExecutionContext) -> pa.Table:
    context.add_output_metadata(
        {
            "merge_predicate": "s.a = t.a",
            "merge_operations_config": MergeOperationsConfig(
                when_not_matched_insert_all=[WhenNotMatchedInsertAll()],
                when_matched_update_all=[WhenMatchedUpdateAll()],
            ).model_dump(),
        },
    )

    return pa.Table.from_pydict({"a": [1, 2, 3], "b": [4, 5, 6]})


@op(out=Out(metadata={"schema": "add_one2"}))
def add_one2(context: OpExecutionContext, df: pa.RecordBatchReader):  # noqa: ANN201
    context.add_output_metadata(
        {
            "merge_predicate": "s.a = t.a",
            "merge_operations_config": MergeOperationsConfig(
                when_not_matched_insert_all=[WhenNotMatchedInsertAll()],
                when_matched_update_all=[WhenMatchedUpdateAll()],
            ).model_dump(),
        },
    )

    return df.read_all().set_column(0, "a", pa.array([2, 3, 4]))


@graph
def add_one_to_dataframe_2():
    add_one2(a_df2())


@op(out=Out(metadata={"schema": "a_df"}))
def a_df() -> pa.Table:
    return pa.Table.from_pydict({"a": [1, 2, 3], "b": [4, 5, 6]})


@op(out=Out(metadata={"schema": "add_one"}))
def add_one(df: pa.Table):  # noqa: ANN201
    return df.set_column(0, "a", pa.array([2, 3, 4]))


@graph
def add_one_to_dataframe():
    add_one(a_df())


@pytest.mark.parametrize("merge_type", [MergeType.deduplicate_insert, MergeType.upsert])
def test_deltalake_io_manager_with_ops_rust_writer(tmp_path, merge_type: MergeType):
    resource_defs = {
        "io_manager": DeltaLakePyarrowIOManager(
            root_uri=str(tmp_path),
            storage_options=LocalConfig(),
            mode=WriteMode.merge,
            merge_config=MergeConfig(
                merge_type=merge_type,
                predicate="s.a = t.a",
                source_alias="s",
                target_alias="t",
            ),
        ),
    }

    job = add_one_to_dataframe.to_job(resource_defs=resource_defs)

    # run the job twice to ensure that tables get properly deleted
    for _ in range(2):
        res = job.execute_in_process()

        assert res.success

        dt = DeltaTable(os.path.join(tmp_path, "a_df/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [1, 2, 3]

        dt = DeltaTable(os.path.join(tmp_path, "add_one/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [2, 3, 4]


def test_deltalake_io_manager_custom_merge(tmp_path):
    resource_defs = {
        "io_manager": DeltaLakePyarrowIOManager(
            root_uri=str(tmp_path),
            storage_options=LocalConfig(),
            mode=WriteMode.merge,
            merge_config=MergeConfig(
                merge_type=MergeType.custom,
                predicate="s.a = t.a",
                source_alias="s",
                target_alias="t",
                merge_operations_config=MergeOperationsConfig(
                    when_not_matched_insert_all=[WhenNotMatchedInsertAll()],
                    when_matched_update_all=[WhenMatchedUpdateAll()],
                ),
            ),
        ),
    }

    job = add_one_to_dataframe.to_job(resource_defs=resource_defs)

    # run the job twice to ensure that tables get properly deleted
    for _ in range(2):
        res = job.execute_in_process()

        assert res.success

        dt = DeltaTable(os.path.join(tmp_path, "a_df/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [1, 2, 3]

        dt = DeltaTable(os.path.join(tmp_path, "add_one/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [2, 3, 4]


def test_deltalake_io_manager_runtime_metadata_merge_configuration(tmp_path):
    """Whether runtime metadata 'merge_predicate' and 'merge_operations_config' gets picked up."""
    resource_defs = {
        "io_manager": DeltaLakePyarrowIOManager(
            root_uri=str(tmp_path),
            storage_options=LocalConfig(),
            mode=WriteMode.merge,
            merge_config=MergeConfig(
                merge_type=MergeType.custom,
                source_alias="s",
                target_alias="t",
            ),
        ),
    }

    job = add_one_to_dataframe_2.to_job(resource_defs=resource_defs)

    # run the job twice to ensure that tables get properly deleted
    for _ in range(2):
        res = job.execute_in_process()

        assert res.success

        dt = DeltaTable(os.path.join(tmp_path, "a_df2/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [1, 2, 3]

        dt = DeltaTable(os.path.join(tmp_path, "add_one2/result"))
        out_df = dt.to_pyarrow_table()
        assert sorted(out_df["a"].to_pylist()) == [2, 3, 4]
