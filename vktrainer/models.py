# -*- coding: utf-8 -*-

import json
import os
from shutil import copyfile

from flask import url_for

from vktrainer import db, app
from vktrainer.utils import get_md5


photos = db.Table('training_set_photos',
    db.Column('training_set_id', db.Integer, db.ForeignKey('training_set.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'))
)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64))
    picture = db.Column(db.String(128))
    md5 = db.Column(db.String(64))

    @classmethod
    def create_from_file(cls, file, check_if_exists=True):
        # We check no photo with the same md5 already exists in db
        md5 = get_md5(file)
        if check_if_exists:
            photo = cls.query.filter_by(md5=md5).first()
            if photo is not None:
                return None

        # We copy the file
        _, filename = os.path.split(file)
        path = os.path.join('vktrainer', app.config['PICTURES_FOLDER'], md5)
        copyfile(file, path)

        name, _ = os.path.splitext(filename)
        photo = Photo(name=name, md5=md5, picture=path)
        db.session.add(photo)
        db.session.commit()
        return photo

    def get_path(self):
        return os.path.join(app.config['PICTURES_FOLDER'], self.md5)


class TrainingSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64))
    photos = db.dynamic_loader(
        'Photo', secondary=photos, backref=db.backref('training_sets', lazy='dynamic'))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return url_for('training_set', pk=self.id)

    def get_edit_url(self):
        return url_for('training_set_edit', pk=self.id)

    def get_results_url(self):
        return url_for('training_set_extract_results', pk=self.id)

    def get_results(self):
        return [tr.get_pretty_result() for tr in self.training_results.all()]


class TrainingPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    training_set_id = db.Column(db.Integer, db.ForeignKey('training_set.id'))

    name = db.Column(db.String(64))
    instruction = db.Column(db.Text)
    training_set = db.relation('TrainingSet', backref=db.backref('patterns', lazy='dynamic'))
    pattern_ref = db.Column(db.String(64))
    position = db.Column(db.Integer)

    @property
    def pattern(self):
        from .patterns import REF_TO_PATTERN_CLASS
        return REF_TO_PATTERN_CLASS.get(self.pattern_ref)


class TrainingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    training_set_id = db.Column(db.Integer, db.ForeignKey('training_set.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))

    training_set = db.relation('TrainingSet', backref=db.backref('training_results', lazy='dynamic'))
    photo = db.relation('Photo')
    result = db.Column(db.Text)  # Result stored in JSON

    def get_pretty_result(self):
        try:
            loaded_result = json.loads(self.result)
        except ValueError:
            # Could not decode JSON
            loaded_result = None

        if loaded_result:
            result = {
                'state': 'OK',
                'value': loaded_result,
            }
        else:
            result = {
                'state': 'KO',
                'value': {},
            }

        return {
            'photo': {
                'name': self.photo.name,
                'id': self.photo.id,
            },
            'result': result,
            'id': self.id,
            'url': self.get_absolute_url(),
        }

    def get_absolute_url(self):
        return url_for('training_result', pk=self.id)
