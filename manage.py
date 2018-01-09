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


@manager.command
def bootstrapdb():
    """Bootstrap db with sample training set"""
    from vktrainer import db
    from vktrainer.models import TrainingSet, TrainingPattern

    syncdb()
    photos = import_photos('test_pictures')

    # We create the training sets
    gender_age_set = TrainingSet(name='Gender & Age')
    points_set = TrainingSet(name='Face detection')

    db.session.add_all([gender_age_set, points_set])
    db.session.commit()

    # We add the photos
    for photo in photos:
        gender_age_set.photos.append(photo)
        points_set.photos.append(photo)
    db.session.commit()

    # We create the patterns
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
        instruction='Enter the age of the person',
        pattern_ref='number',
        position=2,
    )

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

    db.session.add_all([gender, age, left_eye, right_eye, nose])
    db.session.commit()

    print('Successfully bootstrapped db')


if __name__ == '__main__':
    manager.run()
