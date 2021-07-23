"""
Module for all configuration options of agent
"""

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

from pydantic import BaseSettings
from typing import List, Tuple, Union


class Settings(BaseSettings):
    """
    Settings class for agent
    """
    # General settings
    stackl_host: str = "http://localhost:8000"
    agent_name: str = "common"
    agent_type: str = "mock"
    redis_host: List[Tuple[str, int]] = '[["localhost", 26379]]'
    redis_port: int = 6379
    redis_password: str = None
    redis_sentinel: bool = False
    redis_sentinel_master: str = ""
    secret_handler: str = "base64"
    loglevel: str = "INFO"
    max_jobs: int = 10
    job_timeout: int = 3660

    # Kubernetes Handler
    stackl_namespace: str = None
    service_account: str = None

    # Settings for Vault
    vault_role: str = None
    vault_addr: str = None
    vault_mount_point: str = None
    vault_image: str = "vault:latest"

    # Settings for Conjur
    authenticator_client_container_name: str = None
    conjur_appliance_url: str = None
    conjur_account: str = None
    conjur_authn_token_file: str = None
    conjur_authn_url: str = None
    conjur_authn_login: str = None
    conjur_ssl_config_map: str = None
    conjur_ssl_config_map_key: str = None
    conjur_verify: str = "True"

    # Outputs
    stackl_cli_image: str = f"stacklio/stackl-cli:v{metadata.version('agent')}"


settings = Settings()
