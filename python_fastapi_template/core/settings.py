import importlib.metadata
import time

from pydantic_settings import BaseSettings, SettingsConfigDict

from python_fastapi_template.utils.basic import get_date_string_for_shanghai

run_at_ts = int(time.time())
run_at = get_date_string_for_shanghai(run_at_ts)
version = importlib.metadata.version('python_fastapi_template')


class HttpAuthSettings(BaseSettings):
    username: str = 'root'
    password: str = 'example'

    model_config = SettingsConfigDict(env_prefix='basic_auth_')


class AppSettings(BaseSettings):
    api_prefix: str = '/api'
    basic_auth: HttpAuthSettings = HttpAuthSettings()

    # meta
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
