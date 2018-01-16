# -*- coding: utf-8 -*-


class SelectPattern(object):
    input = 'select'
    choices = []


class GenderPattern(SelectPattern):
    reference = 'gender'
    choices = [
        ('Male'),
        ('Female'),
        ('Unknown'),
    ]


class AgePattern(SelectPattern):
    reference = 'age_select'
    choices = [
        ('0-5'),
        ('6-13'),
        ('14-25'),
        ('26-35'),
        ('36-45'),
        ('46-55'),
        ('56-65'),
        ('66-75'),
        ('76-99'),
    ]


class GlassesPattern(SelectPattern):
    reference = 'glasses'
    choices = [
        ('No glasses'),
        ('Glasses'),
        ('Sunglasses'),
    ]


class FacialHairPattern(SelectPattern):
    reference = 'facial_hair'
    choices = [
        ('No facial hair'),
        ('Beard'),
        ('Mustache only'),
    ]


class NumberInputPattern(object):
    reference = 'number'
    input = 'number_input'


class PointPattern(object):
    reference = 'point'
    input = 'point'


REF_TO_PATTERN_CLASS = {}


def register(klass):
    global REF_TO_PATTERN_CLASS
    REF_TO_PATTERN_CLASS[klass.reference] = klass


register(GenderPattern)
register(AgePattern)
register(GlassesPattern)
register(FacialHairPattern)
register(NumberInputPattern)
register(PointPattern)
