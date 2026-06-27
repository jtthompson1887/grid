import os
import json
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from ..database import Database
from ..ui.favicon import create as create_favicon

app = FastAPI()


@app.get('/api/state')
def get_state():
    db = Database()
    state = db.get_state()
    return JSONResponse(content=state.to_dict())


@app.get('/api/favicon.svg')
def get_favicon():
    db = Database()
    state = db.get_state()
    svg = create_favicon(state.latest.types)
    return Response(content=svg, media_type='image/svg+xml')
