# -*- coding: utf-8 -*-


class PointPattern(object):
    reference = 'point'
    input = 'draw_point'


class RectanglePattern(object):
    reference = 'rectangle'
    input = 'draw_rectangle'


class SelectPattern(object):
    input = 'select'
    choices = []

    @classmethod
    def get_flattened_choices(cls):
        return ';'.join(cls.choices)


class MoodPattern(SelectPattern):
    reference = 'mood'
    choices = [
        ('Very angry'),
        ('Angry'),
        ('Neutral'),
        ('Happy'),
        ('Very Happy'),
    ]


class NumberInputPattern(object):
    reference = 'number'
    input = 'number_input'


REF_TO_PATTERN_CLASS = {}


def register(klass):
    global REF_TO_PATTERN_CLASS
    REF_TO_PATTERN_CLASS[klass.reference] = klass


register(PointPattern)
register(RectanglePattern)
register(MoodPattern)
register(NumberInputPattern)
