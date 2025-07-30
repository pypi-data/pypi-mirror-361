import enum
from typing import Any, Dict, List, Optional

import pydantic.networks
from pydantic import PostgresDsn

from src.alchemy_h8.rate_limiter import RateLimiterStrategy


class PoolType(enum.Enum):
    """Enum for SQLAlchemy connection pool types."""

    QUEUE_POOL = "QUEUE_POOL"
    ASYNC_QUEUE_POOL = "ASYNC_QUEUE_POOL"
    NULL_POOL = "NULL_POOL"


class CredentialProvider:
    pass


class DBConnectionConfig:
    """Configuration for database connection."""

    def __init__(
        self,
        url: pydantic.networks.PostgresDsn,
        # Connection pool settings
        pool_size: int = 5,
        pool_type: PoolType = PoolType.ASYNC_QUEUE_POOL,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        idle_connection_timeout: int = 600,  # in seconds
        # SSL settings
        use_ssl: bool = False,
        ssl_ca: Optional[str] = None,
        ssl_cert: Optional[str] = None,
        ssl_key: Optional[str] = None,
        # Read replica settings
        read_replica_hosts: Optional[List[PostgresDsn]] = None,
        use_read_replicas_for_reads: bool = True,
        # Retry settings
        retry_attempts: int = 3,
        retry_backoff: float = 0.5,
        retry_max_backoff: float = 10.0,
        max_retries: int = 3,
        base_retry_delay: float = 0.1,
        max_retry_delay: float = 2.0,
        retry_jitter: float = 0.1,
        # Circuit breaker settings
        use_circuit_breaker: bool = False,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_recovery_timeout: int = 30,
        # Rate limiter settings
        use_rate_limiter: bool = False,
        rate_limit_max_requests: int = 100,
        rate_limit_time_window: float = 1.0,
        rate_limit_strategy: RateLimiterStrategy = RateLimiterStrategy.TOKEN_BUCKET,
        rate_limit_max_delay: float = 2.0,
        # Logging settings
        echo: bool = False,
        echo_pool: bool = False,
        # Credential provider settings
        credential_provider: Optional[CredentialProvider] = None,
    ):
        """Initialize database connection configuration."""
        self._url = url
        self.driver = url.scheme.split("+")[1]
        # Validate driver is asyncpg
        if self.driver != "asyncpg":
            raise ValueError("Only asyncpg driver is supported for PostgreSQL")

        self.pool_size = pool_size
        self.pool_type = pool_type
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.idle_connection_timeout = idle_connection_timeout

        self.use_ssl = use_ssl
        self.ssl_ca = ssl_ca
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key

        self.read_replica_hosts = read_replica_hosts or []
        self.use_read_replicas_for_reads = use_read_replicas_for_reads

        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        self.retry_max_backoff = retry_max_backoff
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.max_retry_delay = max_retry_delay
        self.retry_jitter = retry_jitter

        # Circuit breaker settings
        self.use_circuit_breaker = use_circuit_breaker
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_recovery_timeout = circuit_breaker_recovery_timeout

        # Rate limiter settings
        self.use_rate_limiter = use_rate_limiter
        self.rate_limit_max_requests = rate_limit_max_requests
        self.rate_limit_time_window = rate_limit_time_window
        self.rate_limit_strategy = rate_limit_strategy
        self.rate_limit_max_delay = rate_limit_max_delay

        self.echo = echo
        self.echo_pool = echo_pool

        self.credential_provider = credential_provider

    @property
    def url(self) -> str:
        return self._url.unicode_string()

    def get_engine_args(self) -> Dict[str, Any]:
        """
        Get SQLAlchemy engine creation arguments.

        Returns:
            Dictionary of engine arguments
        """
        args: Dict[str, Any] = {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": self.pool_pre_ping,
            "echo": self.echo,
            "echo_pool": self.echo_pool,
        }

        # Add connect_args if needed for SSL or driver-specific options
        connect_args: Dict[str, Any] = {}

        # Handle SSL configuration
        if self.use_ssl:
            connect_args["ssl"] = True

            if self.ssl_ca:
                connect_args["sslrootcert"] = self.ssl_ca

            if self.ssl_cert:
                connect_args["sslcert"] = self.ssl_cert

            if self.ssl_key:
                connect_args["sslkey"] = self.ssl_key

        # Add driver-specific connection arguments
        # For asyncpg
        if self.driver == "asyncpg":
            # Convert pool_timeout to asyncpg timeout
            connect_args["timeout"] = self.pool_timeout

            # Add statement timeout (30s default)
            connect_args["command_timeout"] = 30.0

            # Add server settings for PostgreSQL
            connect_args["server_settings"] = {
                "application_name": "db_handler",
                "search_path": "public",
            }

        if connect_args:
            args["connect_args"] = connect_args

        return args

    @classmethod
    def get_read_replica_host_configs(cls, read_replica_hosts: List[PostgresDsn]) -> List["DBConnectionConfig"]:
        return [DBConnectionConfig(url) for url in read_replica_hosts]
