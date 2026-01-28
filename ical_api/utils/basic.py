import logging
from datetime import datetime
from functools import reduce
from typing import cast

import pytz

logger = logging.getLogger(__file__)


def optional_chain(obj, keys: str):
    def get_value(obj, key: str):
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key)

    try:
        return reduce(get_value, keys.split("."), obj)
    except (AttributeError, KeyError):
        return None


def get_date_string_for_shanghai(ts: int) -> str:
    return cast(
        str, pytz.timezone("Asia/Shanghai").localize(datetime.fromtimestamp(ts)).strftime("%Y-%m-%dT%H:%M:%S%z")
    )
