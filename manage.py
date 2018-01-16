# -*- coding: utf-8 -*-

import os

from flask_script import Manager

from vktrainer import db, app

manager = Manager(app)


@manager.command
def syncdb():
    """Create the database tables"""
    # from vktrainer.models import *

    print('Using database %s' % db.engine.url)
    db.create_all()
    print('Created tables')


@manager.option('-f', '--folder', help='Pictures to import folder from')
def import_photos(folder):
    """Import photos from a folder"""
    from vktrainer.models import Photo

    folder_path = os.path.join('vktrainer', Photo.PICTURES_FOLDER)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    photos = []

    for file in files:
        photo = Photo.create_from_file(file)
        if photo is None:
            print('Not importing {} since it is already in db'.format(file))
            continue

        photos.append(photo)
        print('Successfully imported {}'.format(file))

    return photos


def create_gender_training_set(db, photos):
    from vktrainer.models import TrainingSet, TrainingPattern

    gender_age_set = TrainingSet(name='Gender & Age')
    db.session.add(gender_age_set)
    db.session.commit()

    for photo in photos:
        gender_age_set.photos.append(photo)

    gender = TrainingPattern(
        training_set=gender_age_set,
        name='Gender',
        instruction='Choose the gender that most fits the face',
        pattern_ref='gender',
        position=1,
    )
    age = TrainingPattern(
        training_set=gender_age_set,
        name='Age',
        instruction='Enter the estimated age of the person',
        pattern_ref='number',
        position=2,
    )
    db.session.add_all([gender, age])
    db.session.commit()

    return gender_age_set


def create_points_training_set(db, photos):
    from vktrainer.models import TrainingSet, TrainingPattern

    points_set = TrainingSet(name='Face detection')
    db.session.add(points_set)
    db.session.commit()

    for photo in photos:
        points_set.photos.append(photo)

    left_eye = TrainingPattern(
        training_set=points_set,
        name='Left eye',
        instruction='Click on the left eye of the face',
        pattern_ref='point',
        position=1,
    )
    right_eye = TrainingPattern(
        training_set=points_set,
        name='Right eye',
        instruction='Click on the right eye of the face',
        pattern_ref='point',
        position=2,
    )
    nose = TrainingPattern(
        training_set=points_set,
        name='Nose',
        instruction='Click on the nose of the face',
        pattern_ref='point',
        position=3,
    )
    db.session.add_all([left_eye, right_eye, nose])
    db.session.commit()

    return points_set


def create_full_training_set(db, photos):
    from vktrainer.models import TrainingSet, TrainingPattern

    full_set = TrainingSet(name='Full face tagging')
    db.session.add(full_set)
    db.session.commit()

    for photo in photos:
        full_set.photos.append(photo)

    gender = TrainingPattern(
        training_set=full_set,
        name='Gender',
        instruction='Choose the gender that most fits the face',
        pattern_ref='gender',
        position=1,
    )
    age = TrainingPattern(
        training_set=full_set,
        name='Age',
        instruction='Enter the estimated age of the person',
        pattern_ref='age_select',
        position=2,
    )
    glasses = TrainingPattern(
        training_set=full_set,
        name='Glasses',
        instruction='Is the person wearing glasses or sunglasses?',
        pattern_ref='glasses',
        position=3,
    )
    facial_hair = TrainingPattern(
        training_set=full_set,
        name='Facial hair',
        instruction='Does the person have facial hair?',
        pattern_ref='facial_hair',
        position=4,
    )
    left_eye = TrainingPattern(
        training_set=full_set,
        name='Left eye',
        instruction='Click on the left eye of the face',
        pattern_ref='point',
        position=5,
    )
    right_eye = TrainingPattern(
        training_set=full_set,
        name='Right eye',
        instruction='Click on the right eye of the face',
        pattern_ref='point',
        position=6,
    )
    mouth = TrainingPattern(
        training_set=full_set,
        name='Mouth',
        instruction='Click on the center of the mouth',
        pattern_ref='point',
        position=7,
    )
    db.session.add_all([gender, age, glasses, facial_hair, left_eye, right_eye, mouth])
    db.session.commit()

    return full_set


def create_training_sets(db, photos):
    # create_gender_training_set(db, photos)
    # create_points_training_set(db, photos)
    create_full_training_set(db, photos)


@manager.command
def bootstrapdb():
    """Bootstrap db with sample training set"""
    from vktrainer import db

    syncdb()
    photos = import_photos('test_pictures')
    create_training_sets(db, photos)

    print('Successfully bootstrapped db')


if __name__ == '__main__':
    manager.run()
