# -*- coding: utf-8 -*-

from flask import (
    render_template,
    redirect,
    url_for,
    send_file,
    request,
    jsonify,
    Blueprint,
)
from flask_login import logout_user, login_user, login_required, current_user
from werkzeug.exceptions import abort

from vktrainer.forms import LoginForm
from vktrainer.models import TrainingSet, Photo, TrainingResult, User


vktrainer_bp = Blueprint('vktrainer', __name__)


@vktrainer_bp.route('/')
def home():
    training_sets = TrainingSet.query.order_by(TrainingSet.name).all()
    return render_template('home.html', training_sets=training_sets)


@vktrainer_bp.route('/login/', methods=['GET', 'POST', ])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        name = request.form['name']

        user, created = User.get_or_create(name)
        login_user(user)

        # We should check that the url is safe
        next_url = request.args.get('next')
        if not next_url:
            next_url = url_for('vktrainer.home')

        return redirect(next_url)

    return render_template('login.html', form=form)


@vktrainer_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('vktrainer.home'))


@vktrainer_bp.route('/trainingset/<int:pk>')
@login_required
def training_set(pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == pk).first_or_404()
    first_photo = training_set.get_first_photo()

    if not first_photo:
        return render_template('empty_training_set.html')

    return redirect(url_for('vktrainer.training_set_photo', training_set_pk=pk))


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/photo/')
@login_required
def training_set_photo(training_set_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()

    ctx = {
        'training_set': training_set,
    }

    return render_template('training_set_photo.html', **ctx)


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/patterns/')
@login_required
def training_set_patterns(training_set_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()

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


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/percentage_done/')
@login_required
def training_set_percentage_done(training_set_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()

    return jsonify({
        'percentage_done': int(training_set.get_percentage_done()),
    })


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/photo/<int:pk>')
@login_required
def training_set_get_photo(training_set_pk, pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()
    photo = training_set.photos.filter_by(id=pk).first()

    if photo is None:
        abort(404)

    return jsonify({
        'pk': photo.id,
        'url': photo.get_absolute_url(),
        'name': photo.name,
    })


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/photo/next/')
@login_required
def training_set_next_photo(training_set_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()

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


@vktrainer_bp.route('/photo/<int:pk>')
@login_required
def show_photo(pk):
    photo = Photo.query.filter(Photo.id == pk).first_or_404()
    return send_file(photo.get_path())


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/result/', methods=['POST', ])
@login_required
def training_set_photo_post_result(training_set_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()

    data = request.form
    photo_pk = data.get('photo')
    result = data.get('training_result') or '{}'
    photo_is_incorrect = data.get('photo_is_incorrect') or False

    if not photo_pk:
        abort(404)
    photo = training_set.photos.filter_by(id=photo_pk).first()
    if photo is None:
        abort(404)

    TrainingResult.create(
        photo=photo,
        training_set=training_set,
        user=current_user,
        result=result,
        photo_is_incorrect=photo_is_incorrect,
    )

    return jsonify({})


@vktrainer_bp.route('/trainingset/<int:training_set_pk>/result/<int:result_pk>')
@login_required
def training_set_result(training_set_pk, result_pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == training_set_pk).first_or_404()
    training_result = training_set.training_results.filter(TrainingResult.id == result_pk).first_or_404()

    pretty_result = training_result.get_pretty_result()
    result_state = pretty_result['result']['state']
    result_value = pretty_result['result']['value']

    points_coordinates = []
    patterns_with_value = []
    patterns = training_set.patterns.order_by('position')
    for pattern in patterns:
        pattern_result = result_value.get(pattern.name)

        if pattern.pattern.input == 'point':
            try:
                x_abs = pattern_result['x_abs']
                y_abs = pattern_result['y_abs']

                points_coordinates.append((x_abs, y_abs))
                patterns_with_value.append((
                    pattern.name,
                    '&#10003;',
                ))

            except KeyError:
                patterns_with_value.append((
                    pattern.name,
                    None,
                ))

        else:
            patterns_with_value.append((
                pattern.name,
                pattern_result,
            ))

    ctx = {
        'training_set': training_set,
        'photo': training_result.photo,
        'result_state': result_state,
        'points_coordinates': points_coordinates,
        'patterns_with_value': patterns_with_value,
    }

    return render_template('training_set_result.html', **ctx)


@vktrainer_bp.route('/trainingset/<int:pk>/results')
@login_required
def training_set_results(pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == pk).first_or_404()
    results = training_set.get_results()
    return jsonify({'results': results})


@vktrainer_bp.route('/trainingset/<int:pk>/leaderboard')
def training_set_leaderboard(pk):
    training_set = TrainingSet.query.filter(TrainingSet.id == pk).first_or_404()

    ctx = {
        'training_set': training_set,
    }
    
    return render_template('training_set_leaderboard.html', **ctx)
