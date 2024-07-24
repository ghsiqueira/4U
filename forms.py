from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = StringField('Descrição', validators=[DataRequired()])
    cover_image = FileField('Imagem de Capa', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Imagens apenas!')])
    file = FileField('PDF', validators=[FileAllowed(['pdf'], 'PDFs apenas!')])
    publish_date = DateTimeLocalField('Data de Publicação', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Upload')