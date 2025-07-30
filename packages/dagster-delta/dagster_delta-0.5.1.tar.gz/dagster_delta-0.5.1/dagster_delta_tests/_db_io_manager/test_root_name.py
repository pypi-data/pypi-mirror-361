import os

import pyarrow as pa
from dagster import (
    asset,
    materialize,
)
from deltalake import DeltaTable

from dagster_delta import DeltaLakePyarrowIOManager


@asset(
    key_prefix=["my_schema"],
    metadata={"root_name": "custom_asset"},
)
def asset_1() -> pa.Table:
    return pa.Table.from_pydict(
        {
            "value": [1],
            "b": [1],
        },
    )


def test_asset_with_root_name(
    tmp_path,
    io_manager: DeltaLakePyarrowIOManager,
):
    resource_defs = {"io_manager": io_manager}

    res = materialize([asset_1], resources=resource_defs)
    assert res.success

    data = res.asset_value(asset_1.key)

    dt = DeltaTable(os.path.join(str(tmp_path), "my_schema", "custom_asset"))

    assert data == dt.to_pyarrow_table()
