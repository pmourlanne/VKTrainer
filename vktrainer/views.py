# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, send_file, request, jsonify
from flask_login import logout_user, login_user, login_required, current_user
from werkzeug.exceptions import abort

from vktrainer import app, db
from vktrainer.forms import LoginForm
from vktrainer.models import TrainingSet, Photo, TrainingResult, User
from vktrainer.utils import get_object_or_404


@app.route('/')
def home():
    training_sets = TrainingSet.query.order_by(TrainingSet.name).all()
    return render_template('home.html', training_sets=training_sets)


@app.route('/login/', methods=['GET', 'POST', ])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = request.form['name']

        user = User.query.filter(User.name == name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

        login_user(user)

        # We should check that the url is safe
        next_url = request.args.get('next')
        if not next_url:
            next_url = url_for('home')

        return redirect(next_url)

    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/trainingset/<int:pk>')
@login_required
def training_set(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    first_photo = training_set.get_first_photo()

    if not first_photo:
        return render_template('empty_training_set.html')

    return redirect(url_for('training_set_photo', training_set_pk=pk))


@app.route('/trainingset/<int:training_set_pk>/photo/')
@login_required
def training_set_photo(training_set_pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)

    ctx = {
        'training_set': training_set,
    }

    return render_template('training_set_photo.html', **ctx)


@app.route('/trainingset/<int:training_set_pk>/patterns/')
@login_required
def training_set_patterns(training_set_pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)

    patterns = []
    for pattern in training_set.patterns.order_by('position'):
        patterns.append({
            'name': pattern.name,
            'instruction': pattern.instruction,
            'input': pattern.pattern.input,
            'choices': getattr(pattern.pattern, 'choices', []),
        })

    return jsonify({
        'patterns': patterns,
    })


@app.route('/trainingset/<int:training_set_pk>/photo/<int:pk>')
@login_required
def training_set_get_photo(training_set_pk, pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)
    photo = training_set.photos.filter_by(id=pk).first()

    if photo is None:
        abort(404)

    return jsonify({
        'pk': photo.id,
        'url': photo.get_absolute_url(),
        'name': photo.name,
    })


@app.route('/trainingset/<int:training_set_pk>/photo/next/')
@login_required
def training_set_next_photo(training_set_pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)

    current_photo = None
    current_photo_pk = request.args.get('photo')
    if current_photo_pk:
        current_photo = training_set.photos.filter_by(id=current_photo_pk).first()

    if current_photo:
        photo = training_set.get_next_photo(current_photo)
    else:
        photo = training_set.get_first_photo()

    return jsonify({
        'pk': photo.id,
        'url': photo.get_absolute_url(),
        'name': photo.name,
    })


@app.route('/photo/<int:pk>')
@login_required
def show_photo(pk):
    photo = get_object_or_404(Photo, Photo.id == pk)
    return send_file(photo.get_path())


@app.route('/trainingset/<int:training_set_pk>/result/', methods=['POST', ])
@login_required
def training_set_photo_post_result(training_set_pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)

    data = request.form
    photo_pk = data.get('photo')
    result = data.get('training_result')

    if not photo_pk:
        abort(404)
    photo = training_set.photos.filter_by(id=photo_pk).first()
    if photo is None:
        abort(404)

    training_result = TrainingResult(
        photo=photo,
        training_set=training_set,
        user=current_user,
        result=result,
    )
    db.session.add(training_result)
    db.session.commit()

    return jsonify({})


@app.route('/trainingset/<int:pk>/results')
@login_required
def training_set_extract_results(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    results = training_set.get_results()
    return jsonify({'results': results})
