# Gullygram CMO - AI Growth Marketing Consultant & Festival Studio

![Gullygram CMO Demo](demo.gif)

**Gullygram CMO** is an enterprise multi-agent AI marketing consultant built using Google's **Agent Development Kit (ADK 1.1.0 GA)**, **Vertex AI Agent Platform**, and Google's latest **Gemini & Omni models**.

It helps sports technology startups and apartment society communities create viral sports marketing content, evaluate Customer Acquisition Cost (CAC) and Return on Ad Spend (ROAS), and manage multi-religion Indian festival celebration campaigns with localized wishes.

---

## 🚀 Implemented Architecture & Agent Features

### 1. Multi-Agent Architecture
- **Root Agent (`gullygram-cmo`)**: Coordinates marketing consultancy, financial calculations, database lookups, and sub-agent delegation.
- **Viral Content Agent (`content_agent`)**: Specialized sub-agent focused on Gullygram sports communities (Badminton, Table Tennis, Swimming) across Bengaluru apartment societies (HSR Layout, Sarjapur Road, Whitefield). Generates viral captions and ad creative images.
- **Indian Festival Agent (`celebration_agent`)**: Multi-religion Indian festival tracking agent supporting celebrations across all faiths (Diwali, Eid, Christmas, Holi, Onam, Pongal, Ugadi, Ganesh Chaturthi, Durga Puja, Baisakhi, Gurpurab, Mahavir Jayanti, Buddha Purnima, Navroz). Generates heartwarming Gullygram wishes and festive creative assets.

### 2. Wired Tools & Google Cloud Integrations
- **Google Cloud Firestore (`query_marketing_channels`)**: Retrieves real-time channel benchmarks, conversion rates, and historical performance metrics from the `marketing_channels` collection.
- **Marketing Financial Sandbox (`calculate_marketing_roi`)**: Performs deterministic Python calculations for CAC, ROAS, expected lead volume, and campaign ROI.
- **Gemini Ad Image Generator (`generate_marketing_ad_image`)**: Generates marketing ad graphics via Gemini/Imagen models and uploads them directly to Google Cloud Storage.
- **Google Omni Video Generator (`generate_marketing_video`)**: Generates short promotional video clips using `gemini-omni-flash-preview` in the `global` region, saves artifacts via `tool_context.save_artifact()`, and uploads video bytes to Google Cloud Storage.
- **Google Cloud Storage Bucket**: Public media storage bucket (`gullygram-cmo-media-*`) hosting generated images and video files.
- **ADK Preload Memory Bank (`preload_memory`)**: Preloads business context, brand voice guidelines, target demographic details, and campaign memory across sessions.
- **A2UI v0.8 Schema Manager (`after_model_callback`)**: Intercepts model responses and renders rich, interactive UI cards using the A2UI Basic Catalog (`Card`, `Column`, `Row`, `Text`, `Image`, `Icon`).

---

## 🎨 Web Frontend & Festival Posts Studio

The project includes a FastAPI proxy and custom dark-purple & amber web UI:
- **Growth & Viral Chat View**: Interactive conversation workspace featuring A2UI card rendering and 3 quick prompt chips.
- **Indian Festival Posts Studio**: Multi-religion celebration calendar interface allowing users to select upcoming Indian festivals, view media graphics, edit captions and Gullygram wishes live, copy text with 1-click clipboard integration, and download media assets for social media stories.

---

## 🛠️ Planned / Future Enhancements

- [ ] Direct automated publishing to Instagram Graph API & WhatsApp Business API.
- [ ] Real-time bidding optimization for live paid ad accounts.

---

## 💻 Setup and Local Running Instructions

### Prerequisites
- Python 3.11+
- `uv` package manager (`pip install uv`)
- Google Cloud SDK (`gcloud`) authenticated to a GCP Project with Vertex AI, Firestore, and Cloud Storage APIs enabled.

### 1. Environment Configuration
Set the required environment variables:

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-east1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
```

### 2. Install Dependencies
Install python packages via `uv`:

```bash
uv sync
```

### 3. Run Agent Engine & Frontend Locally
To start the local FastAPI web server and chat frontend:

```bash
cd frontend
export PORT=8080
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/us-east1/reasoningEngines/<engine-id>"
export AGENT_DIRECTORY="app"
uv run python main.py
```

Once running, access the application in your local browser at `localhost` on port `8080`.

### 4. Deploying to Production

#### Deploy Agent Backend to Vertex AI Agent Platform:
```bash
uv run agents-cli deploy --update-env-vars GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY --no-confirm-project
```

#### Deploy Frontend to Google Cloud Run:
```bash
cd frontend
gcloud run deploy gullygram-cmo-frontend \
  --source=. \
  --region=us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>",AGENT_DIRECTORY="app"
```
