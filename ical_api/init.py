import importlib
import pkgutil

from fastapi import FastAPI

import ical_api.core.middlewares.errors
import ical_api.core.middlewares.json_response
from ical_api.core.exception import register_exception_handler
from ical_api.core.settings import AppSettings
from ical_api.utils.mermaid import load_mermaid_plugin


def include_routers(app: FastAPI, module_name: str = 'ical_api.applications', api_prefix: str | None = None):
    if api_prefix is None:
        api_prefix = AppSettings().api_prefix

    pkg = importlib.import_module(module_name)
    prefix = pkg.__name__ + '.'
    for _, mod_name, _ in pkgutil.walk_packages(pkg.__path__, prefix):
        mod = importlib.import_module(mod_name)
        router = getattr(mod, 'router', None)
        if router is None:
            continue
        app.include_router(router, prefix=api_prefix)


def add_middlewares(app: FastAPI):
    ical_api.core.middlewares.errors.add_middleware(app)
    ical_api.core.middlewares.json_response.add_middleware(app)


def initial(app: FastAPI):
    include_routers(app)
    add_middlewares(app)
    register_exception_handler(app)
    load_mermaid_plugin()
