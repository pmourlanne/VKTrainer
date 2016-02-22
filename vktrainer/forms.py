# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms.fields import TextField
from wtforms.validators import Required, Length


class CreateTrainingSetForm(Form):
    name = TextField('Name', [Required(), Length(max=64)])
