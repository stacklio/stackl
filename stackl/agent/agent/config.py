from pydantic import BaseSettings


class Settings(BaseSettings):
    # General settings
    stackl_host: str = "http://localhost:8000"
    agent_name: str = "common"
    agent_type: str = "mock"
    redis_host: str = "localhost"
    redis_port: int = 6379
    secret_handler: str = "base64"
    loglevel: str = "INFO"

    # Kubernetes Handler
    stackl_namespace: str = None
    service_account: str = None

    # Settings for Vault
    vault_role: str = None
    vault_addr: str = None
    vault_mount_point: str = None

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
    stackl_cli_image: str = "stacklio/stackl-cli:v0.2.2dev"


settings = Settings()
