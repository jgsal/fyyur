#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# Import additions
from flask_migrate import Migrate
import sys
import config
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Import database models with app context
with app.app_context():
  from models import *

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home Page

@app.route('/')
def index():
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Venues.
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    results = Venue.query.distinct(Venue.city, Venue.state).all()
    for result in results:
        city_state_unit = {
            "city": result.city,
            "state": result.state
        }
        venues = Venue.query.filter_by(city=result.city, state=result.state).all()

        # format each venue
        formatted_venues = []
        for venue in venues:
            formatted_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })

        city_state_unit["venues"] = formatted_venues
        data.append(city_state_unit)

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    appSearch = request.form.get('search_term').strip()
    stringMatches = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(appSearch))).all()

    response = {}
    current_date = datetime.now()
    data = []

    for venue in stringMatches:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming_shows = 0

        for show in venue_shows:
            if show.start_time > current_date:
                num_upcoming_shows += 1

        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_upcoming_shows  # added to search_venues.html
        })
        print(data)

        response = {}
        response['count'] = len(stringMatches)
        response['data'] = data
        print(response)

    return render_template('pages/search_venues.html', results=response, search_term=appSearch)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # TODO: replace with real venue data from the venues table, using venue_id
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    # print(venue)
    if not venue:
        # Redirect home
        return redirect(url_for('index'))
    else:
        # add genre

        # List and count shows
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        now = datetime.now()
        for show in venue.shows:
            if show.start_time > now:
                upcoming_shows_count += 1
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
            if show.start_time < now:
                past_shows_count += 1
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })

        data = {
            "id": venue_id,
            "name": venue.name,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "genres": venue.genres,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count
        }

    return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)

    if form.validate():
        try:
            newvenue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres = form.genres.data,
                #genres=",".join(form.genres.data),  # convert genre array to string separated with commas ##!! Error, every letter is separated by commas
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                website=form.website_link.data
            )
            # on successful db insert, flash success
            db.session.add(newvenue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed!')
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed!  Error(s):  '+result)

    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

  try:
    # Get venue by ID
    venue = Venue.query.get_or_404(venue_id)
    venue_name = venue.name

    db.session.delete(venue)
    db.session.commit()

    flash('Venue ' + venue_name + ' was deleted, including all of their shows.')
    return render_template('pages/home.html')
  except ValueError:
    flash(' An error occured and Venue ' + venue_name + ' was not deleted')
  finally:
    db.session.close()

  return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data =venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website_link.data
            venue.image_link = form.image_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.commit()
            flash('Venue, ' + request.form['name'] + ', was successfully updated!')
        except Exception as error:
            flash('An error occured and venue, ' + request.form['name'] + ', was not edit.')
            print(sys.exc_info())
    else:
        result = json.dumps(form.errors)
        flash('An error occured and venue, ' + request.form['name'] + ', was not edit. Error(s): '+ result)
        print(sys.exc_info())

    return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = db.session.query(Artist.id, Artist.name).all()
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    appSearch = request.form.get('search_term')
    stringMatches = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(appSearch))).all()

    response = {}
    response['count'] = len(stringMatches)
    response['data'] = stringMatches

    return render_template('pages/search_artists.html', results=response, search_term=appSearch)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    artist.genres = artist.genres.split(',')

    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows:
        data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": artist.genres,
        "image_link": artist.image_link,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.image_link.data = artist.image_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)

    artist = Artist.query.get(artist_id)
    if form.validate():
        try:
                artist.name = form.name.data
                artist.city = form.city.data
                artist.state = form.state.data
                artist.phone = form.phone.data
                artist.genres = form.genres.data
                artist.facebook_link = form.facebook_link.data
                artist.website = form.website_link.data
                artist.image_link = form.image_link.data
                artist.seeking_venue = form.seeking_venue.data
                artist.seeking_description = form.seeking_description.data

                db.session.commit()
                flash('Artist, ' + form.name.data + ', was successfully updated!')
        except Exception as error:
            flash('An error occurred. Artist, ' + form.name.data + ', could not be updated.')
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Artist, ' + request.form['name'] + ', could not be edited. Error(s): '+ result)
        print(sys.exc_info())

    return redirect(url_for('show_artist', artist_id=artist_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():  # from template
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    
    form = ArtistForm(request.form)  # request.form

    if form.validate():
        try:
            newartist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                genres=",".join(form.genres.data), # converts genre array to string separated with commas
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(newartist)
            db.session.commit()
            # on successful db insert, flash success (from template)
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        except Exception:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. Error(s): '+ result)
        print(sys.exc_info())

    return render_template('pages/home.html')  # from template

@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
# @app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get_or_404(artist_id)
    artist_name = artist.name

    artdel_session = db.object_session(artist)
    artdel_session.delete(artist)
    artdel_session.commit()
    # db.session.delete(artist)
    # db.session.commit()

    flash('Artist ' + artist_name + ' was deleted, including all of their shows.')
    return render_template('pages/home.html')
  except ValueError:
    flash(' An error occured and Artist ' + artist_name + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('artists'))

#  ----------------------------------------------------------------#
#  Shows
#  ----------------------------------------------------------------#

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    return render_template('pages/shows.html', shows=data)

#  ----------------------------------------------------------------
#  Create Shows
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    if form.validate():
        try:
            newshow = Show(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data
            )

            db.session.add(newshow)
            db.session.commit()

            # on successful db insert, flash success
            flash('Show was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except Exception:
            db.session.rollback()
            result = json.dumps(form.errors)
            flash('Show could not be added.Error(s): '+ result)
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Show could not be added. Error(s): '+ result)
        print(sys.exc_info())

    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Error Handling
#  ----------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''