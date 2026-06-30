from schemas import DoctorInput, ScoreBreakdown


def build_explanation(doc: DoctorInput, score: ScoreBreakdown) -> str:
    highlights = []

    if score.rating_score >= 88:
        highlights.append(f"تقييم ممتاز {doc.rating_avg:.1f}⭐ من {doc.rating_count} مريض")
    elif score.rating_score >= 75:
        highlights.append(f"تقييم جيد {doc.rating_avg:.1f}⭐ من {doc.rating_count} مريض")

    if doc.city_match:
        highlights.append("عيادته في نفس مدينتك")

    if doc.available_slots_next_14_days >= 10:
        highlights.append("مواعيد كتيرة متاحة دلوقتي")
    elif doc.available_slots_next_14_days >= 4:
        highlights.append(f"{doc.available_slots_next_14_days} مواعيد متاحة خلال أسبوعين")
    elif doc.available_slots_next_14_days >= 1:
        highlights.append("عنده مواعيد قريبة")

    if doc.completed_appointments_count >= 500:
        highlights.append(f"خبرة واسعة — {doc.completed_appointments_count}+ حالة")
    elif doc.completed_appointments_count >= 200:
        highlights.append(f"خبرة جيدة — {doc.completed_appointments_count}+ حالة")

    extra_langs = [l for l in doc.languages if l != "ar"]
    if extra_langs:
        highlights.append(f"بيتكلم {' و '.join(extra_langs)}")

    if score.price_score >= 70:
        price_egp = doc.consultation_price_cents // 100
        highlights.append(f"سعر مناسب — {price_egp} جنيه")

    return " · ".join(highlights[:3]) or "متاح في تخصصك"
