import collections as cl
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional
from wtforms import SubmitField, SelectField, TextAreaField, IntegerField
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)

rus_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
eng_alphabet = 'abcdefghijklmnopqrstuvwxyz'
# Index letter о in the Russian alphabet
rus_freq = 15
# Index letter e in the English alphabet
eng_freq = 4


class CaesarForm(FlaskForm):
    field_str = TextAreaField('Enter Text', validators=[DataRequired()])
    language = SelectField('Alphabet', choices=['Russian', 'English'])
    option = SelectField('Option', choices=['Encrypt', 'Decrypt'])
    shift = IntegerField('Shift', validators=[Optional()])
    result = TextAreaField('Result')
    submit = SubmitField('Do')


def decrypt(alphabet, encrypt_str, freq, shift=None):
    most_freq = cl.Counter(encrypt_str.lower()).most_common()
    for i in range(len(most_freq)):
        if most_freq[i][0] == ' ' or most_freq[i][0] == '-' or most_freq[i][0] == ',' or most_freq[i][0] == '.':
            del most_freq[i]
            break
    decrypt_str = ''
    if shift is not None:
        shifts = shift
    else:
        shifts = alphabet.find(most_freq[0][0]) - freq
    for letter in encrypt_str.lower():
        if letter not in alphabet:
            decrypt_str += letter
        else:
            index = alphabet.find(letter) - shifts
            decrypt_str += alphabet[index]
    return decrypt_str


def encrypt(string, shift, alphabet):
    encrypt_str = ''
    for letter in string.lower():
        if letter not in alphabet:
            encrypt_str += letter
        else:
            try:
                index = alphabet.find(letter) + shift
                encrypt_str += alphabet[index]
            except IndexError:
                index = alphabet.find(letter) + shift - len(alphabet)
                encrypt_str += alphabet[index]
    return encrypt_str


def frequency(lan):
    if lan == 'Russian':
        return rus_freq
    elif lan == 'English':
        return eng_freq


def lang(lan):
    if lan == 'Russian':
        return rus_alphabet
    elif lan == 'English':
        return eng_alphabet


@app.route('/', methods=['GET', 'POST'])
def home():
    form = CaesarForm()
    if form.validate_on_submit():
        if form.option.data == 'Encrypt':
            if form.field_str.data.lower()[0] not in lang(form.language.data):
                flash('Please Change Language')
            elif not form.shift.data:
                flash('Please Enter a Shift')
            else:
                form.result.data = encrypt(form.field_str.data.lower(), form.shift.data, lang(form.language.data))
        elif form.option.data == 'Decrypt':
            if form.field_str.data.lower()[0] not in lang(form.language.data):
                flash('Please Change Language!')
            if not form.shift.data:
                form.result.data = decrypt(lang(form.language.data), form.field_str.data.lower(),
                                           frequency(form.language.data))
            elif form.shift.data:
                form.result.data = decrypt(lang(form.language.data), form.field_str.data.lower(),
                                           frequency(form.language.data), shift=int(form.shift.data))
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
