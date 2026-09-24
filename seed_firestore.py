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

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-a4d830cde502"
COLLECTION_NAME = "marketing_channels"

SEED_DATA = [
    {
        "id": "paid-social",
        "name": "Paid Social Ads (Meta & TikTok)",
        "category": "Paid Media",
        "avg_cac": 28.50,
        "estimated_monthly_leads": 450,
        "conversion_rate": 0.035,
        "recommended_budget_min": 1000.0,
        "best_for": "B2C E-commerce, visual products, impulse purchases, mobile-first apps",
        "content_format": "Short-form vertical video (UGC), high-contrast carousel ad mockups",
    },
    {
        "id": "seo-content",
        "name": "Organic SEO & Thought Leadership",
        "category": "Organic Growth",
        "avg_cac": 12.00,
        "estimated_monthly_leads": 800,
        "conversion_rate": 0.048,
        "recommended_budget_min": 600.0,
        "best_for": "B2B SaaS, educational products, high-intent search buyers",
        "content_format": "Long-form search-optimized guides, case studies, comparison tables",
    },
    {
        "id": "email-newsletter",
        "name": "Email Newsletter & Lead Nurturing",
        "category": "Direct Response",
        "avg_cac": 8.00,
        "estimated_monthly_leads": 600,
        "conversion_rate": 0.062,
        "recommended_budget_min": 300.0,
        "best_for": "Community building, high LTV recurring subscriptions, creator brands",
        "content_format": "Weekly curated newsletter, drip sequences, special offer announcements",
    },
    {
        "id": "influencer-sponsorships",
        "name": "Influencer & Creator Collaborations",
        "category": "Paid Media",
        "avg_cac": 35.00,
        "estimated_monthly_leads": 300,
        "conversion_rate": 0.042,
        "recommended_budget_min": 1500.0,
        "best_for": "Lifestyle brands, niche tools, high-trust recommendations",
        "content_format": "Sponsored video integration, unboxing reviews, custom discount codes",
    },
    {
        "id": "cold-outreach",
        "name": "Outbound Cold Email & LinkedIn DM",
        "category": "Direct Response",
        "avg_cac": 45.00,
        "estimated_monthly_leads": 150,
        "conversion_rate": 0.085,
        "recommended_budget_min": 400.0,
        "best_for": "High-ticket B2B services, agency client acquisition, enterprise deals",
        "content_format": "Personalized 3-touch cold emails, personalized loom videos, LinkedIn messages",
    },
]


def seed():
    print(
        f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'..."
    )
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_DATA:
        doc_id = item["id"]
        data = {k: v for k, v in item.items() if k != "id"}
        collection_ref.document(doc_id).set(data, merge=True)
        print(f" - Seeded document '{doc_id}': {data['name']}")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed()
