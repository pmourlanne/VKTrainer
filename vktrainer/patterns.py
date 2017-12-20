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
        ('Not a face'),
    ]


class NumberInputPattern(object):
    reference = 'number'
    input = 'number_input'


REF_TO_PATTERN_CLASS = {}


def register(klass):
    global REF_TO_PATTERN_CLASS
    REF_TO_PATTERN_CLASS[klass.reference] = klass


register(GenderPattern)
register(NumberInputPattern)
