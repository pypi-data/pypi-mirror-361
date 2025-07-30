from dagster_delta.config import (
    AzureConfig,
    BackoffConfig,
    ClientConfig,
    GcsConfig,
    LocalConfig,
    MergeConfig,
    MergeOperationsConfig,
    MergeType,
    S3Config,
    WhenMatchedDelete,
    WhenMatchedUpdate,
    WhenMatchedUpdateAll,
    WhenNotMatchedBySourceDelete,
    WhenNotMatchedBySourceUpdate,
    WhenNotMatchedInsert,
    WhenNotMatchedInsertAll,
)
from dagster_delta.io_manager.arrow import DeltaLakePyarrowIOManager
from dagster_delta.io_manager.base import (
    BaseDeltaLakeIOManager,
    SchemaMode,
    WriteMode,
)
from dagster_delta.resources import DeltaTableResource

__all__ = [
    "AzureConfig",
    "ClientConfig",
    "GcsConfig",
    "S3Config",
    "LocalConfig",
    "BackoffConfig",
    "MergeConfig",
    "MergeType",
    "WriteMode",
    "SchemaMode",
    "DeltaTableResource",
    "BaseDeltaLakeIOManager",
    "DeltaLakePyarrowIOManager",
    "WhenMatchedDelete",
    "WhenMatchedUpdate",
    "WhenMatchedUpdateAll",
    "WhenNotMatchedBySourceDelete",
    "WhenNotMatchedBySourceUpdate",
    "WhenNotMatchedInsert",
    "WhenNotMatchedInsertAll",
    "MergeOperationsConfig",
]


try:
    from dagster_delta.io_manager.polars import DeltaLakePolarsIOManager  # noqa

    __all__.extend(["DeltaLakePolarsIOManager"])

except ImportError as e:
    if "polars" in str(e):
        pass
    else:
        raise e
