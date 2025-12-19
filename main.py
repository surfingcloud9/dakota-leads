from fastapi import FastAPI, Request, HTTPException
import os
import time
import hmac
import logging
from hashlib import sha256
import requests  # For API calls

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ElevenLabs static egress IPs for whitelisting (by region)
ALLOWED_IPS = [
    "34.67.146.145",  # US
    "34.59.11.47",    # US
    "35.204.38.71",   # EU
    "34.147.113.54",  # EU
    "35.185.187.110", # Asia
    "35.247.157.189"  # Asia
]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook():
    return {"client": {"name": "Ara"}}

@app.post("/sms")
async def sms(request: Request):
    form = await request.form()
    logger.info(f"SMS received: {dict(form)}")
    return "OK"
