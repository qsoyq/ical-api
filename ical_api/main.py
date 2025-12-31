import logging

import typer
import uvicorn
from fastapi import FastAPI

from ical_api.core.events import lifespan
from ical_api.core.settings import version
from ical_api.init import initial
from ical_api.utils.logger import init_logger

cmd = typer.Typer()
app = FastAPI(title='ical-api', version=version, lifespan=lifespan)


initial(app)


@cmd.command()
def http(
    host: str = typer.Option('0.0.0.0', '--host', '-h', envvar='http_host'),
    port: int = typer.Option(8000, '--port', '-p', envvar='http_port'),
    reload: bool = typer.Option(False, '--debug', envvar='http_reload'),
    log_level: int = typer.Option(logging.DEBUG, '--log_level', envvar='log_level'),
):
    """启动 http 服务"""
    init_logger(log_level)
    logging.info(f"http server listening on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == '__main__':
    cmd()
