# -*- coding: utf-8 -*-


class PointPattern(object):
    reference = 'point'


class RectanglePattern(object):
    reference = 'rectangle'


REF_TO_PATTERN_CLASS = {}

def register(klass):
    global REF_TO_PATTERN_CLASS
    REF_TO_PATTERN_CLASS[klass.reference] = klass

register(PointPattern)
register(RectanglePattern)
