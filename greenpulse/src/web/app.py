from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import logging
import threading
import time
import schedule
from database import db
from config import config
# Import the scheduler jobs from the original main logic (which we will move/import)
# To avoid circular imports, we might need to restructure.
# For now, let's assume we copy the scheduler logic here or import it.

# We need to refactor the scheduler logic into a separate module or class
# Let's assume we have a `scheduler_service.py` that has `start_scheduler()`
# But for now, I'll define the app and we'll fix the imports in the next step.

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="/app/src/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="/app/src/web/templates")

logger = logging.getLogger("GreenPulse.Web")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Get latest status
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Last suggestion
    cursor.execute("SELECT * FROM irrigation_logs WHERE event_type='suggestion' ORDER BY timestamp DESC LIMIT 1")
    last_suggestion = cursor.fetchone()
    
    # Last watering
    cursor.execute("SELECT * FROM irrigation_logs WHERE event_type IN ('watering_end', 'manual') ORDER BY timestamp DESC LIMIT 1")
    last_watering = cursor.fetchone()
    
    # Recent weather history
    cursor.execute("SELECT * FROM weather_history ORDER BY timestamp DESC LIMIT 5")
    weather_history = cursor.fetchall()
    
    cursor.close()

    import json
    if last_suggestion and last_suggestion.get('raw_data'):
        try:
            last_suggestion['raw_data'] = json.loads(last_suggestion['raw_data'])
        except:
            last_suggestion['raw_data'] = {}
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "last_suggestion": last_suggestion,
        "last_watering": last_watering,
        "weather_history": weather_history
    })

@app.get("/logs", response_class=HTMLResponse)
async def read_logs(request: Request):
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM irrigation_logs ORDER BY timestamp DESC LIMIT 50")
    logs = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "config": config.options})

# We will add the startup event in main.py or here if this becomes the entry point.
