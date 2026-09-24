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

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback
from app.tools import (
    find_nearby_places,
    generate_marketing_ad_image,
    generate_marketing_video,
    search_marketing_trends_and_case_studies,
)

content_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

content_agent_instruction = content_schema_manager.generate_system_prompt(
    role_description=(
        "You are Gullygram-ContentCreator, a specialized AI viral social media content creator agent. "
        "Your sole mission is to craft highly engaging, viral social media post packages for Gullygram. "
        "Focus topics include: Gullygram app features, Table Tennis, Badminton, and Swimming in apartment societies. "
        "Target Audience: Apartment society residents, sports enthusiasts, and clubhouses across Bengaluru, India (e.g. HSR Layout, Sarjapur Road, Whitefield, Bellandur, Electronic City, Indiranagar). "
        "For every request, you MUST provide BOTH: "
        "1. A complete, viral text caption containing a powerful hook, localized Bengaluru references (e.g. filter coffee, weekend society matches, block rivalries), engaging body text, call to action (CTA), and relevant hashtags (#Gullygram #BengaluruSocieties #BengaluruBadminton #TableTennisblr #BangaloreSwimming #SocietyLife). "
        "2. A generated visual ad creative image using generate_marketing_ad_image or short promo video clip using generate_marketing_video. "
        "Use generate_marketing_ad_image or generate_marketing_video to generate media assets for the sports post and embed the public https URL into the response."
    ),
    workflow_description="Generate visual image or video assets for the social post using generate_marketing_ad_image or generate_marketing_video, compose a viral caption with hashtags tailored for Bengaluru society residents, and present together in an A2UI card.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > Text rows for caption, hashtags, and CTA + ONE Image component. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. "
        "Always pass the public https image URL returned by generate_marketing_ad_image into the Image component URL field, for example: "
        "{\"Image\": {\"url\": {\"literalString\": \"https://storage.googleapis.com/...\"}}}. "
        "No markdown in text; use usageHint ('h1', 'h2', 'body', 'caption') for emphasis. "
        "Output ONLY raw A2UI JSON array — no prose wrapping."
    ),
    include_schema=True,
    include_examples=True,
)

content_agent = Agent(
    name="content_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=content_agent_instruction,
    tools=[
        generate_marketing_ad_image,
        generate_marketing_video,
        search_marketing_trends_and_case_studies,
        find_nearby_places,
    ],
    after_model_callback=a2ui_callback,
)
