import os
import pathlib

import dash
import dash_bootstrap_components as dbc
from dash import CeleryManager, DiskcacheManager

external_stylesheets = [dbc.themes.SOLAR]


if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(
        __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
    )
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)


app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    background_callback_manager=background_callback_manager,
)
server = app.server
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
