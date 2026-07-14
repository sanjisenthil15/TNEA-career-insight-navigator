"""
Test the Admission Intelligence Engine
"""

from models.recommender import recommend

print("=" * 60)
print("Testing Recommendation Engine")
print("=" * 60)

results = recommend(
    cutoff=195,
    community="BC",
    branch_code="CS",
    district=None,
    year=2025
)

print(f"Recommendations Found : {len(results)}")
print("-" * 60)
for college in results[:10]:

    print(f"College      : {college['college_name']}")
    print(f"Branch       : {college['branch_name']}")
    print(f"Cutoff       : {college['cutoff']}")
    print(f"Probability  : {college['probability']}%")
    print(f"Level        : {college['recommendation_level']}")
    print(f"Ranking      : {college['ranking_score']}")

    print("AI Reason:")

    for reason in college["ai_reason"]:
        print(f"  ✓ {reason}")

    print("-" * 60)