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
async def webhook(request: Request):
    client_ip = request.client.host if request.client else None
    logger.info(f"Received webhook request from IP: {client_ip}")
    
    # IP whitelisting for security
    if client_ip not in ALLOWED_IPS:
        logger.warning(f"Blocked request from unauthorized IP: {client_ip}")
        raise HTTPException(status_code=403, detail="Unauthorized IP")
    
    payload = await request.body()
    signature_header = request.headers.get("elevenlabs-signature")
    logger.info("Webhook request from allowed IP, proceeding with validation")
    
    if signature_header is None:
        logger.warning("Missing ElevenLabs-Signature header")
        raise HTTPException(status_code=400, detail="Missing ElevenLabs-Signature header")
    
    # Parse the signature header (format: t=timestamp,v0=hash)
    parts = signature_header.split(",")
    if len(parts) != 2:
        logger.warning(f"Invalid signature format: {signature_header}")
        raise HTTPException(status_code=400, detail="Invalid signature format")
    
    timestamp_str = parts[0][2:]  # Remove 't='
    hmac_signature = parts[1]     # 'v0=hash'
    logger.info(f"Parsed timestamp: {timestamp_str}, signature: {hmac_signature}")
    
    # Validate timestamp (reject if older than 30 minutes)
    tolerance = int(time.time()) - 30 * 60
    try:
        timestamp = int(timestamp_str)
    except ValueError:
        logger.warning(f"Invalid timestamp: {timestamp_str}")
        raise HTTPException(status_code=400, detail="Invalid timestamp")
    
    if timestamp < tolerance:
        logger.warning(f"Timestamp too old: {timestamp} < {tolerance}")
        raise HTTPException(status_code=400, detail="Timestamp too old")
    
    # Get the secret from environment variables
    secret = os.getenv("ELEVENLABS_WEBHOOK_SECRET")
    if not secret:
        logger.error("ELEVENLABS_WEBHOOK_SECRET not set")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Validate signature
    full_payload_to_sign = f"{timestamp}.{payload.decode('utf-8')}"
    mac = hmac.new(
        key=secret.encode("utf-8"),
        msg=full_payload_to_sign.encode("utf-8"),
        digestmod=sha256,
    )
    expected_digest = 'v0=' + mac.hexdigest()
    logger.info(f"Expected digest: {expected_digest}")
    
    if hmac_signature != expected_digest:
        logger.warning("Signature mismatch")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    logger.info("Signature validation passed")
    
    # Parse payload with error handling
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = data.get("type")
    if not event_type:
        logger.warning("Missing event type in payload")
        raise HTTPException(status_code=400, detail="Missing event type")
    
    logger.info(f"Webhook payload: {data}")
    
    # Handle specific event types with validation
    if event_type == "call_initiation_failure":
        logger.info("Processing call initiation failure event")
        event_data = data.get("data", {})
        if not event_data:
            logger.warning("Missing data in call_initiation_failure")
            return {"status": "received"}
        
        agent_id = event_data.get("agent_id")
        conversation_id = event_data.get("conversation_id")
        failure_reason = event_data.get("failure_reason")
        metadata = event_data.get("metadata", {})
        event_timestamp = data.get("event_timestamp")
        
        logger.info(f"Agent ID: {agent_id}")
        logger.info(f"Conversation ID: {conversation_id}")
        logger.info(f"Failure Reason: {failure_reason}")
        logger.info(f"Metadata: {metadata}")
        logger.info(f"Event Timestamp: {event_timestamp}")
        
        # Simulate register-call for retry
        try:
            register_payload = {"phone_number": "+1234567890", "agent_id": agent_id}
            response = requests.post("https://api.elevenlabs.io/v1/convai/twilio/register-call", json=register_payload, headers={"xi-api-key": os.getenv("XI_API_KEY", "")})
            logger.info(f"Simulated register-call: {response.status_code}")
        except Exception as e:
            logger.error(f"Register-call error: {str(e)}")
    
    elif event_type == "post_call_transcription":
        logger.info("Processing post-call transcription event")
        event_data = data.get("data", {})
        if not event_data:
            logger.warning("Missing data in post_call_transcription")
            return {"status": "received"}
        
        # Safe extraction
        user_id = event_data.get("metadata", {}).get("user_id", "unknown")
        transcript_summary = event_data.get("analysis", {}).get("transcript_summary", "")
        call_successful = event_data.get("analysis", {}).get("call_successful", False)
        full_transcript = event_data.get("transcript", "")
        
        logger.info(f"User ID: {user_id}")
        logger.info(f"Transcript Summary: {transcript_summary}")
        logger.info(f"Call Successful: {call_successful}")
        logger.info(f"Full Transcript: {full_transcript}")
        
        # Check for end_call intent (from config)
        if "end_call" in transcript_summary.lower():
            logger.info("Detected end_call intent from transcript - simulating tool use")
        
        # Simulate CRM update
        simulated_record = {
            "lastInteraction": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "conversationSummary": transcript_summary,
            "callOutcome": call_successful,
            "fullTranscript": full_transcript,
        }
        logger.info(f"Simulated CRM update: {simulated_record}")
        
        # Handle audio flags
        if 'has_audio' in data:
            logger.info(f"Has audio: {data['has_audio']}")
        if 'has_user_audio' in data:
            logger.info(f"Has user audio: {data['has_user_audio']}")
        if 'has_response_audio' in data:
            logger.info(f"Has response audio: {data['has_response_audio']}")
        
        # DJ Event Planner simulation
        if "dj" in transcript_summary.lower() or "wedding" in transcript_summary.lower():
            logger.info("DJ Event Planner: Extracted event - simulating scheduling")
    
    else:
        logger.info(f"Unhandled event type: {event_type}")
    
    return {"status": "received"}

@app.post("/sms")
async def sms(request: Request):
    form = await request.form()
    logger.info(f"SMS received: {dict(form)}")
    return "OK"