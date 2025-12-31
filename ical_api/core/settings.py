import importlib.metadata
import time

from pydantic_settings import BaseSettings, SettingsConfigDict

from ical_api.utils.basic import get_date_string_for_shanghai

run_at_ts = int(time.time())
run_at = get_date_string_for_shanghai(run_at_ts)
version = importlib.metadata.version('ical_api')


class HttpAuthSettings(BaseSettings):
    username: str = 'root'
    password: str = 'example'

    model_config = SettingsConfigDict(env_prefix='basic_auth_', extra='ignore')


class VlrggSettings(BaseSettings):
    # calander
    fetch_match_time_semaphore: int = 15
    model_config = SettingsConfigDict(env_prefix='vlrgg_', extra='ignore')


class AppSettings(BaseSettings):
    api_prefix: str = '/api'
    basic_auth: HttpAuthSettings = HttpAuthSettings()
    vlrgg: VlrggSettings = VlrggSettings()

    # meta
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
