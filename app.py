from flask import Flask, render_template, request, redirect, url_for, session
from chat import ree

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def login():
    user_input =""
    if request.method == "POST":
        user_input = request.form['user_input'].lower()
        print(user_input)
        bot_response = ree(user_input)
        return render_template("index.html", bot_response=bot_response) 
    else:
        return render_template("Login.html")


if __name__ == "__main__":
    app.run(debug=True)