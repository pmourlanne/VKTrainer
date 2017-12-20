# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, send_file, request, jsonify
from werkzeug.exceptions import abort

from vktrainer import app, db
from vktrainer.models import TrainingSet, Photo, TrainingResult
from vktrainer.utils import get_object_or_404


@app.route('/')
def home():
    training_sets = TrainingSet.query.order_by(TrainingSet.name).all()
    return render_template('home.html', training_sets=training_sets)


@app.route('/trainingset/<int:pk>')
def training_set(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    first_photo = training_set.get_first_photo()

    if not first_photo:
        return render_template('empty_training_set.html')

    return redirect(url_for('training_set_photo', training_set_pk=pk, pk=first_photo.id))


@app.route('/trainingset/<int:training_set_pk>/photo/')
def training_set_photo(training_set_pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)

    ctx = {
        'training_set': training_set,
    }

    return render_template('training_set_photo.html', **ctx)


@app.route('/trainingset/<int:training_set_pk>/photo/<int:pk>')
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


@app.route('/trainingresult/<int:pk>')
def training_result(pk):
    training_result = get_object_or_404(TrainingResult, TrainingResult.id == pk)
    training_set = training_result.training_set
    photo = training_result.photo

    previous_result = training_set.training_results.filter(TrainingResult.id < pk).order_by('-id').first()
    next_result = training_set.training_results.filter(TrainingResult.id > pk).order_by('id').first()

    ctx = {
        'training_result': training_result,
        'training_set': training_set,
        'photo': photo,
        'previous_result': previous_result,
        'next_result': next_result,
    }

    return render_template('training_result.html', **ctx)


@app.route('/trainingresult/<int:pk>', methods=['POST', ])
def training_result_delete(pk):
    training_result = get_object_or_404(TrainingResult, TrainingResult.id == pk)
    training_set = training_result.training_set

    next_result = training_set.training_results.filter(TrainingResult.id > pk).order_by('id').first()
    if not next_result:
        next_result = training_set.training_results.filter(TrainingResult.id < pk).order_by('-id').first()

    success_url = next_result.get_absolute_url() if next_result else training_set.get_absolute_url()

    db.session.delete(training_result)
    db.session.commit()

    return jsonify({'url': success_url})


@app.route('/photo/<int:pk>')
def show_photo(pk):
    photo = get_object_or_404(Photo, Photo.id == pk)
    return send_file(photo.get_path())


@app.route('/trainingset/<int:training_set_pk>/photo/<int:pk>/result', methods=['POST', ])
def training_set_photo_post_result(training_set_pk, pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)
    photo = training_set.photos.filter_by(id=pk).first()

    if photo is None:
        abort(404)

    data = request.form
    result = data['training_result']

    training_result = TrainingResult(photo=photo, training_set=training_set, result=result)
    db.session.add(training_result)
    db.session.commit()

    next_photo = training_set.get_next_photo(photo)

    return jsonify({
        'url': url_for('training_set_photo', training_set_pk=training_set_pk, pk=next_photo.id),
    })


@app.route('/trainingset/<int:pk>/results')
def training_set_extract_results(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    results = training_set.get_results()
    return jsonify({'results': results})
