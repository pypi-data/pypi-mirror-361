import os
import logging
from enum import Enum
from dotenv import dotenv_values
from typing import Dict, Union


logger = logging.getLogger(__name__)


class ConfigKeys(str, Enum):
    AIRADAR_API_SERVER = "AIRADAR_API_SERVER"
    AIRADAR_API_VERSION = "AIRADAR_API_VERSION"
    AIRADAR_AUTH_CLIENT_ID = "AIRADAR_AUTH_CLIENT_ID"
    AIRADAR_AUTH_CLIENT_SECRET = "AIRADAR_AUTH_CLIENT_SECRET"  # nosec
    AIRADAR_AUTH_CLIENT_SCOPE = "AIRADAR_AUTH_CLIENT_SCOPE"
    AIRADAR_AUTH_CLIENT_PRIVATE_KEY = "AIRADAR_AUTH_CLIENT_PRIVATE_KEY"
    AIRADAR_AUTH_CLIENT_KID = "AIRADAR_AUTH_CLIENT_KID"
    AIRADAR_AUTH_TENANT_URL = "AIRADAR_AUTH_TENANT_URL"
    AIRADAR_LOG_LEVEL = "AIRADAR_LOG_LEVEL"


class Configurations:
    def __init__(self) -> None:
        self._settings_dict: Dict[ConfigKeys, Union[str, int, None]] = {
            ConfigKeys.AIRADAR_API_VERSION: "v1",
            ConfigKeys.AIRADAR_AUTH_CLIENT_SCOPE: "radar-api",
        }
        self.required_envs_keys = [
            ConfigKeys.AIRADAR_AUTH_TENANT_URL,
            ConfigKeys.AIRADAR_AUTH_CLIENT_ID,
            ConfigKeys.AIRADAR_API_SERVER,
        ]
        self._load_values()

    def _load_values(self) -> None:
        config = {**dotenv_values(".env"), **dotenv_values(".env.local"), **os.environ}

        for key in ConfigKeys:
            self._settings_dict[key] = config.get(key, self._settings_dict.get(key))

        for required_envs_key in self.required_envs_keys:
            if not self._settings_dict.get(required_envs_key):
                logger.critical(
                    f"""
                    {required_envs_key.name} is missing. Logged artifacts won't persist to the server.
                    Set an environment variables for {", ".join([k for k in self.required_envs_keys])}. 
                """
                )
                break

    def get_value(
        self, key: ConfigKeys, default: Union[str, int, None] = None
    ) -> Union[str, int, None]:
        return self._settings_dict.get(key, default)


airadar_configs = Configurations()
