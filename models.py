#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'  # ---Changed from shows --#

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id} Artist {self.artist_id}, Venue {self.venue_id}>'

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))  # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'