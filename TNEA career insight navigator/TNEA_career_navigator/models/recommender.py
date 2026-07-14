"""
=========================================================
TNEA AI Career Advisor
Recommendation Engine
=========================================================
"""

from models.database import recommend_colleges
# =========================================================
# RECOMMENDATION LEVELS
# =========================================================

def get_recommendation_level(student_cutoff, college_cutoff):
    """
    Determine recommendation level based on
    student's cutoff margin.
    """

    difference = student_cutoff - college_cutoff

    if difference >= 2.0:
        return "Highly Likely"

    elif difference >= 0.5:
        return "Competitive"

    else:
        return "Ambitious"
    # =========================================================
# ADMISSION PROBABILITY
# =========================================================

def calculate_probability(student_cutoff, college_cutoff):
    """
    Calculate admission probability based on
    cutoff difference.
    """

    difference = student_cutoff - college_cutoff

    if difference >= 3:
        return 99

    elif difference >= 2:
        return 95

    elif difference >= 1:
        return 90

    elif difference >= 0.5:
        return 80

    elif difference >= 0:
        return 70

    elif difference >= -0.5:
        return 60

    else:
        return 40
    # =========================================================
# RANKING SCORE
# =========================================================

def calculate_ranking_score(
    probability,
    recommendation_level
):
    """
    Calculate ranking score for sorting colleges.
    """

    score = probability

    if recommendation_level == "Highly Likely":
        score += 5

    elif recommendation_level == "Competitive":
        score += 2

    return score
# =========================================================
# AI RECOMMENDATION REASON
# =========================================================

def generate_ai_reason(
    student_cutoff,
    college_cutoff,
    recommendation_level,
    probability
):
    """
    Generate a human-readable explanation
    for the recommendation.
    """

    difference = round(student_cutoff - college_cutoff, 2)

    reasons = []

    # Cutoff analysis
    if difference >= 2:
        reasons.append(
            f"Your cutoff is {difference} marks above the previous cutoff."
        )

    elif difference >= 0:
        reasons.append(
            f"Your cutoff is {difference} marks above the previous cutoff, making this a realistic option."
        )

    else:
        reasons.append(
            f"Your cutoff is {abs(difference)} marks below the previous cutoff, so admission may be competitive."
        )

    # Recommendation level
    if recommendation_level == "Highly Likely":
        reasons.append(
            "This college is one of your strongest admission opportunities."
        )

    elif recommendation_level == "Competitive":
        reasons.append(
            "This college is worth applying to as it falls within a competitive range."
        )

    else:
        reasons.append(
            "This is an ambitious choice. Include it along with safer options."
        )

    # Probability
    reasons.append(
        f"Estimated admission probability: {probability}%."
    )

    return reasons
# =========================================================
# MAIN RECOMMENDATION ENGINE
# =========================================================

def recommend(
    cutoff,
    community,
    branch_code,
    district=None,
    year=2025
):
    """
    Main recommendation engine.
    """

    raw_results = recommend_colleges(
        cutoff=cutoff,
        community=community,
        branch_code=branch_code,
        district=district,
        year=year
    )

    recommendations = []

    for college in raw_results:

        college_cutoff = float(college["cutoff"])

        probability = calculate_probability(
            cutoff,
            college_cutoff
        )

        level = get_recommendation_level(
            cutoff,
            college_cutoff
        )

        ranking_score = calculate_ranking_score(
            probability,
            level
        )

        ai_reason = generate_ai_reason(
            cutoff,
            college_cutoff,
            level,
            probability
        )

        recommendations.append({

            "college_code": college["college_code"],

            "college_name": college["college_name"],

            "district": college["district"],

            "branch_code": college["branch_code"],

            "branch_name": college["branch_name"],

            "cutoff": college_cutoff,

            "probability": probability,

            "recommendation_level": level,

            "ranking_score": ranking_score,

            "ai_reason": ai_reason

        })

    recommendations.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    return recommendations