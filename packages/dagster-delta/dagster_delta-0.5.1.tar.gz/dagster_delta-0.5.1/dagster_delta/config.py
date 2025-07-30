from enum import Enum
from typing import Literal, Optional

from dagster import Config


def _to_str_dict(dictionary: dict) -> dict[str, str]:
    """Filters dict of None values and casts other values to str."""
    return {key: str(value) for key, value in dictionary.items() if value is not None}


class LocalConfig(Config):
    """Storage configuration for local object store."""

    provider: Literal["local"] = "local"

    def str_dict(self) -> dict[str, str]:
        """Storage options as str dict."""
        return _to_str_dict(self.model_dump())


class AzureConfig(Config):
    """Storage configuration for Microsoft Azure Blob or ADLS Gen 2 object store."""

    provider: Literal["azure"] = "azure"

    account_name: Optional[str] = None
    """Storage account name"""

    client_id: Optional[str] = None
    """Client ID for ID / secret based authentication."""

    client_secret: Optional[str] = None
    """Client secret for ID / secret based authentication."""

    tenant_id: Optional[str] = None
    """Tenant ID for ID / secret based authentication."""

    federated_token_file: Optional[str] = None
    """File containing federated credential token"""

    account_key: Optional[str] = None
    """Storage account master key"""

    sas_key: Optional[str] = None
    """Shared access signature"""

    token: Optional[str] = None
    """Hard-coded bearer token"""

    use_azure_cli: Optional[bool] = None
    """Use azure cli for acquiring access token"""

    use_fabric_endpoint: Optional[bool] = None
    """Use object store with url scheme account.dfs.fabric.microsoft.com"""

    msi_resource_id: Optional[str] = None
    """Msi resource id for use with managed identity authentication."""

    msi_endpoint: Optional[str] = None
    """Endpoint to request a imds managed identity token."""

    container_name: Optional[str] = None
    """Storage container name"""

    def str_dict(self) -> dict[str, str]:
        """Storage options as str dict."""
        return _to_str_dict(self.model_dump())


class S3Config(Config):
    """Storage configuration for Amazon Web Services (AWS) S3 object store."""

    provider: Literal["s3"] = "s3"

    access_key_id: Optional[str] = None
    """AWS access key ID"""

    secret_access_key: Optional[str] = None
    """AWS access key secret"""

    region: Optional[str] = None
    """AWS region"""

    bucket: Optional[str] = None
    """Storage bucket name"""

    endpoint: Optional[str] = None
    """Sets custom endpoint for communicating with S3."""

    token: Optional[str] = None
    """Token to use for requests (passed to underlying provider)"""

    imdsv1_fallback: bool = False
    """Allow fall back to ImdsV1"""

    virtual_hosted_style_request: Optional[str] = None
    """Bucket is hosted under virtual-hosted-style URL"""

    unsigned_payload: Optional[bool] = None
    """Avoid computing payload checksum when calculating signature."""

    checksum: Optional[str] = None
    """Set the checksum algorithm for this client."""

    metadata_endpoint: Optional[str] = None
    """Instance metadata endpoint URL for fetching credentials"""

    container_credentials_relative_uri: Optional[str] = None
    """Set the container credentials relative URI

    https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html
    """

    def str_dict(self) -> dict[str, str]:
        """Storage options as str dict."""
        return _to_str_dict(self.model_dump())


class GcsConfig(Config):
    """Storage configuration for Google Cloud Storage object store."""

    provider: Literal["gcs"] = "gcs"

    service_account: Optional[str] = None
    """Path to the service account file"""

    service_account_key: Optional[str] = None
    """The serialized service account key."""

    bucket: Optional[str] = None
    """Bucket name"""

    application_credentials: Optional[str] = None
    """Application credentials path"""

    def str_dict(self) -> dict[str, str]:
        """Storage options as str dict."""
        return _to_str_dict(self.model_dump())


class BackoffConfig(Config):
    """Configuration for exponential back off https://docs.rs/object_store/latest/object_store/struct.BackoffConfig.html"""

    init_backoff: Optional[str] = None
    """The initial backoff duration"""

    max_backoff: Optional[str] = None
    """The maximum backoff duration"""

    base: Optional[float] = None
    """The multiplier to use for the next backoff duration"""


