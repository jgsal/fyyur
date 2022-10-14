#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
# Import additions
from config import *
import collections
import collections.abc
collections.Callable = collections.abc.Callable
from flask_migrate import Migrate
import sys
# from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
# import only works after initializing db - flask won't detect models if this is in the import section.
from models import db, Venue, Artist, Show
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

#  ----------------------------------------------------------------#
#  Venues.
#  ----------------------------------------------------------------#

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    city_state = Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.state, Venue.city).all()
    current_date = datetime.now()
    data = []

    # Loop city and state for distinct city state dictionary, in desc order due to query
    for place in city_state:
        city_state_dict = {
            "city": place.city,
            "state": place.state       
        }
        # for each distinct city state, query venue list
        venues = Venue.query.filter_by(city=place.city, state=place.state).all()

        # Nested for. Create venue list for each city state.
        venue_list = []
        for venue in venues:
            venue_list.append({
                "id": venue.id,
                "name": venue.name,
                #lambda=anonymous function, returns single expression. Looping through and listing shows with future date; count items.
                "num_upcoming_shows": len(list(filter(lambda n: n.start_time > current_date, venue.shows)))
            })

        # Add venue key to city state dict. Each city state as key with venue list associated.
        city_state_dict["venues"] = venue_list
        # Append dictionary to list
        data.append(city_state_dict)
        
    return render_template('pages/venues.html', areas=data)

#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # strip removes trailing or leading spaces
    appsearch = request.form.get('search_term').strip()
    # Queryable Attribute, ilike insensitive, like sensitive. Creating wild card string with format to query matches.
    querymatches = Venue.query.filter(Venue.name.ilike('%{}%'.format(appsearch))).order_by(Venue.name).all()

    results = {}
    current_date = datetime.now()
    data = []

    # Append each venue match to data list
    for venue in querymatches:

        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(list(filter(lambda n: n.start_time > current_date, venue.shows)))  # added to search_venues.html
        })
        # print(data)

        # Add result count key and data key with venue match list to result dictionary
        results['count'] = len(querymatches)
        results['data'] = data
        # print(results)

    return render_template('pages/search_venues.html', results=results, search_term=appsearch)

#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # TODO: replace with real venue data from the venues table, using venue_id
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    current_date = datetime.now()

    # Create upcoming show list
    for show in shows:
        if show.start_time > current_date:
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

        #create past show list
        if show.start_time < current_date:
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    # Venue data (dict)
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
        "past_shows_count": len(past_shows),  # count list items
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows) # count list items
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form) # request.form

    if form.validate(): # Check values against form validations
        try:
            # Variable of Class with column data from form
            newvenue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres = form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                website=form.website_link.data
            )
            # on successful db insert, flash success
            db.session.add(newvenue)
            db.session.commit()
            flash('Venue, ' + newvenue.name + ', was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue, ' + newvenue.name + ', could not be listed!')
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Venue, ' + form.name.data + ', could not be listed!  Error(s):  '+result)

    return render_template('pages/home.html')

#  ---------------End Create Venue-------------------------------------------

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    try:
        # Get Venue, set name variable
        venue = Venue.query.get_or_404(venue_id)
        venue_name = venue.name

        # Delete, Commit
        db.session.delete(venue)
        db.session.commit()

        # Success flash
        flash('Venue ' + venue_name + ' was deleted, including all of their shows.')
        return render_template('pages/home.html')
    except ValueError:
        db.session.rollback()
        flash(' An error occured and Venue ' + venue_name + ' was not deleted')
    finally:
        db.session.close()

    return redirect(url_for('venues'))

#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
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

#  ----------------------------------------------------------------

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
            flash('Venue, ' + venue.name + ', was successfully updated!')
        except Exception as error:
            db.session.rollback()
            flash('An error occured and venue, ' + venue.name + ', was not updated.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occured and venue, ' + venue.name + ', was not updated. Error(s): '+ result)
        print(sys.exc_info())

    return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------#
#  Artists
#  ----------------------------------------------------------------#

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artist = Artist.query.order_by(Artist.name).all()
    current_date = datetime.now()
    data = []

    for artist in artist:
        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(list(filter(lambda n: n.start_time > current_date, artist.shows))) # added to search_artist.html
        })

    return render_template('pages/artists.html', artists=data)

#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # strip removes trailing or leading spaces
    appsearch = request.form.get('search_term').strip()
    # Queryable Attribute, ilike insensitive, like sensitive. Formatting appsearch.
    querymatches = Artist.query.filter(Artist.name.ilike('%{}%'.format(appsearch))).order_by(Artist.name).all()

    response = {}
    current_date = datetime.now()
    data = []

    for artist in querymatches:

        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(list(filter(lambda n: n.start_time > current_date, artist.shows))) # added to search_artist.html
        })
        # print(data)

        response['count'] = len(querymatches)
        response['data'] = data

    return render_template('pages/search_artists.html', results=response, search_term=appsearch)

#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    current_date = datetime.now()

    for show in shows:
        if show.start_time > current_date:
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

        if show.start_time < current_date:
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

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
        "past_shows_count": len(past_shows), # count list items
        "upcoming_shows_count": len(upcoming_shows) # count list items
    }

    return render_template('pages/show_artist.html', artist=data)

#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
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

#  ----------------------------------------------------------------

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
            flash('Artist, ' + artist.name + ', was successfully updated!')
            print(sys.exc_info())
        except Exception as error:
            db.session.rollback()
            flash('An error occured and artist, ' + artist.name + ', was not updated.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occured and artist, ' + artist.name + ', was not updated. Error(s): '+ result)
        print(sys.exc_info())

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():  # from template
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    if form.validate():
        try:
            newartist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres = form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(newartist)
            db.session.commit()
            # on successful db insert, flash success (from template)
            flash('Artist, ' + newartist.name + ', was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist, ' + newartist.name + ', could not be listed.')
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Artist, ' + form.name.data + ', could not be listed. Error(s): '+ result)

    return render_template('pages/home.html')  # from template

#  ----------End Create Artist------------------------------------------

@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
# @app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
# consistency
    try:
        # Get venue by ID
        artist = Artist.query.get_or_404(artist_id)
        artist_name = artist.name

        db.session.delete(artist)
        db.session.commit()

        flash('Artist, ' + artist_name + ', was deleted, including all of their shows.')
        return render_template('pages/home.html')
    except ValueError:
        flash(' An error occured and Artist, ' + artist_name + ', was not deleted')
        db.session.rollback()
        # current_session.rollback()
    finally:
        db.session.close()
        # current_session.close()

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

#  Create Shows
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

#  ----------------------------------------------------------------

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    if form.validate():
        try:
            newshow = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
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
            flash('Show could not be added. Check Artist/Venue IDs')
        finally:
            db.session.close()
    else:
        result = json.dumps(form.errors)
        flash('An error occurred. Show could not be added. Error(s): '+ result)
        print(sys.exc_info())

    return render_template('pages/home.html')
#  ------------------End Show Create-------------------------------

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

# resolved sqlalchemy/postgresql timeout error
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

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
