"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.

Why A2A: agents-cli 1.1.0 (GA) deploys ADK agents to Agent Runtime as A2A agents
and no longer registers the reasoning-engine operation schema the old
`agent_engines.get(...).stream_query()` path relied on (operation_schemas() comes
back empty). The container serves the A2A protocol over the Agent Engine HTTP
passthrough, so this proxy fetches the agent's card and sends messages with the
a2a-sdk client (the same path `agents-cli run --mode a2a` uses). This works for
both A2A and plain ADK 1.1.0 deployments (the container serves A2A either way).

Run:
  pip install -r requirements.txt
  export AGENT_ENGINE_RESOURCE_NAME="projects/.../locations/.../reasoningEngines/..."
  export AGENT_DIRECTORY="app"   # your agent's app directory (agents-cli-manifest.yaml)
  python main.py                 # -> http://localhost:8080
"""

import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskArtifactUpdateEvent,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/287012207859/locations/us-east1/reasoningEngines/7947017157890539520",
)
# The agent's app directory (matches agent_directory in agents-cli-manifest.yaml).
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
# Location is embedded in the resource name: projects/<p>/locations/<loc>/reasoningEngines/<id>.
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

# A2A endpoint for an Agent Runtime deployment, via the Agent Engine HTTP
# passthrough. The card lives at the well-known path under this base.
A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

# The agent tags its A2UI data parts with this mime type.
_A2UI_MIME = "application/json+a2ui"

# One set of ADC credentials, refreshed per request (access tokens expire ~1h).
_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    # Always return JSON so the browser never receives a plain-text 500 page
    # (which shows up in the chat as "Unexpected token 'I', "Internal S"... is
    # not valid JSON"). Any server-side failure now surfaces as a readable
    # message in the chat bubble instead.
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


# Reuse ONE A2A context per user so the agent remembers the conversation.
_contexts: dict[str, str] = {}
# Cache the agent card after the first fetch.
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        # Agent Runtime does not serve a public card URL, so point the client at
        # the passthrough base for message sends.
        card.url = A2A_BASE
        _card = card
    return _card


def _extract_parts(parts: list) -> list[dict]:
    """Turn A2A response parts into structured parts for the chat UI.

    Text parts pass through as {"kind": "text"}. A2UI data parts (tagged
    application/json+a2ui) become {"kind": "a2ui", "data": <message>} so the UI
    renders the card; each data part is one A2UI message (beginRendering or
    surfaceUpdate).
    """
    out: list[dict] = []
    for p in parts:
        root = getattr(p, "root", p)
        if isinstance(root, TextPart) and getattr(root, "text", None):
            out.append({"kind": "text", "text": root.text})
        elif getattr(root, "data", None) is not None:
            meta = getattr(root, "metadata", None) or {}
            mime = meta.get("mimeType") if isinstance(meta, dict) else None
            if mime == _A2UI_MIME:
                out.append({"kind": "a2ui", "data": root.data})
        elif isinstance(root, FilePart):
            uri = getattr(getattr(root, "file", None), "uri", None)
            if uri:
                out.append({"kind": "text", "text": uri})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=_contexts.get(user_id),
        )

        last_task = None
        got_artifact_update = False
        async for event in a2a_client.send_message(msg):
            if not isinstance(event, tuple):
                continue
            task, update = event
            if task is not None:
                last_task = task
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id
            if isinstance(update, TaskArtifactUpdateEvent):
                got_artifact_update = True
                parts.extend(_extract_parts(update.artifact.parts))

        # Non-streaming fallback: pull parts from the final task's artifacts.
        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        # The turn produced no text or UI (e.g. the agent only ran tools, or a
        # tool stalled). Be honest rather than silent.
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


# In-memory post store for saved celebration posts
_saved_festival_posts: list[dict] = [
    {
        "id": "post_diwali_demo",
        "festival": "Diwali (Festival of Lights)",
        "religion": "Hindu / Jain / Sikh",
        "date": "November 2026",
        "caption": "🪔 Gullygram wishes you and your apartment society family a luminous, prosperous & joyous Diwali! 🪔\n\nMay your clubhouse light up with victory, laughter, and unbreakable community spirit. From exciting society tournaments to bright festive sweets, let's celebrate togetherness!",
        "hashtags": "#GullygramWishes #HappyDiwali #SocietyCelebrations #FestivalOfLights #BengaluruSocieties",
        "media_url": "https://storage.googleapis.com/gullygram-cmo-media-qwiklabs-gcp-03-a4d830cde502/ad_creative_bfa7a61b.jpg",
        "created_at": "2026-09-24T09:40:00Z",
    },
    {
        "id": "post_eid_demo",
        "festival": "Eid al-Fitr",
        "religion": "Islam",
        "date": "March / April 2026",
        "caption": "🌙 Eid Mubarak from team Gullygram! 🌙\n\nGullygram wishes you, your family, and your society neighbors peace, harmony, and endless blessings. May your celebrations be filled with warm smiles, delicious Sheer Khurma, and victory on the society sports grounds!",
        "hashtags": "#GullygramWishes #EidMubarak #SocietyUnity #BengaluruFestivals #CommunityVibes",
        "media_url": "https://storage.googleapis.com/gullygram-cmo-media-qwiklabs-gcp-03-a4d830cde502/ad_creative_c95327d8.jpg",
        "created_at": "2026-09-24T09:40:00Z",
    },
    {
        "id": "post_christmas_demo",
        "festival": "Christmas & New Year",
        "religion": "Christianity / Universal",
        "date": "December 25, 2026",
        "caption": "🎄 Merry Christmas & Happy Holidays from Gullygram! 🎄\n\nWishing all society residents a season wrapped in joy, warmth, and cheerful athletic rivalries! May your clubhouse carry the magic of Christmas lights and friendly winter matches.",
        "hashtags": "#GullygramWishes #MerryChristmas #SocietyHoliday #BengaluruSports #JoyfulMoments",
        "media_url": "https://storage.googleapis.com/gullygram-cmo-media-qwiklabs-gcp-03-a4d830cde502/ad_creative_bfa7a61b.jpg",
        "created_at": "2026-09-24T09:40:00Z",
    }
]

INDIAN_FESTIVALS = [
    {"name": "Diwali (Festival of Lights)", "religion": "Hindu / Jain / Sikh", "month": "October / November"},
    {"name": "Eid al-Fitr & Eid al-Adha", "religion": "Islam", "month": "March / June"},
    {"name": "Christmas", "religion": "Christianity", "month": "December 25"},
    {"name": "Holi (Festival of Colors)", "religion": "Hinduism", "month": "March"},
    {"name": "Onam", "religion": "Kerala / Regional", "month": "August / September"},
    {"name": "Pongal / Makar Sankranti", "religion": "Tamil Nadu / South India", "month": "January 14-17"},
    {"name": "Ugadi / Gudi Padwa", "religion": "Karnataka / Andhra / Maharashtra", "month": "March / April"},
    {"name": "Ganesh Chaturthi", "religion": "Hinduism", "month": "August / September"},
    {"name": "Durga Puja & Navratri", "religion": "Hinduism / Regional", "month": "October"},
    {"name": "Baisakhi & Gurpurab", "religion": "Sikhism", "month": "April / November"},
    {"name": "Mahavir Jayanti & Paryushan", "religion": "Jainism", "month": "April / September"},
    {"name": "Buddha Purnima", "religion": "Buddhism", "month": "May"},
    {"name": "Navroz (Parsi New Year)", "religion": "Zoroastrianism", "month": "August"},
]


@app.get("/api/festivals")
async def get_festivals():
    return {"festivals": INDIAN_FESTIVALS}


@app.get("/api/festivals/posts")
async def get_saved_posts():
    return {"posts": _saved_festival_posts}


@app.post("/api/festivals/save")
async def save_festival_post(req: Request):
    body = await req.json()
    post_id = body.get("id") or f"post_{uuid.uuid4().hex[:8]}"
    
    # Check existing post to update or append new
    existing = next((p for p in _saved_festival_posts if p["id"] == post_id), None)
    new_post = {
        "id": post_id,
        "festival": body.get("festival", "Custom Celebration"),
        "religion": body.get("religion", "All Religions"),
        "date": body.get("date", "2026"),
        "caption": body.get("caption", ""),
        "hashtags": body.get("hashtags", "#GullygramWishes"),
        "media_url": body.get("media_url", ""),
        "created_at": body.get("created_at") or "2026-09-24T09:40:00Z",
    }
    
    if existing:
        existing.update(new_post)
    else:
        _saved_festival_posts.insert(0, new_post)
        
    return {"status": "Success", "post": new_post}


# Serve the chat UI (keep this mount last so /chat and /api win).
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

