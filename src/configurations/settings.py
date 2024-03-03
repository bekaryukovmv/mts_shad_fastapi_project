"""
A module with environment settings.
It is used to ensure that all settings are in one place.
And also in order to pull variables from the environment (secrets).

In order for the variables to be pulled up here, you need to create a .env file
And put in it the variables that are defined in the settings (db_host, db_name, private_key, public_key).
The example is in the file.env

important! file.env should not be included in git commits.
It contains information about how to connect to the database and other secrets
and can give access to the application to intruders.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str  # PostgreSQL database host
    db_name: str  # PostgreSQL database name
    private_key: str  # private key for encryption/decryption of the JWT token
    public_key: str  # public key for encryption/decryption of the JWT token
    access_token_expire_minutes: int = 3  # token lifetime
    algorithm: str = "RS256"  # the encryption algorithm
    db_test_name: str = "fastapi_project_test_db"  # PostgreSQL test database name
    max_connection_count: int = 10  # maximum number of connections

    @property
    def database_url(self) -> str:
        return f"{self.db_host}/{self.db_name}"

    @property
    def database_test_url(self) -> str:
        return f"{self.db_host}/{self.db_test_name}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
