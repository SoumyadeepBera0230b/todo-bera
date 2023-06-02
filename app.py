from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my.db"
app.config["SQLALCHEMY_BINDS"] = {"done": "sqlite:///done.db"}
db = SQLAlchemy(app)
app.app_context().push()


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


class Done(db.Model):
    __bind_key__ = "done"
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    # date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


db.create_all()


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        todo = Todo(
            title=request.form["title"],
            desc=request.form["desc"],
        )
        db.session.add(todo)
        db.session.commit()
    alltodos = Todo.query.all()
    return render_template("home.html", alltodos=alltodos, titles="HOME")


@app.route("/completed")
def completed():
    allcompleted = Done.query.all()
    return render_template("completed.html", titles="Completed", done=allcompleted)


@app.route("/delete/<int:sno>")
def delete(sno):
    alltodos = Todo.query.filter_by(sno=sno).first()
    db.session.delete(alltodos)
    db.session.commit()
    return redirect("/home")


@app.route("/done/<int:sno>")
def done(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    done = Done(
        title=todo.title,
        desc=todo.desc,
    )
    db.session.add(done)
    db.session.commit()
    return redirect(f"/delete/{sno}")


@app.route("/drop")
def drop():
    db.session.query(Done).delete()
    db.session.commit()
    return redirect("/completed")


@app.route("/update/<int:sno>", methods=["POST", "GET"])
def update(sno):
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/home")
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template("update.html", titles="Update", todo=todo)


if __name__ == "__main__":
    app.run(debug=True, port=50)
