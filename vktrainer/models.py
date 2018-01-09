# -*- coding: utf-8 -*-

import json
import os
import random
from shutil import copyfile

from flask import url_for, current_app as app
from flask_login import UserMixin

from sqlalchemy import func, desc

# from vktrainer import db, app, login_manager
from vktrainer import db, login_manager
from vktrainer.utils import get_md5


photos = db.Table('training_set_photos',
    db.Column('training_set_id', db.Integer, db.ForeignKey('training_set.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64))

    def __repr__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name):
        user = cls.query.filter(cls.name == name).first()

        if not user:
            user = cls(name=name)
            db.session.add(user)
            db.session.commit()

            return user, True

        return user, False


@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64))
    picture = db.Column(db.String(128))
    md5 = db.Column(db.String(64))

    PICTURES_FOLDER = 'pictures/'

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
        path = os.path.join('vktrainer', cls.PICTURES_FOLDER, md5)
        copyfile(file, path)

        name, _ = os.path.splitext(filename)
        photo = Photo(name=name, md5=md5, picture=path)
        db.session.add(photo)
        db.session.commit()
        return photo

    def get_path(self):
        return os.path.join(self.PICTURES_FOLDER, self.md5)

    def get_absolute_url(self):
        return url_for('vktrainer.show_photo', pk=self.id)


class TrainingSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64))
    photos = db.dynamic_loader(
        'Photo', secondary=photos, backref=db.backref('training_sets', lazy='dynamic'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return url_for('vktrainer.training_set', pk=self.id)

    def get_results_url(self):
        return url_for('vktrainer.training_set_results', pk=self.id)

    def get_leaderboard_url(self):
        return url_for('vktrainer.training_set_leaderboard', pk=self.id)

    def get_results(self):
        return [tr.get_pretty_result() for tr in self.training_results.all()]

    def get_leaderboard(self):
        count = func.count(TrainingResult.id)

        return self.training_results.join(
            TrainingResult.user,
        ).add_column(
            count,
        ).group_by(
            TrainingResult.user_id,
        ).order_by(
            desc(count),
        ).values(
            User.name,
            count,
        )

    def get_percentage_done(self):
        nb_photos_with_results = self.photos.filter(
            Photo.id.in_(self.training_results.with_entities(TrainingResult.photo_id))
        ).count()
        nb_photos = self.photos.count()

        return float(nb_photos_with_results) / nb_photos * 100

    def get_first_photo(self):
        if app.config['SHOW_PICTURES_ORDERING'] == 'linear':
            return self.photos.order_by('id').first()
        else:
            return self._get_next_photo_semi_random(None)

    def get_next_photo(self, photo):
        if app.config['SHOW_PICTURES_ORDERING'] == 'linear':
            return self._get_next_photo_linear(photo)
        else:
            return self._get_next_photo_semi_random(photo)

    def _get_next_photo_linear(self, photo):
        next_photo = self.photos.filter(Photo.id > photo.id).order_by('id').first()
        if not next_photo:
            # We are already at the last photo, we show the first one
            next_photo = self.photos.order_by('id').first()

        return next_photo

    def _get_previous_photo_linear(self, photo):
        previous_photo = self.photos.filter(Photo.id < photo.id).order_by('-id').first()
        if not previous_photo:
            # We are already at the first photo, we show the last one
            previous_photo = self.photos.order_by('-id').first()

        return previous_photo

    def _get_next_photo_semi_random(self, photo):
        """
        We serve a random photo without any results
        If there aren't any, we serve a random photo
        """

        photos_without_results = self.photos.filter(~Photo.id.in_(
            self.training_results.with_entities(TrainingResult.photo_id)
        ))
        if photo:
            photos_without_results = photos_without_results.filter(Photo.id != photo.id)

        nb_photos_without_results = photos_without_results.count()
        if nb_photos_without_results:
            return photos_without_results.all()[random.randint(0, nb_photos_without_results - 1)]
        else:
            nb_photos = self.photos.count()
            random_nb = random.randint(0, nb_photos - 1)
            return self.photos.all()[random_nb]

    def _get_previous_photo_semi_random(self, photo):
        # Don't want to allow previous photo in semi random mode (breaks UX)
        return None



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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    training_set = db.relation('TrainingSet', backref=db.backref('training_results', lazy='dynamic'))
    photo = db.relation('Photo')
    user = db.relation('User', lazy='joined', backref=db.backref('training_results'))
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
            'user': self.user.name if self.user else None,
            'result': result,
            'id': self.id,
        }

    @classmethod
    def create(cls, photo, training_set, user, result):
        training_result = cls(
            photo=photo,
            training_set=training_set,
            user=user,
            result=result,
        )

        db.session.add(training_result)
        db.session.commit()

        return training_result
