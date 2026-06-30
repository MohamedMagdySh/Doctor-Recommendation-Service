import sys
sys.path.insert(0, '.')

from schemas import DoctorInput, ScoreBreakdown
from scoring import rank_doctors, compute_score, _price_score, _bayesian_rating
from explanation import build_explanation


def make_doctor(**kwargs) -> DoctorInput:
    defaults = dict(
        id="1", first_name="أحمد", last_name="محمد", specialty_name="قلب",
        languages=["ar"], rating_avg=4.5, rating_count=100,
        consultation_price_cents=30000, city_match=True,
        clinic_id="c1", clinic_name="عيادة النيل", clinic_address="القاهرة",
        nearest_available_slot="2025-07-01T10:00:00Z",
        completed_appointments_count=200, no_show_count=5,
        available_slots_next_14_days=8,
    )
    defaults.update(kwargs)
    return DoctorInput(**defaults)


def make_score(**kwargs) -> ScoreBreakdown:
    defaults = dict(rating_score=80, availability_score=60,
                    location_score=100, experience_score=50,
                    price_score=50, total_score=74)
    defaults.update(kwargs)
    return ScoreBreakdown(**defaults)


# ─── Scoring Tests ──────────────────────────────────────────

def test_bayesian_penalizes_few_reviews():
    high_count = _bayesian_rating(4.8, 200)
    low_count  = _bayesian_rating(5.0, 1)
    assert high_count > low_count
    print("✓ bayesian penalizes few reviews")


def test_city_match_gives_full_score():
    score = compute_score(make_doctor(city_match=True), price_score=50)
    assert score.location_score == 100
    print("✓ city match = 100")


def test_no_city_match_gives_penalty():
    score = compute_score(make_doctor(city_match=False), price_score=50)
    assert score.location_score == 30
    print("✓ no city match = 30")


def test_no_show_penalty_applied():
    good = compute_score(make_doctor(completed_appointments_count=500, no_show_count=5),  price_score=50)
    bad  = compute_score(make_doctor(completed_appointments_count=300, no_show_count=200), price_score=50)
    assert good.experience_score > bad.experience_score
    print("✓ no-show penalty applied")


def test_price_score_cheapest_gets_highest():
    prices = [20000, 30000, 40000]
    assert _price_score(20000, prices) > _price_score(30000, prices) > _price_score(40000, prices)
    print("✓ cheaper doctor gets higher price score")


def test_price_score_all_equal_returns_50():
    assert _price_score(30000, [30000, 30000, 30000]) == 50
    print("✓ equal prices return neutral score 50")


def test_rank_returns_top_5_only():
    doctors = [make_doctor(id=str(i), rating_avg=4.0 + i*0.1, rating_count=100) for i in range(8)]
    assert len(rank_doctors(doctors, top_n=5)) == 5
    print("✓ rank returns top 5 only")


def test_rank_is_descending():
    doctors = [make_doctor(id=str(i), rating_avg=3.0 + i*0.3, rating_count=200) for i in range(5)]
    scores = [s.total_score for _, s in rank_doctors(doctors, top_n=5)]
    assert scores == sorted(scores, reverse=True)
    print("✓ rank is descending")


# ─── Explanation Tests ──────────────────────────────────────

def test_explanation_mentions_rating_when_high():
    result = build_explanation(make_doctor(rating_avg=4.8, rating_count=320), make_score(rating_score=92))
    assert "4.8" in result
    print("✓ explanation mentions high rating")


def test_explanation_no_city_when_no_match():
    result = build_explanation(make_doctor(city_match=False), make_score(location_score=30))
    assert "مدينتك" not in result
    print("✓ explanation hides city when no match")


def test_explanation_mentions_city_when_match():
    result = build_explanation(make_doctor(city_match=True), make_score(location_score=100))
    assert "مدينتك" in result
    print("✓ explanation mentions city when match")


def test_explanation_mentions_slots_when_many():
    result = build_explanation(make_doctor(available_slots_next_14_days=12), make_score(availability_score=80))
    assert "مواعيد" in result
    print("✓ explanation mentions slots when many")


def test_explanation_mentions_price_when_cheap():
    """السعر بيظهر لما ما فيش highlights تانية تملا الـ 3 أماكن"""
    doc = make_doctor(
        rating_avg=3.5, rating_count=10,
        city_match=False,
        available_slots_next_14_days=0,
        completed_appointments_count=10,
        consultation_price_cents=20000,
    )
    result = build_explanation(doc, make_score(rating_score=40, availability_score=0,
                                               location_score=30, experience_score=5, price_score=75))
    assert "200" in result
    print("✓ explanation mentions price when cheap")


def test_explanation_never_empty():
    doc = make_doctor(rating_avg=3.0, rating_count=5, city_match=False,
                      available_slots_next_14_days=0, completed_appointments_count=10)
    result = build_explanation(doc, make_score(rating_score=30, availability_score=0,
                                               location_score=30, experience_score=5, price_score=50))
    assert len(result) > 0
    print("✓ explanation never empty")


# ─── Run All ────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_bayesian_penalizes_few_reviews,
        test_city_match_gives_full_score,
        test_no_city_match_gives_penalty,
        test_no_show_penalty_applied,
        test_price_score_cheapest_gets_highest,
        test_price_score_all_equal_returns_50,
        test_rank_returns_top_5_only,
        test_rank_is_descending,
        test_explanation_mentions_rating_when_high,
        test_explanation_no_city_when_no_match,
        test_explanation_mentions_city_when_match,
        test_explanation_mentions_slots_when_many,
        test_explanation_mentions_price_when_cheap,
        test_explanation_never_empty,
    ]

    print("=" * 45)
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ {t.__name__}: {e}")
            failed += 1

    print("=" * 45)
    print(f"  {passed} passed  |  {failed} failed  |  {len(tests)} total")
    print("=" * 45)
