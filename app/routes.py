from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Album, Track, Like
from .forms import LoginForm, RegisterForm, AlbumForm, TrackForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/albums')
def albums():
    all_albums = Album.query.all()
    return render_template('albums.html', albums=all_albums)

@bp.route('/album/<int:album_id>', methods=['GET', 'POST'])
def album(album_id):
    album = Album.query.get_or_404(album_id)
    form = TrackForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        track = Track(title=form.title.data, album=album)
        db.session.add(track)
        db.session.commit()
        return redirect(url_for('main.album', album_id=album_id))
    return render_template('album.html', album=album, form=form)

@bp.route('/add_album', methods=['GET', 'POST'])
@login_required
def add_album():
    form = AlbumForm()
    if form.validate_on_submit():
        album = Album(title=form.title.data, release_date=form.release_date.data)
        db.session.add(album)
        db.session.commit()
        return redirect(url_for('main.albums'))
    return render_template('add_album.html', form=form)

@bp.route('/like/<int:track_id>')
@login_required
def like(track_id):
    if not Like.query.filter_by(user_id=current_user.id, track_id=track_id).first():
        like = Like(user_id=current_user.id, track_id=track_id)
        db.session.add(like)
        db.session.commit()
    return redirect(request.referrer)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
