from fastapi import FastAPI, HTTPException
from schemas import RecommendationRequest, RecommendationResponse, DoctorCard
from scoring import rank_doctors
from explanation import build_explanation

app = FastAPI(title="Doctor Recommendation Service")


@app.get("/")
def root():
    """Railway و أي حد يفتح الرابط يتأكد إن السيرفر شغال"""
    return {"status": "ok", "service": "Doctor Recommendation Service"}


@app.get("/health")
def health_check():
    """Health check endpoint صريح"""
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend_doctors(request: RecommendationRequest) -> RecommendationResponse:
    if not request.doctors:
        raise HTTPException(status_code=404, detail="مفيش دكاترة متاحين")

    top_ranked = rank_doctors(request.doctors, top_n=5)

    fallback_message = (
        f"مفيش دكاترة {request.specialty_name} في {request.city_name}، دي أقرب النتايج المتاحة"
        if request.is_fallback else None
    )

    return RecommendationResponse(
        specialty=request.specialty_name,
        city=request.city_name,
        total_found=len(request.doctors),
        is_fallback=request.is_fallback,
        fallback_message=fallback_message,
        top_doctors=[
            DoctorCard(
                rank=idx + 1,
                doctor_id=doc.id,
                full_name=f"د. {doc.first_name} {doc.last_name}",
                specialty_name=doc.specialty_name,
                profile_photo_url=doc.profile_photo_url,
                rating_avg=doc.rating_avg,
                rating_count=doc.rating_count,
                consultation_price_cents=doc.consultation_price_cents,
                currency=doc.currency,
                languages=doc.languages,
                clinic_id=doc.clinic_id,
                clinic_name=doc.clinic_name,
                clinic_address=doc.clinic_address,
                city_name=request.city_name,
                nearest_available_slot=doc.nearest_available_slot,
                available_slots_count=doc.available_slots_next_14_days,
                explanation=build_explanation(doc, score),
                score_breakdown=score,
            )
            for idx, (doc, score) in enumerate(top_ranked)
        ],
    )
