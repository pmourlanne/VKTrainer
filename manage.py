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

    folder_path = os.path.join('vktrainer', app.config['PICTURES_FOLDER'])
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
    training_set = TrainingSet(name='Replicants')

    db.session.add(training_set)
    db.session.commit()

    # We add the photos
    for photo in photos:
        training_set.photos.append(photo)
    db.session.commit()

    # We create the patterns
    gender = TrainingPattern(
        training_set=training_set,
        name='Gender',
        instruction='Choose the gender that most fits the face',
        pattern_ref='gender',
        position=1,
    )
    age = TrainingPattern(
        training_set=training_set,
        name='Age',
        instruction='Enter the age of the person',
        pattern_ref='number',
        position=1,
    )

    db.session.add(gender)
    db.session.add(age)
    db.session.commit()

    print('Successfully bootstrapped db')


if __name__ == '__main__':
    manager.run()
