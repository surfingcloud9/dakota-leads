from fastapi import FastAPI, Request
import os

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("/webhook received:", data)
    return {"status": "received"}

@app.post("/sms")
async def sms(request: Request):
    form = await request.form()
    print("/sms received:", dict(form))
    return "OK"
