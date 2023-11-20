from datetime import timedelta
from flask import Flask, redirect, render_template, request, session, url_for
import db, string, random
app = Flask(__name__)
app.secret_key = "".join(random.choices(string.ascii_letters, k = 256))

@app.route("/", methods = ["GET"])
def index():
    msg = request.form.get("msg")
    if msg == None:
        return render_template("index.html")
    else:
        return render_template("index.html", msg = msg)

#アンケートページ
@app.route("/evaluation")
def evaluation():
    return render_template("evaluation.html")

#アンケート回答
@app.route("/", methods = ["POST"])
def evalution_exe():
    evalution = request.form.get("evalution")
    check_nightwear = request.form.get("check_nightwear")
    check_slippers = request.form.get("check_slippers")
    check_garbage = request.form.get("check_garbage")
    check_towel = request.form.get("check_towel")
    content = request.form.get("content")
    
    session["evalution"] = evalution
    session["check_nightwear"] = check_nightwear
    session["check_slippers"] = check_slippers
    session["check_garbage"] = check_garbage
    session["check_towel"] = check_towel
    session["content"] = content
    
    msg = "ご協力ありがとうございました。"
    
    return render_template("index.html",msg = msg)
    

#要望申請ページ
@app.route("/request")
def request():
    return render_template("request.html")

#要望申請
@app.route("/", methods = ["POST"])
def request_exe():
    request_nightwear = request.form.get("request_nightwear")
    request_bathtowel = request.form.get("request_bathtowel")
    request_water = request.form.get("request_water")
    request_facetowel = request.form.get("request_facetowel")
    request_tissue = request.form.get("request_tissue")
    request_tea = request.form.get("request_tea")
    request_toiletpaper = request.form.get("request_toiletpaper")
    request_slipperr = request.form.get("request_nightwear")
    request_hairbrush = request.form.get("request_hairbrush")
    request_toothbrush = request.form.get("request_toothbrush")
    content = request.form.get("content")

    session[request_nightwear] = request_nightwear
    session[request_bathtowel] = request_bathtowel
    session[request_water] = request_water
    session[request_facetowel] = request_facetowel
    session[request_tissue] = request_tissue
    session[request_tea] = request_tea
    session[request_toiletpaper] = request_toiletpaper
    session[request_slipperr] = request_slipperr
    session[request_hairbrush] = request_hairbrush
    session[request_toothbrush] = request_toothbrush
    session[content] = content
    
    msg = "ご要望承りました"
    
    return render_template("index.html",msg = msg)