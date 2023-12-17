from flask import Flask, redirect, render_template, url_for, request


app = Flask(__name__)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", page='index', title='Головна - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about")
def about():
    return render_template('about/index.html', page='about')


@app.route("/contacts")
def contacts():
    return render_template('contact/contact.html', page='contacts')


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "GET":
        return render_template('auth/sign_in.html')
    elif request.method == "POST":
        return render_template('auth/sign_in.html')
    

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template('auth/sign_up.html')
    elif request.method == "POST":
        return render_template('auth/sign_up.html')
    
    
    
@app.route("/heros")
def heros():
    return render_template("main/geroi.html", page='index')


@app.route("/about/history")
def history():
    return render_template('about/history.html', page='about')


@app.route("/about/olympiads")
def olympiads():
    return render_template('about/olymp.html', page='about')


@app.route("/about/symbols")
def symbols():
    return render_template('about/symbol.html', page='about')
    



if __name__ == '__main__':
    app.run(debug=True, port=5555)
