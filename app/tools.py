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

import os
from typing import Any, Dict, List, Optional
import uuid
from google import genai
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types
import requests

PROJECT_ID = "qwiklabs-gcp-03-a4d830cde502"
COLLECTION_NAME = "marketing_channels"
BUCKET_NAME = "gullygram-cmo-media-qwiklabs-gcp-03-a4d830cde502"



def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized explicitly with the project ID string."""
    return firestore.Client(project=PROJECT_ID)


def list_marketing_channels(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List marketing channels from the Firestore database, optionally filtered by category.

    Args:
        category: Optional category filter (e.g. 'Paid Media', 'Organic Growth', 'Direct Response').

    Returns:
        A list of dictionaries containing channel details and performance metrics.
    """
    db = get_firestore_client()
    ref = db.collection(COLLECTION_NAME)
    if category:
        docs = ref.where("category", "==", category).stream()
    else:
        docs = ref.stream()

    channels = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        channels.append(data)
    return channels


def get_channel_details(channel_id: str) -> Dict[str, Any]:
    """Get detailed metrics and strategy guidelines for a specific marketing channel by ID.

    Args:
        channel_id: The unique ID of the marketing channel (e.g. 'paid-social', 'seo-content', 'email-newsletter').

    Returns:
        A dictionary with the channel details or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(channel_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return {"error": f"Channel with ID '{channel_id}' not found."}


def add_or_update_marketing_channel(
    channel_id: str,
    name: str,
    category: str,
    avg_cac: float,
    estimated_monthly_leads: int,
    conversion_rate: float,
    recommended_budget_min: float,
    best_for: str,
    content_format: str,
) -> str:
    """Add or update a marketing channel record in the Firestore database.

    Args:
        channel_id: Unique identifier for the channel (e.g., 'paid-social', 'cold-email').
        name: Display name of the marketing channel.
        category: Channel category (e.g., 'Paid Media', 'Organic Growth', 'Direct Response').
        avg_cac: Estimated average Customer Acquisition Cost in USD.
        estimated_monthly_leads: Projected monthly leads achievable.
        conversion_rate: Expected conversion rate (e.g., 0.035 for 3.5%).
        recommended_budget_min: Minimum recommended monthly budget in USD.
        best_for: Target audience or product type best suited for this channel.
        content_format: Key content types needed (e.g., 'Short video, vertical carousel').

    Returns:
        A success message string confirming the write operation.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(channel_id)
    payload = {
        "name": name,
        "category": category,
        "avg_cac": float(avg_cac),
        "estimated_monthly_leads": int(estimated_monthly_leads),
        "conversion_rate": float(conversion_rate),
        "recommended_budget_min": float(recommended_budget_min),
        "best_for": best_for,
        "content_format": content_format,
    }
    doc_ref.set(payload, merge=True)
    return f"Successfully saved marketing channel '{name}' (ID: {channel_id}) to Firestore."


def calculate_marketing_roi(
    monthly_budget: float,
    avg_cac: float,
    customer_ltv: float,
    conversion_rate: float = 0.04,
) -> Dict[str, Any]:
    """Calculates projected customer acquisitions, revenue, Return on Ad Spend (ROAS), and net ROI for a marketing campaign budget.

    Args:
        monthly_budget: Total monthly advertising/marketing spend in USD.
        avg_cac: Average Customer Acquisition Cost (CAC) in USD.
        customer_ltv: Lifetime Value (LTV) or revenue per acquired customer in USD.
        conversion_rate: Expected lead-to-customer conversion rate (default: 0.04 for 4%).

    Returns:
        A dictionary containing projected leads, acquired customers, gross revenue, net profit, ROAS, and ROI percentage.
    """
    if avg_cac <= 0:
        return {"error": "Average CAC must be greater than zero."}

    projected_customers = int(monthly_budget / avg_cac)
    projected_leads = (
        int(projected_customers / conversion_rate) if conversion_rate > 0 else 0
    )
    projected_revenue = round(projected_customers * customer_ltv, 2)
    net_profit = round(projected_revenue - monthly_budget, 2)
    roas = (
        round(projected_revenue / monthly_budget, 2) if monthly_budget > 0 else 0.0
    )
    roi_percent = (
        round((net_profit / monthly_budget) * 100, 2) if monthly_budget > 0 else 0.0
    )

    return {
        "monthly_budget": monthly_budget,
        "avg_cac": avg_cac,
        "customer_ltv": customer_ltv,
        "projected_leads": projected_leads,
        "projected_customers": projected_customers,
        "projected_revenue": projected_revenue,
        "net_profit": net_profit,
        "roas": roas,
        "roi_percent": f"{roi_percent}%",
    }


