from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FloatField, BooleanField, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed

from wtforms.widgets import ListWidget, CheckboxInput

class EventForm(FlaskForm):
    name = StringField('Nom de l\'event', validators=[DataRequired(), Length(max=128)])
    description = StringField('Descripció', validators=[DataRequired(), Length(max=128)])
    email = StringField('Correu electrònic', validators=[DataRequired(), Email()])
    submit = SubmitField('Crear event')

class ParticipantForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(max=128)])
    email = StringField('Correu electrònic', validators=[Optional(), Email()])
    event_id = HiddenField()
    num_people = IntegerField('Nombre de persones representades',
                          default=1,
                          validators=[NumberRange(min=1, max=20)])
    send_email = BooleanField('Enviar correu de benvinguda')
    submit = SubmitField('Afegir participant')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ExpenseForm(FlaskForm):
    description = StringField('Descripció', validators=[DataRequired(), Length(max=256)])
    amount = FloatField('Import (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    payer_id = SelectField('Pagat per', coerce=int, validators=[DataRequired()])
    split_between = MultiCheckboxField('Compartit entre', coerce=int, choices=[], validators=[Optional()])
    date = StringField('Data', validators=[Optional()])
    receipt_image = FileField('Foto de la factura', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Afegir despesa')

class AccessEventForm(FlaskForm):
    token = StringField('Token d\'accés', validators=[DataRequired(), Length(max=256)])
    submit = SubmitField('Accedir a l\'event')

class EmailRecoveryForm(FlaskForm):
    email = StringField('Correu electrònic', validators=[DataRequired(), Email()])
    submit = SubmitField('Recuperar events')