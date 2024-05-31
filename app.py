from flask import Flask, request, render_template, redirect, flash, jsonify, session, make_response
from random import randint, choice, sample
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

# empty list where answers should go
RESPONSE_LIST = "responses"

# Further study to choose different survies
CURRENT_SURVEY = "current_survey"



@app.route('/')
def select_survey():
    """Renders list of surveys to start"""

    return render_template("choose-survey.html", surveys=surveys)

@app.route("/", methods=["POST"])
def pick_survey():
    """Choose a survey to start"""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("done.html")
    
    survey = surveys[survey_id]
    session[CURRENT_SURVEY] = survey_id

    return render_template("start.html", survey=survey)




@app.route('/begin', methods=["POST"])
def begin_survey():
    """Begins new survey"""

    # session stores a list of variables
    session[RESPONSE_LIST] = []

    return redirect("/questions/0")


@app.route('/answer', methods=["POST"])
def answer_question():
    """Gets answer, saves it and moves to next question"""

    # choice represents what user selects
    choice = request.form['answer']
    text = request.form.get("text", "")

    # res is response. Use session to store in list
    responses = session[RESPONSE_LIST]
    responses.append({"choice": choice, "text": text})


    session[RESPONSE_LIST] = responses
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if(len(responses) == len(survey.questions)):
        return redirect('/finished') # If all questions answered
    
    else:
        return redirect(f'/questions/{len(responses)}')
    

@app.route('/questions/<int:qid>')
def show_question(qid):
    """Display current question"""
    responses = session.get(RESPONSE_LIST)
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if (responses is None):
        return redirect('/')
    
    if (len(responses) == len(survey.questions)):
        # answered all questions
        return redirect('/finished')
    
    if(len(responses) != qid):
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)


@app.route('/finished')
def finished():
    """Survey complete."""

    survey_id = session[CURRENT_SURVEY]
    survey = surveys[survey_id]
    responses = session[RESPONSE_LIST]

    html = render_template("finished.html", survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
