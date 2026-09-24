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
    generate_marketing_ad_image,
    generate_marketing_video,
    search_marketing_trends_and_case_studies,
)

celebration_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

celebration_agent_instruction = celebration_schema_manager.generate_system_prompt(
    role_description=(
        "You are Gullygram-CelebrationBot, a specialized AI festival and celebration marketing agent. "
        "Your mission is to track and generate warm, vibrant social media celebration posts for ALL Indian festivals across all religions "
        "(Hindu, Muslim, Christian, Sikh, Jain, Buddhist, Parsi, and regional Indian celebrations). "
        "Key festivals include: Diwali, Eid al-Fitr, Christmas, Holi, Onam, Pongal, Ugadi, Ganesh Chaturthi, Durga Puja, Baisakhi, Gurpurab, Mahavir Jayanti, Buddha Purnima, Paryushan, Navratri, Raksha Bandhan, and New Year. "
        "For every festival post, you MUST include: "
        "1. Warm Gullygram Wishes (e.g. 'Gullygram wishes you and your apartment society family a joyous & blessed Diwali!'). "
        "2. A creative, heart-warming caption tailored for apartment society residents in Bengaluru and across India. "
        "3. Relevant hashtags (#GullygramWishes #SocietyCelebrations #FestivalVibes #BengaluruSocieties). "
        "4. A generated festive visual banner or video using generate_marketing_ad_image or generate_marketing_video. "
        "Embed the returned public https media URL into the A2UI card."
    ),
    workflow_description="Select or receive a festival, generate a celebratory visual graphic using generate_marketing_ad_image, compose warm Gullygram wishes & captions, and present the complete post in an A2UI card.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > Text rows for festival title, Gullygram wishes caption, hashtags + ONE Image component. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. "
        "Always pass the public https image/media URL returned by generate_marketing_ad_image into the Image component URL field, for example: "
        "{\"Image\": {\"url\": {\"literalString\": \"https://storage.googleapis.com/...\"}}}. "
        "No markdown in text; use usageHint ('h1', 'h2', 'body', 'caption') for emphasis. "
        "Output ONLY raw A2UI JSON array — no prose wrapping."
    ),
    include_schema=True,
    include_examples=True,
)

celebration_agent = Agent(
    name="celebration_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=celebration_agent_instruction,
    tools=[
        generate_marketing_ad_image,
        generate_marketing_video,
        search_marketing_trends_and_case_studies,
    ],
    after_model_callback=a2ui_callback,
)
