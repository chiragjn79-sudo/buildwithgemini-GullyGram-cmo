# How to Use, Maintain & Develop Gullygram CMO (Non-Coder Guide)

Welcome to **Gullygram CMO**! This guide is designed to help you run, edit, manage, and expand your AI Growth Marketing Consultant & Indian Festival Studio application—**even if you don't have coding experience**.

---

## 📖 Table of Contents
1. [How to Edit & Add Features without Coding](#1-how-to-edit--add-features-without-coding)
2. [Managing Marketing Data in Google Cloud Console](#2-managing-marketing-data-in-google-cloud-console)
3. [Running the Application Locally](#3-running-the-application-locally)
4. [Deploying Updates to Production](#4-deploying-updates-to-production)
5. [Saving & Pushing Changes to GitHub](#5-saving--pushing-changes-to-github)

---

## 1. How to Edit & Add Features without Coding

Since your workstation setup is temporary, here are 3 easy ways to continue working on your project using AI assistants:

### Option A: Use Cursor AI Editor (Recommended)
**Cursor** is a free AI code editor that lets you make changes by typing plain English instructions.

1. Download and install **[Cursor IDE](https://www.cursor.com/)**.
2. Open Cursor, click **File ➔ Clone Repository**, and paste:
   ```
   https://github.com/chiragjn79-sudo/buildwithgemini-GullyGram-cmo
   ```
3. Press `Ctrl + K` (Windows) or `Cmd + K` (Mac) or open the **AI Chat Sidebar**.
4. Type plain English prompts such as:
   - *"Add Raksha Bandhan and Janmashtami to the Indian Festival Studio."*
   - *"Change the accent color from amber to golden yellow."*
   - *"Add a export button for saved posts."*
5. Cursor will automatically edit the code and test the changes for you!

---

### Option B: Edit Directly in Your Web Browser (GitHub Web Editor)
You don't need to install anything on your computer!

1. Open your GitHub repository in any browser:
   [https://github.com/chiragjn79-sudo/buildwithgemini-GullyGram-cmo](https://github.com/chiragjn79-sudo/buildwithgemini-GullyGram-cmo)
2. Press the **`.` (period)** key on your keyboard.
3. This opens a cloud VS Code editor directly in your browser.
4. Edit any text or styling in `frontend/static/index.html` or `frontend/main.py`.
5. Click the **Source Control** icon on the left menu, enter a short note, and click **Commit and Push**.

---

### Option C: Google Project IDX (Free Cloud Environment)
Google offers **Project IDX**, a web-based IDE with Gemini AI built-in:

1. Go to **[idx.dev](https://idx.dev)** and sign in with your Google account.
2. Click **Import Repository** and paste your GitHub repository URL:
   `https://github.com/chiragjn79-sudo/buildwithgemini-GullyGram-cmo`
3. Work on your project inside a pre-configured Google cloud environment with built-in Gemini assistance.

---

## 2. Managing Marketing Data in Google Cloud Console

Your marketing channel benchmarks and lead conversion rates live in **Google Cloud Firestore**. You can edit data visually without touching any code:

1. Open the [Google Cloud Console - Firestore Page](https://console.cloud.google.com/firestore/databases/-default-/data).
2. Click on the `marketing_channels` collection.
3. You can click **Add Document** or select an existing channel (e.g., `whatsapp_groups`, `society_posters`) to edit cost-per-lead, conversion rates, or benchmark CAC directly in a visual web form.

---

## 3. Running the Application Locally

To test the application on your computer:

1. **Install Dependencies**:
   ```bash
   uv sync
   ```
2. **Set Environment Variables**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
   export GOOGLE_CLOUD_LOCATION="us-east1"
   export GOOGLE_GENAI_USE_VERTEXAI="true"
   export GOOGLE_MAPS_API_KEY="<your-api-key>"
   ```
3. **Start the Web Server**:
   ```bash
   cd frontend
   export PORT=8080
   uv run python main.py
   ```
4. Open `http://localhost:8080` in your web browser.

---

## 4. Deploying Updates to Production

Whenever you want to deploy your latest changes live to the cloud:

### Deploy Agent Engine (Backend)
```bash
uv run agents-cli deploy --update-env-vars GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY --no-confirm-project
```

### Deploy Web Frontend to Google Cloud Run
```bash
cd frontend
gcloud run deploy gullygram-cmo-frontend \
  --source=. \
  --region=us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>",AGENT_DIRECTORY="app"
```

---

## 5. Saving & Pushing Changes to GitHub

To save your work and push updates back to your GitHub repository, open your terminal in the project folder and run:

```bash
git add .
git commit -m "Update festival studio features"
git push
```
