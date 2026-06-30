# Doctor Recommendation Service

A smart recommendation engine that ranks doctors for a patient based on specialty and city, using multi-factor scoring and auto-generated explanations.

## Overview

The patient selects a **specialty** and a **city**. The service ranks the available doctors and returns the top 5, along with a short explanation for each one describing why that doctor is a good match.

## Scoring Logic

Each doctor receives a score out of 100 based on 5 weighted factors:

| Factor | Weight | Logic |
|---|---|---|
| **Rating** | 35% | Bayesian Average — prevents a new doctor with a perfect rating and few reviews from outranking a doctor with hundreds of reviews |
| **Availability** | 25% | Number of available time slots in the next 14 days |
| **Location** | 20% | Whether the doctor's clinic is in the same city as the patient |
| **Experience** | 10% | Number of completed appointments, with a penalty if the no-show rate exceeds 30% |
| **Price** | 10% | Relative comparison against the average price of all available doctors |

## Explanation Engine

Instead of a plain ranked list, the service builds a natural-language explanation highlighting the top 3 strengths of each doctor, generated directly from the data — no external AI API involved.

```
"Excellent rating 4.8⭐ from 320 patients · Clinic in your city · Many available slots"
```

## Fallback Handling

If no doctors are found in the patient's requested city, the backend re-queries without the city filter and the service returns doctors from other cities along with a clear message (`is_fallback: true`).

---

## API

### GET /

Health check — confirms the server is running.

### POST /api/v1/recommendations/doctors

**Request**

```json
{
  "patient": { "id": "uuid" },
  "specialty_name": "Cardiology",
  "city_name": "Cairo",
  "is_fallback": false,
  "doctors": [
    "list of candidate doctors from the database"
  ]
}
```

**Response**

```json
{
  "specialty": "Cardiology",
  "city": "Cairo",
  "total_found": 12,
  "is_fallback": false,
  "fallback_message": null,
  "top_doctors": [
    {
      "rank": 1,
      "full_name": "Dr. Ahmed Mohamed",
      "rating_avg": 4.8,
      "explanation": "Excellent rating 4.8 from 320 patients, clinic in your city",
      "score_breakdown": {
        "total_score": 86
      }
    }
  ]
}
```

---

## Project Structure

| File | Purpose |
|---|---|
| `schemas.py` | Input/output data models (Pydantic) |
| `scoring.py` | Scoring engine for each doctor |
| `explanation.py` | Builds the explanation sentence from the data |
| `main.py` | FastAPI endpoints |
| `query.sql` | SQL queries the backend runs against the database |
| `test_scoring.py` | Tests for scoring and explanation logic (14 tests) |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` to try the API via Swagger UI.

## Running Tests

```bash
python test_scoring.py
```

---

## Tech Stack

- **FastAPI** — API framework
- **Pydantic** — data validation
- **PostgreSQL** (assumed, per schema) — stores doctors, clinics, and appointments data

---

Graduation project — doctor recommendation system for a medical appointment booking platform.