class ClientConfig(Config):
    """Configuration for http client interacting with storage APIs."""

    allow_http: Optional[bool] = None
    """Allow non-TLS, i.e. non-HTTPS connections"""

    allow_invalid_certificates: Optional[bool] = None
    """Skip certificate validation on https connections.

    ## Warning

    You should think very carefully before using this method.
    If invalid certificates are trusted, any certificate for any site will be trusted for use.
    This includes expired certificates. This introduces significant vulnerabilities,
    and should only be used as a last resort or for testing
    """

    connect_timeout: Optional[str] = None
    """Timeout for only the connect phase of a Client"""

    default_content_type: Optional[str] = None
    """default CONTENT_TYPE for uploads"""

    http1_only: Optional[bool] = None
    """Only use http1 connections"""

    http2_keep_alive_interval: Optional[int] = None
    """Interval for HTTP2 Ping frames should be sent to keep a connection alive."""

    http2_keep_alive_timeout: Optional[int] = None
    """Timeout for receiving an acknowledgement of the keep-alive ping."""

    http2_keep_alive_while_idle: Optional[int] = None
    """Enable HTTP2 keep alive pings for idle connections"""

    http2_only: Optional[bool] = None
    """Only use http2 connections"""

    pool_idle_timeout: Optional[str] = None
    """The pool max idle timeout

    This is the length of time an idle connection will be kept alive
    """

    pool_max_idle_per_host: Optional[int] = None
    """maximum number of idle connections per host"""

    proxy_url: Optional[str] = None
    """HTTP proxy to use for requests"""

    timeout: Optional[str] = None
    """Request timeout, e.g. 10s, 60s

    The timeout is applied from when the request starts connecting until the response body has finished
    """

    user_agent: Optional[str] = None
    """User-Agent header to be used by this client"""

    OBJECT_STORE_CONCURRENCY_LIMIT: Optional[str] = None
    """The number of concurrent connections the underlying object store can create"""

    MOUNT_ALLOW_UNSAFE_RENAME: Optional[str] = None
    """If set it will allow unsafe renames on mounted storage"""

    max_retries: Optional[int] = None
    """The maximum number of times to retry a request. Set to 0 to disable retries"""

    retry_timeout: Optional[str] = None
    """The maximum duration of time from the initial request after which no further retries will be attempted. e.g. 10s, 60s"""

    backoff_config: Optional[BackoffConfig] = None
    """Configuration for exponential back off """

    def str_dict(self) -> dict[str, str]:
        """Storage options as str dict."""
        model_dump = self.model_dump()
        str_dict: dict[str, str] = {}
        for key, value in model_dump.items():
            if value is not None:
                if isinstance(value, BackoffConfig):
                    ## delta-rs uses custom config keys for the BackOffConfig
                    ## https://delta-io.github.io/delta-rs/integrations/object-storage/special_configuration/
                    if value.base is not None:
                        str_dict["backoff_config.base"] = str(value.base)
                    if value.max_backoff is not None:
                        str_dict["backoff_config.max_backoff"] = str(value.max_backoff)
                    if value.init_backoff is not None:
                        str_dict["backoff_config.init_backoff"] = str(value.init_backoff)
                else:
                    str_dict[key] = str(value)
        return str_dict


class MergeType(str, Enum):
    """Enum of the possible IO Manager merge types
    - "deduplicate_insert"  <- Deduplicates on write
    - "update_only"  <- updates only the matches records
    - "upsert"  <- updates existing matches and inserts non matched records
    - "replace_and_delete_unmatched" <- updates existing matches and deletes unmatched
    - "custom" <- requires MergeOperationsConfig to be provided
    """

    deduplicate_insert = "deduplicate_insert"  # Deduplicates on write
    update_only = "update_only"  # updates only the records
    upsert = "upsert"  # updates and inserts
    replace_delete_unmatched = "replace_and_delete_unmatched"
    custom = "custom"


class OperationConfig(Config):
    """Basic operation config"""

    predicate: Optional[str] = None


class OperationAllConfig(Config):
    """Configuration for `_all` operations"""

    predicate: Optional[str] = None
    except_cols: Optional[list[str]] = None


class OperationWithUpdatesConfig(Config):
    """Configuration for operations that allow specific column updates"""

    updates: dict[str, str]
    predicate: Optional[str] = None


class WhenNotMatchedInsert(OperationWithUpdatesConfig):
    """When not matched statement"""

    pass


class WhenNotMatchedInsertAll(OperationAllConfig):
    """When not matched insert all statement"""

    pass


class WhenMatchedUpdate(OperationWithUpdatesConfig):
    """When matched update statement"""

    pass


class WhenMatchedUpdateAll(OperationAllConfig):
    """When matched update all statement"""

    pass


class WhenMatchedDelete(OperationConfig):
    """When matched delete statement"""

    pass


class WhenNotMatchedBySourceDelete(OperationConfig):
    """When not matched by source delete statement"""

    pass


class WhenNotMatchedBySourceUpdate(OperationWithUpdatesConfig):
    """When not matched by source update statement"""

    pass


class MergeOperationsConfig(Config):
    """Configuration for each merge operation. Only used with merge_type 'custom'.

    If you have multiple when statements of a single operation, they are evaluated in the order as provided in the list.
    """

    when_not_matched_insert: Optional[list[WhenNotMatchedInsert]] = None
    when_not_matched_insert_all: Optional[list[WhenNotMatchedInsertAll]] = None
    when_matched_update: Optional[list[WhenMatchedUpdate]] = None
    when_matched_update_all: Optional[list[OperationAllConfig]] = None
    when_matched_delete: Optional[list[WhenMatchedDelete]] = None
    when_not_matched_by_source_delete: Optional[list[WhenNotMatchedBySourceDelete]] = None
    when_not_matched_by_source_update: Optional[list[WhenNotMatchedBySourceUpdate]] = None


class MergeConfig(Config):
    """Configuration for the MERGE operation."""

    merge_type: MergeType
    """The type of MERGE to execute."""

    predicate: Optional[str] = None
    """SQL like predicate on how to merge, passed into DeltaTable.merge()

    This can also be set on the asset definition metadata using the `merge_predicate` key"""

    source_alias: Optional[str] = None
    """Alias for the source table"""

    target_alias: Optional[str] = None
    """Alias for the target table"""

    error_on_type_mismatch: bool = True
    """specify if merge will return error if data types are mismatching"""

    merge_operations_config: Optional[MergeOperationsConfig] = None
    """Full configuration of each merge operation, only use with merge_type='custom'"""
