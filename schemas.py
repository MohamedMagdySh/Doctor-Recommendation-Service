from pydantic import BaseModel, Field
from typing import Optional


# ─── Input ─────────────────────────────────────────────────

class DoctorInput(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialty_name: str
    languages: list[str] = []
    rating_avg: float = Field(ge=0, le=5)
    rating_count: int = Field(ge=0)
    consultation_price_cents: int = Field(ge=0)
    currency: str = "EGP"
    city_match: bool
    profile_photo_url: Optional[str] = None
    clinic_id: str
    clinic_name: str
    clinic_address: str
    nearest_available_slot: Optional[str] = None
    completed_appointments_count: int = Field(ge=0)
    no_show_count: int = Field(ge=0)
    available_slots_next_14_days: int = Field(ge=0)


class PatientContext(BaseModel):
    id: str


class RecommendationRequest(BaseModel):
    patient: PatientContext
    specialty_name: str
    city_name: str
    is_fallback: bool = False             # الباك بيبعتها True لو مفيش في المدينة
    doctors: list[DoctorInput]


# ─── Internal ───────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    rating_score: int
    availability_score: int
    location_score: int
    experience_score: int
    price_score: int
    total_score: int


# ─── Output ─────────────────────────────────────────────────

class DoctorCard(BaseModel):
    rank: int
    doctor_id: str
    full_name: str
    specialty_name: str
    profile_photo_url: Optional[str]
    rating_avg: float
    rating_count: int
    consultation_price_cents: int
    currency: str
    languages: list[str]
    clinic_id: str
    clinic_name: str
    clinic_address: str
    city_name: str
    nearest_available_slot: Optional[str]
    available_slots_count: int
    explanation: str
    score_breakdown: Optional[ScoreBreakdown] = None


class RecommendationResponse(BaseModel):
    specialty: str
    city: str
    total_found: int
    is_fallback: bool                          # True لو النتايج من مدينة تانية
    fallback_message: Optional[str] = None    # "مفيش دكاترة قلب في الإسكندرية، دي أقرب النتايج"
    top_doctors: list[DoctorCard]
