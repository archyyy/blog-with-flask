from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()


app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route("/")
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post_edit = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post_edit.title,
        subtitle=post_edit.subtitle,
        img_url=post_edit.img_url,
        author=post_edit.author,
        body=post_edit.body
    )
    if edit_form.validate_on_submit():
        post_edit.title = edit_form.title.data
        post_edit.subtitle = edit_form.subtitle.data
        post_edit.img_url = edit_form.img_url.data
        post_edit.author = edit_form.author.data
        post_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_edit.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        today = datetime.today().strftime("%B %d, %Y")
        post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            author=form.author.data,
            img_url=form.img_url.data,
            date=today,
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(debug=True)  # host='0.0.0.0', port=5000
