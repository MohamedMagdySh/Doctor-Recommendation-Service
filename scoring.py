from schemas import DoctorInput, ScoreBreakdown

GLOBAL_RATING_AVG = 4.2
MIN_VOTES = 50
MAX_SLOTS = 20
MAX_COMPLETED = 600
WEIGHTS = {
    "rating":       0.35,
    "availability": 0.25,
    "location":     0.20,
    "experience":   0.10,
    "price":        0.10,
}


def _bayesian_rating(avg: float, count: int) -> float:
    return (count / (count + MIN_VOTES)) * avg + (MIN_VOTES / (count + MIN_VOTES)) * GLOBAL_RATING_AVG


def _no_show_penalty(completed: int, no_show: int) -> float:
    total = completed + no_show
    if total == 0:
        return 1.0
    rate = no_show / total
    return max(0.7, 1.0 - (rate / 0.3) * 0.3)


def _price_score(price: int, all_prices: list[int]) -> int:
    """
    بيقارن سعر الدكتور بمتوسط أسعار الدكاترة الموجودين.
    - لو سعره = المتوسط → 50
    - لو أرخص من المتوسط → أعلى من 50 (لحد 100)
    - لو أغلى من المتوسط → أقل من 50 (لحد 0)
    """
    if not all_prices or max(all_prices) == min(all_prices):
        return 50  # كل الأسعار متساوية → neutral

    avg = sum(all_prices) / len(all_prices)

    if price <= avg:
        # أرخص من المتوسط → score بين 50 و 100
        score = 50 + ((avg - price) / avg) * 50
    else:
        # أغلى من المتوسط → score بين 0 و 50
        max_price = max(all_prices)
        score = 50 - ((price - avg) / (max_price - avg)) * 50

    return int(max(0, min(100, score)))


def compute_score(doc: DoctorInput, price_score: int) -> ScoreBreakdown:
    rating_score      = int(max(0, min(100, ((_bayesian_rating(doc.rating_avg, doc.rating_count) - 1) / 4) * 100)))
    availability_score = int(min(100, (doc.available_slots_next_14_days / MAX_SLOTS) * 100))
    location_score    = 100 if doc.city_match else 30
    experience_score  = int((min(doc.completed_appointments_count, MAX_COMPLETED) / MAX_COMPLETED) * _no_show_penalty(doc.completed_appointments_count, doc.no_show_count) * 100)

    total = int(round(
        rating_score       * WEIGHTS["rating"]
        + availability_score * WEIGHTS["availability"]
        + location_score   * WEIGHTS["location"]
        + experience_score * WEIGHTS["experience"]
        + price_score      * WEIGHTS["price"]
    ))

    return ScoreBreakdown(
        rating_score=rating_score,
        availability_score=availability_score,
        location_score=location_score,
        experience_score=experience_score,
        price_score=price_score,
        total_score=total,
    )


def rank_doctors(doctors: list[DoctorInput], top_n: int = 5) -> list[tuple[DoctorInput, ScoreBreakdown]]:
    # نحسب الـ price scores الأول بناءً على كل الأسعار
    all_prices = [doc.consultation_price_cents for doc in doctors]
    price_scores = {doc.id: _price_score(doc.consultation_price_cents, all_prices) for doc in doctors}

    scored = [(doc, compute_score(doc, price_scores[doc.id])) for doc in doctors]
    scored.sort(key=lambda x: x[1].total_score, reverse=True)
    return scored[:top_n]
