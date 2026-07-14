"""
====================================================
TNEA AI Career Advisor
Main Flask Application
====================================================
"""

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for
)

import os

# Import our modules
from models.database import (
    get_all_colleges,
    get_all_districts,
    get_all_branches,
    get_college_details,
    get_college_branches,
    get_compare_colleges
)

from models.recommender import (
    recommend
)

# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "tnea-ai-career-advisor"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "database",
    "tnea.db"
)

app.config["DATABASE"] = DATABASE
# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():

    return render_template("landing.html")
# ==================================================
# ADMISSION PLANNER
# ==================================================

@app.route("/planner")
def planner():

    # Load data from database
    districts = get_all_districts()
    branches = get_all_branches()

    # Community Categories
    communities = [
        "OC",
        "BC",
        "BCM",
        "MBC",
        "SC",
        "SCA",
        "ST"
    ]

    # Available Years
    years = [
        2025,
        2024,
        2023
    ]

    return render_template(
        "planner.html",
        districts=districts,
        branches=branches,
        communities=communities,
        years=years
    )
# ==================================================
# GENERATE RECOMMENDATIONS
# ==================================================

@app.route("/recommend", methods=["POST"])
def recommend_route():

    try:

        cutoff = float(request.form["cutoff"])
        community = request.form["community"]
        branch = request.form["branch"]
        district = request.form.get("district", "")
        year = int(request.form["year"])

        recommendations = recommend(
            cutoff=cutoff,
            community=community,
            branch_code=branch,
            district=district if district else None,
            year=year
        )

        return render_template(
            "result.html",
            recommendations=recommendations,
            cutoff=cutoff,
            community=community,
            branch=branch,
            district=district,
            year=year
        )

    except Exception as e:

        return render_template(
            "planner.html",
            error=str(e)
        )
    # ==================================================
# COLLEGE DETAILS
# ==================================================

@app.route("/college/<int:college_code>")
def college_details(college_code):

    college = get_college_details(college_code)

    if college is None:

        return "College Not Found", 404

    branches = get_college_branches(college_code)

    return render_template(
        "college.html",
        college=college,
        branches=branches
    )
# ==================================================
# COMPARE COLLEGES
# ==================================================

@app.route("/compare")
def compare_colleges():

    college_codes = request.args.getlist("college")

    if len(college_codes) < 2:

        return "Please select at least two colleges for comparison."

    colleges = get_compare_colleges(college_codes)

    return render_template(

        "compare.html",

        colleges=colleges

    )
# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )