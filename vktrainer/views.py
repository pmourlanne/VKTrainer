# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, send_file
from werkzeug.exceptions import abort

from vktrainer import app
from vktrainer.models import TrainingSet, Photo
from vktrainer.utils import get_object_or_404


@app.route('/')
def home():
    training_sets = TrainingSet.query.order_by(TrainingSet.name).all()
    return render_template('home.html', training_sets=training_sets)


@app.route('/trainingset/<int:pk>')
def training_set(pk):
    training_set = get_object_or_404(TrainingSet, TrainingSet.id == pk)
    first_photo = training_set.photos.first()
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
    next_photo = training_set.photos.filter(Photo.id > pk).order_by('id').first()

    ctx = {
        'photo': photo,
        'training_set': training_set,
        'previous_photo': previous_photo,
        'next_photo': next_photo,
    }

    return render_template('training_set_photo.html', **ctx)


@app.route('/photo/<int:pk>')
def show_photo(pk):
    photo = get_object_or_404(Photo, Photo.id == pk)
    return send_file(photo.get_path())
