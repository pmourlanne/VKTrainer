# -*- coding: utf-8 -*-

import os

from flask.ext.script import Manager

import vktrainer

manager = Manager(vktrainer.app)


@manager.command
def initdb():
    """Create the database tables"""
    from vktrainer.models import *

    print 'Using database %s' % vktrainer.db.engine.url
    vktrainer.db.create_all()
    print 'Created tables'


@manager.option('-f', '--folder', help='Pictures to import folder from')
def import_photos(folder):
    """Import photos from a folder"""
    from vktrainer.models import Photo

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    for file in files:
        photo = Photo.create_from_file(file)
        if photo is None:
            print 'Not importing {} since it is already in db'.format(file)
            continue

        print 'Successfully imported {}'.format(file)


if __name__ == '__main__':
    manager.run()
