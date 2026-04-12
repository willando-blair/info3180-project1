"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

from app import app, db
from flask import render_template, request, redirect, url_for, flash
from .forms import PropertyForm
from .models import Property
from datetime import datetime
import os
from werkzeug.utils import secure_filename, send_from_directory


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Willando Blair")

@app.route('/properties/create/', methods=['GET', 'POST'])
def properties_create():
    """Render the website's add properties page."""
    form = PropertyForm()

    if form.validate_on_submit():
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        photo.save(os.path.join(os.getcwd(), 'app/static/uploads/', filename))

        """Create property"""
        new_property = Property(
            title=form.title.data,
            description=form.description.data,
            rooms=form.rooms.data,
            bathrooms=form.bathrooms.data,
            price=form.price.data,
            type=form.type.data,
            location=form.location.data,
            photo_filename=filename,
            created_at=datetime.now()
        )

        db.session.add(new_property)
        db.session.commit()

        flash('Property added successfully!', 'success')
        return redirect(url_for('properties'))
    return render_template('new_property.html', form=form)

@app.route('/properties/')
def properties():
    """Renders the view properties page"""
    all_properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('properties.html', properties=all_properties)

@app.route('/properties/<property_id>/')
def view_property(property_id):
    """Renders the view single property page"""
    active_property = Property.query.filter_by(id=property_id).first()
    return render_template('property.html', property=active_property)

###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