def search_marketing_trends_and_case_studies(
    query: str, limit: int = 5
) -> List[Dict[str, Any]]:
    """Searches public tech & growth marketing discussion archives for articles, strategy threads, and real-world case studies.

    Args:
        query: Marketing keyword, strategy topic, or campaign niche to search for (e.g., 'paid social', 'cold email', 'SaaS pricing').
        limit: Number of top results to return (default: 5, max: 10).

    Returns:
        A list of dictionaries with title, url, author, points, comments, and publication date.
    """
    api_url = os.getenv(
        "MARKETING_SEARCH_BASE_URL", "https://hn.algolia.com/api/v1/search"
    )
    headers = {}
    api_key = os.getenv("MARKETING_SEARCH_API_KEY")
    if api_key:
        headers["X-Api-Key"] = api_key

    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": min(limit, 10),
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])

        results = []
        for hit in hits:
            results.append({
                "title": hit.get("title"),
                "url": hit.get("url")
                or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "author": hit.get("author"),
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "created_at": hit.get("created_at"),
            })
        return results
    except Exception as e:
        return [{"error": f"Failed to fetch marketing trends: {str(e)}"}]


def geocode_address(address: str) -> Dict[str, Any]:
    """Converts a street address or location name into geographic coordinates using the Google Maps Geocoding API.

    Args:
        address: The street address or location name to geocode (e.g. '1600 Amphitheatre Parkway, Mountain View, CA').

    Returns:
        A dictionary with 'name', 'address', and 'location' (latitude & longitude coordinates).
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY is not configured in .env"}

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed: {data.get('error_message', data.get('status'))}"}

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address", address)
        loc = first_result.get("geometry", {}).get("location", {})

        return {
            "name": formatted_address,
            "address": formatted_address,
            "location": {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Geocoding request error: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> List[Dict[str, Any]]:
    """Finds nearby places of a given type around a geographic coordinate location using the Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Place type to search for (e.g. 'restaurant', 'cafe', 'store', 'lodging', 'gym').
        radius_meters: Radius in meters around the coordinate (default: 1000 meters).

    Returns:
        A list of dictionaries containing place 'name', 'address', and 'location'.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY is not configured in .env"}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        places_raw = data.get("places", [])

        results = []
        for item in places_raw:
            display_name = item.get("displayName", {}).get("text", "Unknown")
            address = item.get("formattedAddress", "")
            loc = item.get("location", {})
            results.append({
                "name": display_name,
                "address": address,
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                },
            })
        return results
    except Exception as e:
        return [{"error": f"Places API searchNearby error: {str(e)}"}]


def generate_marketing_ad_image(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a visual marketing ad image, hero banner, or promotional creative asset using the gemini-3.1-flash-lite-image model.

    Args:
        prompt: Detailed prompt describing the ad creative or promotional graphic to generate (e.g., 'Modern sleek social ad banner for organic coffee with bold typography').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the prompt, filename, and public HTTPS URL in Cloud Storage.
    """
    try:
        genai_client = genai.Client(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        parts = response.candidates[0].content.parts
        image_part = parts[0]
        image_bytes = image_part.inline_data.data
        mime_type = image_part.inline_data.mime_type or "image/jpeg"

        ext = "png" if "png" in mime_type else "jpg"
        filename = f"ad_creative_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact for Playground Artifacts panel
        artifact = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact)

        # 2. Upload image bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "prompt": prompt,
            "filename": filename,
            "public_url": public_url,
            "status": "Success",
        }
    except Exception as e:
        return {"error": f"Failed to generate marketing image: {str(e)}"}


def generate_marketing_video(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a short promotional or marketing video clip for Gullygram sports and society events using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Args:
        prompt: Detailed prompt describing the video clip (e.g., 'Short 5-second promo video of a badminton match in a society clubhouse in Bengaluru').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the prompt, filename, and public HTTPS URL in Cloud Storage.
    """
    try:
        genai_client = genai.Client(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        # Check output_video attribute on Interaction
        if hasattr(interaction, "output_video") and interaction.output_video:
            out_vid = interaction.output_video
            if hasattr(out_vid, "bytes") and out_vid.bytes:
                video_bytes = out_vid.bytes
            elif hasattr(out_vid, "data") and out_vid.data:
                video_bytes = out_vid.data
            elif hasattr(out_vid, "inline_data") and out_vid.inline_data:
                video_bytes = out_vid.inline_data.data
                if getattr(out_vid.inline_data, "mime_type", None):
                    mime_type = out_vid.inline_data.mime_type

        # Fallback to outputs list
        if not video_bytes and hasattr(interaction, "outputs") and interaction.outputs:
            for output in interaction.outputs:
                if hasattr(output, "content") and output.content:
                    for part in output.content:
                        if (
                            hasattr(part, "inline_data")
                            and part.inline_data
                            and part.inline_data.data
                        ):
                            video_bytes = part.inline_data.data
                            if part.inline_data.mime_type:
                                mime_type = part.inline_data.mime_type
                            break

        if not video_bytes:
            raise ValueError("No video bytes returned from gemini-omni-flash-preview model")

        if isinstance(video_bytes, str):
            import base64
            video_bytes = base64.b64decode(video_bytes)

        ext = "webm" if "webm" in mime_type else "mp4"
        filename = f"promo_video_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact for Playground Artifacts panel
        artifact = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact)

        # 2. Upload video bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "prompt": prompt,
            "filename": filename,
            "public_url": public_url,
            "status": "Success",
        }
    except Exception as e:
        return {"error": f"Failed to generate marketing video: {str(e)}"}






