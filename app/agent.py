# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback
from app.celebration_agent import celebration_agent
from app.content_agent import content_agent
from app.tools import (
    add_or_update_marketing_channel,
    calculate_marketing_roi,
    find_nearby_places,
    generate_marketing_ad_image,
    generate_marketing_video,
    geocode_address,
    get_channel_details,
    list_marketing_channels,
    search_marketing_trends_and_case_studies,
)


def get_agent_engine_resource_name() -> str | None:
    metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                data = json.load(f)
                runtime_id = data.get("remote_agent_runtime_id")
                if runtime_id and runtime_id != "None":
                    return runtime_id
        except Exception:
            pass
    return None


agent_engine_name = get_agent_engine_resource_name()
code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_name
)


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Gullygram-CMO, an expert AI marketing consultant. "
        "You help founders, creators, and business owners optimize marketing channel strategies, "
        "evaluate Customer Acquisition Costs (CAC), estimate lead volume, formulate content plans, "
        "and generate viral social media content for sports communities (Gullygram, Table tennis, badminton, swimming) in Bengaluru societies. "
        "Remember all user details, stated preferences, business domain, health facts, and explicitly track and recall ALL user allergies (such as food, medication, or environmental allergies) across all sessions and conversations. "
        "You have specialized sub-agents: 'content_agent' (for viral social media posts) and 'celebration_agent' (for multi-religion Indian festival celebration posts with Gullygram wishes). "
        "Use your tools or sub-agents to query marketing channels from Firestore, look up specific channel details, "
        "search live growth marketing trends and case studies, calculate marketing ROI and lead metrics, "
        "geocode addresses, find nearby local businesses or competitor locations, "
        "generate visual ad creative images, generate short promotional video clips, generate viral social media content and Indian festival posts with Gullygram wishes, "
        "and record or update marketing channel recommendations. "
        "You can also execute Python code safely in a sandbox environment to run calculations and analysis."
    ),
    workflow_description="Analyze the user request, delegate content/celebration creation to content_agent/celebration_agent or query marketing tools as needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    sub_agents=[content_agent, celebration_agent],
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        list_marketing_channels,
        get_channel_details,
        add_or_update_marketing_channel,
        calculate_marketing_roi,
        search_marketing_trends_and_case_studies,
        geocode_address,
        find_nearby_places,
        generate_marketing_ad_image,
        generate_marketing_video,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)


