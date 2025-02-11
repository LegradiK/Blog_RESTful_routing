from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

cdeditor = CKEditor()
db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
    # initialise extensions with app
    Bootstrap5(app)
    cdeditor.init_app(app)
    db.init_app(app)
    return app

app = create_app()
app.secret_key = "SECRET_KEY"

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

class PostForm(FlaskForm):
    title = StringField("Blog Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired()])
    body = CKEditorField("Blog Contents", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = []
    for post in all_posts:
        posts.append({
            'id':post.id,
            'title':post.title,
            'subtitle':post.subtitle,
            'date':post.date,
            'body':post.body,
            'author':post.author,
            'img_url':post.img_url
        })

    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new_post', methods=['GET', 'POST'])
def add_post():
    post_form = PostForm()

    if post_form.validate_on_submit():
        today_date = date.today()
        new_post = BlogPost(
            title=post_form.title.data,
            subtitle=post_form.subtitle.data,
            date=today_date,
            author=post_form.author.data,
            img_url=post_form.img_url.data,
            body=post_form.body.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html', form=post_form)


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<post_id>', methods=['GET','POST'])
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)
    edit_form = PostForm(obj=post_to_edit)
    if edit_form.validate_on_submit():
        post_to_edit.title=edit_form.title.data
        post_to_edit.subtitle=edit_form.subtitle.data
        post_to_edit.img_url=edit_form.img_url.data
        post_to_edit.author=edit_form.author.data
        post_to_edit.body=edit_form.body.data
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html', post=post_to_edit, form=edit_form)


# TODO: delete_post() to remove a blog post from the database
@app.route('/delete/<post_id>')
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash(f"Post '{post_to_delete.title}' is deleted successfully!", "success")
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
