import os

import pyarrow as pa
from dagster import asset, materialize
from deltalake import write_deltalake

from dagster_delta import BackoffConfig, ClientConfig, DeltaTableResource, LocalConfig


def test_resource(tmp_path):
    data = pa.table(
        {
            "a": pa.array([1, 2, 3], type=pa.int32()),
            "b": pa.array([5, 6, 7], type=pa.int32()),
        },
    )

    @asset
    def create_table(delta_table: DeltaTableResource):
        write_deltalake(
            delta_table.url,
            data,
            storage_options=delta_table.storage_options.model_dump(),
        )

    @asset
    def read_table(delta_table: DeltaTableResource):
        res = delta_table.load().to_pyarrow_table()
        assert res.equals(data)

    materialize(
        [create_table, read_table],
        resources={
            "delta_table": DeltaTableResource(
                url=os.path.join(tmp_path, "table"),
                storage_options=LocalConfig(),
                client_options=ClientConfig(
                    max_retries=10,
                    retry_timeout="10s",
                    backoff_config=BackoffConfig(init_backoff="10s", base=1.2),
                ),
            ),
        },
    )


def test_resource_versioned(tmp_path):
    data = pa.table(
        {
            "a": pa.array([1, 2, 3], type=pa.int32()),
            "b": pa.array([5, 6, 7], type=pa.int32()),
        },
    )

    @asset
    def create_table(delta_table: DeltaTableResource):
        write_deltalake(
            delta_table.url,
            data,
            storage_options=delta_table.storage_options.model_dump(),
        )
        write_deltalake(
            delta_table.url,
            data,
            storage_options=delta_table.storage_options.model_dump(),
            mode="append",
        )

    @asset
    def read_table(delta_table: DeltaTableResource):
        res = delta_table.load().to_pyarrow_table()
        assert res.equals(data)

    materialize(
        [create_table, read_table],
        resources={
            "delta_table": DeltaTableResource(
                url=os.path.join(tmp_path, "table"),
                storage_options=LocalConfig(),
                client_options=ClientConfig(
                    max_retries=10,
                    retry_timeout="10s",
                    backoff_config=BackoffConfig(init_backoff="10s", base=1.2),
                ),
                version=0,
            ),
        },
    )
