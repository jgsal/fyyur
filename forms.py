from datetime import datetime
from typing import Optional
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TelField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL
import re

#  ----------------------------------------------------------------
#  Dicts
#  ----------------------------------------------------------------

stateops=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]

genreops=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]

#  ----------------------------------------------------------------
#  Forms, Classes, Validation
#  ----------------------------------------------------------------

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        # default=datetime.today()#,
        format='%m-%d-%Y %H:%M'
    )

class VenueForm(Form):
    def validate_phone(form, field):
        if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", form.phone.data):
            raise ValidationError("Invalid phone number.")

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=stateops
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[URL(),DataRequired()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=genreops
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(),DataRequired()]
    )
    website_link = StringField(
        'website_link', validators=[URL(),DataRequired()]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )

class ArtistForm(Form):
    def validate_phone(form, field):
        if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", form.phone.data):
            raise ValidationError("Invalid phone number.")

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=stateops
    )
    phone = StringField(
        # TODO implement validation logic for phone
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[URL(),DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genreops
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL(),DataRequired()]
     )

    website_link = StringField(
        'website_link', validators=[URL(),DataRequired()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )