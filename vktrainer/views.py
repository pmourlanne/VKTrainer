# -*- coding: utf-8 -*-

import json
import os

from flask import render_template, redirect, url_for, send_file, request, jsonify, make_response
from werkzeug import secure_filename
from werkzeug.exceptions import abort

from vktrainer import app, db
from vktrainer.forms import CreateTrainingSetForm
from vktrainer.models import TrainingSet, Photo, TrainingResult
from vktrainer.utils import get_object_or_404


@app.route('/')
def home():
    training_sets = TrainingSet.query.order_by(TrainingSet.name).all()
    return render_template('home.html', training_sets=training_sets)


@app.route('/trainingset/create', methods=['GET', 'POST', ])
def training_set_create():
    form = CreateTrainingSetForm()

    if form.validate_on_submit():
        # Actually create the training set
        training_set = TrainingSet(name=form.name.data)
        db.session.add(training_set)
        db.session.commit()
        return redirect(training_set.get_edit_url())

    return render_template('training_set_create.html', form=form)


@app.route('/trainingset/<int:pk>/edit')
def training_set_edit(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    return render_template('training_set_edit.html', training_set=training_set)


@app.route('/trainingset/<int:pk>/add_photo', methods=['POST', ])
def training_set_add_photo(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)

    file = request.files['file']
    filename = secure_filename(file.filename)
    tmp_path = os.path.join(app.config['TMP_PICTURES_FOLDER'], filename)
    file.save(tmp_path)

    photo = Photo.create_from_file(tmp_path, check_if_exists=False)

    if photo is None:
        return make_response(jsonify({'error': 'Picture already exists'}), 400)

    training_set.photos.append(photo)
    db.session.commit()
    return jsonify({'status': 'ok'})


@app.route('/trainingset/<int:pk>')
def training_set(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    first_photo = training_set.photos.order_by('id').first()
    if not first_photo:
        return render_template('empty_training_set.html')
    return redirect(url_for('training_set_photo', training_set_pk=pk, pk=first_photo.id))


@app.route('/trainingset/<int:training_set_pk>/photo/<int:pk>')
def training_set_photo(training_set_pk, pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == training_set_pk)
    photo = training_set.photos.filter_by(id=pk).first()

    if photo is None:
        abort(404)

    previous_photo = training_set.photos.filter(Photo.id < pk).order_by('-id').first()
    if not previous_photo:
        # We are already at the first photo, we show the last one
        previous_photo = training_set.photos.order_by('-id').first()

    next_photo = training_set.photos.filter(Photo.id > pk).order_by('id').first()
    if not next_photo:
        # We are already at the last photo, we show the first one
        next_photo = training_set.photos.order_by('id').first()

    ctx = {
        'photo': photo,
        'training_set': training_set,
        'previous_photo': previous_photo,
        'next_photo': next_photo,
    }

    return render_template('training_set_photo.html', **ctx)


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


@app.route('/photo/<int:pk>/delete', methods=['POST', ])
def delete_photo(pk):
    photo = get_object_or_404(Photo, Photo.id == pk)
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'status': 'ok'})


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

    next_photo = training_set.photos.filter(Photo.id > pk).order_by('id').first()
    if not next_photo:
        next_photo = training_set.photos.order_by('id').first()

    return jsonify({
        'url': url_for('training_set_photo', training_set_pk=training_set_pk, pk=next_photo.id),
    })


@app.route('/trainingset/<int:pk>/results')
def training_set_extract_results(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    results = training_set.get_results()
    return jsonify({'results': json.dumps(results)})
