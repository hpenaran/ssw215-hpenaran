from flask import Flask, render_template

app = Flask(__name__)

projects_db = [
    {
        "id": 1,
        "title": "Personal Portfolio",
        "description": (
            "I would like to make a professional website for myself for people "
            "to look at if they are curious about who I am."
        ),
        "likes": 0,
    },
    {
        "id": 2,
        "title": "Web App Dashboard",
        "description": (
            "I want to build a polished dashboard that helps users track habits, "
            "goals, and daily progress."
        ),
        "likes": 0,
    },
    {
        "id": 3,
        "title": "Fast Team Communication Tool",
        "description": (
            "I am designing a collaboration space where teams can share updates "
            "and manage ideas clearly."
        ),
        "likes": 0,
    },
]


@app.route("/")
def index():
    return render_template("index.html", projects=projects_db)


if __name__ == "__main__":
    app.run(debug=True)
