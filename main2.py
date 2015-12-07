# --------------------------------------------------
#   APP     UniVerse v0.0.1
#   AUTHOR  David Leger
#   DATE    August, 2015 
# --------------------------------------------------

import os

# import Flask dependancies
from flask import Flask, render_template, flash, request, url_for, redirect, session, jsonify
import json
# import other dependancies
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as sanitize
from flask.ext.cors import CORS

from werkzeug import secure_filename
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

#import custom scripts
from db_connect2 import connection

app = Flask(__name__)
CORS(app, resorces={r'/d/*': {"origins": '*'}})
app.secret_key = 'aqwsedrftgyhujikolp1654as'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def nl2br(string, is_xhtml= True ):
    if is_xhtml:
        return string.replace('\n','<br />\n')
    else :
        return string.replace('\n','<br>\n')

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# --------------------------------------------------
#   SECTION Define Routes
# --------------------------------------------------


@app.route('/search/<search>/', methods = ['GET', 'POST'])
def search(search):
    
    try:
        title = "Search"
        query = "%" + search + "%"
        
        # Establish connection
        c, conn = connection()
        
        result = c.execute("SELECT t.track_id, t.title, a.album_id, a.title, a.artwork, ar.artist_id, ar.name  FROM tracks t, albums a, artists ar WHERE (t.title LIKE (%s) OR t.lyrics LIKE (%s)) AND t.album_id = a.album_id AND a.artist_id = ar.artist_id ORDER BY t.title;", [sanitize(query), sanitize(query)])
        songResults = c.fetchall()
        
        result = c.execute("SELECT a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM albums a, artists ar WHERE (a.title LIKE (%s) OR a.genre LIKE (%s) OR a.year_released LIKE (%s)) AND a.artist_id = ar.artist_id;", [sanitize(query), sanitize(query), sanitize(query)])
        albumResults = c.fetchall()
        
        result = c.execute("SELECT ar.artist_id, ar.name, ar.genre, ar.country, a.artwork FROM artists ar LEFT JOIN albums a ON a.artist_id = ar.artist_id WHERE (name LIKE (%s) OR ar.genre LIKE (%s) OR country LIKE (%s)) GROUP BY ar.artist_id;", [sanitize(query), sanitize(query), sanitize(query)])
        artistResults = c.fetchall()
        
        conn.commit()
        c.close()
        conn.close()
        
        return jsonify({ "tracks": songResults, "albums": albumResults, "artists": artistResults })
        #return render_template("pages/search.html", title = title, search = search, songs = songs, albums = albums, artists = artists)
    except Exception as e:
        #flash(e)
        return str(e)

# --------------------------------------------------


# --------------------------------------------------
#   USER AUTHENTICATION
# --------------------------------------------------

def userAuth(attempted_username, attempted_password):
    try:
        #check username and password with db
        c, conn = connection()
        res = c.execute("SELECT * FROM users WHERE username = (%s)", [attempted_username] )
        user = c.fetchone()
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        
        if int(res) > 0:
            db_password = user['password']
            if sha256_crypt.verify(attempted_password, db_password):
                id = user['user_id']
                user['user_id'] = int(id)
                user['password'] = attempted_password
                user['logged_in'] = True
                
                return user
            return False
        else:
            return False
    except Exception as e:
        return False

# LOGIN
@app.route('/login/', methods = ['POST'])
def login():
    #return jsonify({ "userdata": False })
    data = request.get_json(force=True)
    usernameIn = data['username']
    passwordIn = data['password']
    user = userAuth(usernameIn, passwordIn)
    return jsonify({ "userdata": user})

# --------------------------------------------------


@app.route('/register/', methods = ['PUT'])
def signup():
    title = "Sign Up"
    data = request.get_json(force=True)
    email = data['email']
    username = data['username']
    password = data['password']
    password2 = data['confirmPassword']
            
    #return jsonify({ "userdata": email })
    
    try:
        password = sha256_crypt.encrypt(str(password))

        # Check if username is available
        c, conn = connection()
        db_username = c.execute("SELECT * FROM users WHERE username = (%s)", [sanitize(username)])
        if int(db_username) > 0:
            return jsonify({ "userdata": False, "error": "Username Taken." })

        # Check if email is already used.
        db_email = c.execute("SELECT * FROM users WHERE email = (%s)", [sanitize(email)])
        if int(db_email) > 0:
            return jsonify({ "userdata": False, "error": "Email already used by another account." })

        # Credentials are good! Add new user and close the connection.
        c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                 [sanitize(username), sanitize(password), sanitize(email)])
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()

        return jsonify({ "userdata": True, "message": "You are now registered!" })
                
    except Exception as e:
        flash(e)
        return(str(e))

# --------------------------------------------------

@app.route('/settings/', methods = ['GET', 'POST'])
def settings():
    
    title = "Settings"
    try:
        if request.method == "POST":
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['repeatpassword']
            
            # Establish connection
            c, conn = connection()
            
            file = request.files['image']
            if file and allowed_file(file.filename):
                image = secure_filename("user_img" + str(session['user_id']) + "." + file.filename.rsplit('.', 1)[1])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                c.execute("UPDATE users SET image_url = (%s) WHERE user_id = (%s)", [sanitize(image), session['user_id']])
                session['user_image'] = image
            
            # ------------------------------
            #   New Username
            # ------------------------------
            if username != session['username']:
                db_username = c.execute("SELECT username FROM users WHERE username = (%s) AND user_id != (%s)", [sanitize(username), session['user_id']])
                if int(db_username) > 0:
                    flash("Username taken.")
                    #return render_template('pages/settings.html', title = title)
                else:
                    c.execute("UPDATE users SET username = (%s) WHERE user_id = (%s)", [sanitize(username), session['user_id']])
                    #conn.commit()
                    session['username'] = username
                    flash("Username successfully changed!")
            
            # ------------------------------
            #   New Email Address
            # ------------------------------
            if email != session['user_email']:
                # Check if email is already used.
                db_email = c.execute("SELECT email FROM users WHERE email = (%s) AND user_id != (%s)", [sanitize(email), session['user_id']])
                if int(db_email) > 0:
                    flash("An account already exists with that email.")
                    #return render_template('pages/settings.html', title = title)
                else:
                    c.execute("UPDATE users SET email = (%s) WHERE user_id = (%s)", [sanitize(email), session['user_id']])
                    session['user_email'] = email
                    flash("Email successfully changed!")
            
            # ------------------------------
            #   New Password
            # ------------------------------
            if len(password) > 0:
                 # confirm password
                if password != password2:
                    flash("Passwords do not match.")
                    #return render_template('pages/signup.html', title = title)
                elif len(password) < 8:
                    flash("Password not long enough.")
                    #return render_template('pages/signup.html', title = title)
                else:
                    password = sha256_crypt.encrypt(str(password))
                    c.execute("UPDATE users SET password = (%s) WHERE user_id = (%s)", [sanitize(password), session['user_id']])
                    flash("Password successfully changed!")
            
            # ------------------------------
            
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()

        return render_template('pages/settings.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
# --------------------------------------------------

# --------------------------------------------------
#   EDIT CONTENT PAGES
# --------------------------------------------------

# EDIT SONG
@app.route('/<int:artist_id>/<int:album_id>/<int:track_id>/', methods = ['POST'])
def editSong(artist_id, album_id, track_id):
    
    data = request.get_json(force=True)
    
    if userAuth(data['username'], data['password']) == False:
        print "sup"
        return jsonify({'error': True, 'message': 'You are not logged in!'} )
       
    try:
        song = {}
        song['id'] = str(track_id)
        #song['album_id'] = data[1]
        song['track_number'] = str(data['track_number'])
        song['title'] = data['title'].encode('utf-8')
        song['lyrics'] = data['lyrics'].encode('utf-8')
        song['media_link'] = data['media_link'].encode('utf-8')
        
        c, conn = connection()
        c.execute("UPDATE tracks SET title = (%s), track_no = (%s), lyrics = (%s), media_link = (%s) WHERE track_id = (%s);", [sanitize(song['title']), sanitize(song['track_number']), song['lyrics'], sanitize(song['media_link']),sanitize(song['id'])])
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        
        return jsonify({'error': False, 'message': 'Save successful!'} )

    except Exception as e:
        print "err: " + str(e)
        return jsonify({'error': True, 'message': 'Something went wrong... Content may not have saved.'} )
    
# --------------------------------------------------

# ADD SONG
@app.route('/<int:artist_id>/<int:album_id>/', methods = ['PUT'])
def addSong(artist_id, album_id):
    
    data = request.get_json(force=True)
    
    if userAuth(data['username'], data['password']) == False:
        print "sup"
        return jsonify({'error': True, 'message': 'You are not logged in!'} )
       
    try:
        song = {}
        song['album_id'] = str(album_id)
        #song['album_id'] = data[1]
        song['track_number'] = str(data['track_number'])
        song['title'] = data['title'].encode('utf-8')
        song['lyrics'] = data['lyrics'].encode('utf-8')
        song['media_link'] = data['media_link'].encode('utf-8')
        
        c, conn = connection()
        c.execute("INSERT INTO tracks (album_id, track_no, title, lyrics, media_link) VALUES (%s, %s, %s, %s, %s);", [sanitize(song['album_id']), sanitize(song['track_number']), sanitize(song['title']), song['lyrics'], sanitize(song['media_link'])])
        c.execute("SELECT LAST_INSERT_ID();")
        data = c.fetchone()
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        print data
        return jsonify({"error": False, "message": "Song added!", "track_id": data['LAST_INSERT_ID()']})

    except Exception as e:
        print "err: " + str(e)
        return jsonify({'error': True, 'message': 'Something went wrong... Content may not have saved.'} )
    
# --------------------------------------------------

# EDIT ALBUM
@app.route('/edit-album/', methods = ['GET', 'POST'])
def editAlbum():
    try:
        title = "Edit Album"
        if request.method == "POST":
            
            album = {}

            album['id'] = request.args.get('album')
            album['artist'] = request.args.get('artist')
            album['title'] = request.form['title']
            #album['artwork'] = request.form['artwork']
            album['genre'] = request.form['genre']
            album['year'] = request.form['year']
            title = album['title']
            
            c, conn = connection()
            
            file = request.files['artwork']
            if file and allowed_file(file.filename):
                image = secure_filename("album_img" + str(album['id']) + "." + file.filename.rsplit('.', 1)[1])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                c.execute("UPDATE albums SET artwork = (%s) WHERE album_id = (%s)", [sanitize(image), sanitize(album['id'])])
            
            c.execute("UPDATE albums SET title = (%s), genre = (%s), year_released = (%s) WHERE album_id = (%s)", [sanitize(album['title']), sanitize(album['genre']), sanitize(album['year']), sanitize(album['id'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            return redirect('/artist/?artist=' + str(album['artist']) + "#album" + str(album['id']))
        elif request.method == "GET":
            album_id = request.args.get('album')
            
            # Establish connection
            c, conn = connection()
            
            result = c.execute("SELECT a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM albums a JOIN artists ar ON a.artist_id=ar.artist_id WHERE a.album_id=(%s)", [sanitize(album_id)])
            data = c.fetchone()
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            
            album = {}

            album['id'] = data[0]
            album['title'] = data[1]
            album['artwork'] = data[4]
            album['genre'] = data[2]
            album['year'] = data[3]
            
            artist = {}
            artist['id'] = data[5]
            artist['name'] = data[6]
            
            title = album['title']
           
            # ------------------------------
            
            return render_template('pages/edit-album.html', title = title, album=album, artist = artist)
        else:
            return render_template('err/404.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# EDIT ARTIST
@app.route('/edit-artist/', methods = ['GET', 'POST'])
def editArtist():
    try:
        if request.method == "POST":
            flash("POST")
            artist = {}
            artist['id'] = request.args.get('artist')
            artist['name'] = request.form['name']
            artist['bio'] = request.form['bio'].encode('utf-8')
            artist['genre'] = request.form['genre']
            artist['country'] = request.form['country']
            artist['year'] = request.form['year']
            title = artist['name']
            c, conn = connection()
            c.execute("UPDATE artists SET name = (%s), biography = (%s), genre = (%s), country = (%s), year_formed = (%s) WHERE artist_id = (%s)", [sanitize(artist['name']), artist['bio'], sanitize(artist['genre']), sanitize(artist['country']),sanitize(artist['year']), sanitize(artist['id'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            return redirect('/artist/?artist=' + str(artist['id']))
        elif request.method == "GET":
            artist_id = request.args.get('artist')
            
            # Establish connection
            c, conn = connection()
            
            
            result = c.execute("SELECT * FROM artists WHERE artist_id = (%s)", [sanitize(artist_id)])
            data = c.fetchone()
            
            artist = {}
            artist['id'] = data[0]
            artist['name'] = data[2]
            artist['bio'] = data[1].decode('utf-8')
            artist['genre'] = data[3]
            artist['country'] = data[4]
            artist['year'] = data[5]
            title = artist['name']
            result = c.execute("SELECT member_id, name, role FROM members WHERE artist_id = (%s)", [sanitize(artist_id)])
            data = c.fetchall()
            members = []
            for member in data:
                members.append({'id': member[0], 'name': member[1], 'role': member[2]})
            
            # ------------------------------
           
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            
            #title = "Edit Artist"
            
            return render_template('pages/edit-artist.html', title = title, artist = artist, members = members)
        else:
            return render_template('err/404.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------


# --------------------------------------------------
#   ADD CONTENT PAGES
# --------------------------------------------------

# ADD SONG
@app.route('/add-song/', methods = ['GET', 'POST'])
def addSong2():
    data = request.get_json(force=True)
    
    if userAuth(data['username'], data['password']) == False:
        print "sup"
        return jsonify({'error': True, 'message': 'You are not logged in!'} )
       
    try:
        song = {}
        song['album_id'] = str(data['album_id'])
        song['track_number'] = str(data['track_number'])
        song['title'] = data['title'].encode('utf-8')
        song['lyrics'] = data['lyrics'].encode('utf-8')
        song['media_link'] = data['media_link'].encode('utf-8')
        
        c, conn = connection()
        c.execute("INSERT INTO tracks (album_id, track_no, title, lyrics, media_link) VALUES (%s, %s, %s, %s, %s);", [sanitize(song['album_id']), sanitize(song['track_number']), sanitize(song['title']), song['lyrics'], sanitize(song['media_link'])])
        c.execute("SELECT LAST_INSERT_ID();")
        data = c.fetchone()
        # Close Connection
        conn.commit()
        c.close()
        conn.close()

        return jsonify({"error": False, "message": "Song added!"})
        
        return jsonify({"error": True, "message": "Something went wrong...", "track_id": data })
    except Exception as e:
        return(str(e))
    
# --------------------------------------------------

# EDIT ALBUM
@app.route('/add-album/', methods = ['GET', 'POST'])
def addAlbum():
    try:
        title = "Add Album"
        
        album = {}
        
        if request.method == "POST":
            
            

            album['id'] = request.args.get('artist')
            album['artist_id'] = request.args.get('artist')
            album['title'] = request.form['title']
            #album['artwork'] = request.form['artwork']
            album['genre'] = request.form['genre']
            album['year'] = request.form['year']
            
            file = request.files['artwork']
            
            title = album['title']
            
            c, conn = connection()
            
            
            
            if file and allowed_file(file.filename):
                image = secure_filename("album_img" + str(album['id']) + "." + file.filename.rsplit('.', 1)[1])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                c.execute("INSERT INTO albums ( artist_id, title, genre, year_released, artwork) VALUES(%s, %s, %s, %s, %s)", [sanitize(album['artist_id']), sanitize(album['title']), sanitize(album['genre']), sanitize(album['year']), sanitize(image)])
            else:
                c.execute("INSERT INTO albums ( artist_id, title, genre, year_released) VALUES(%s, %s, %s, %s)", [sanitize(album['artist_id']), sanitize(album['title']), sanitize(album['genre']), sanitize(album['year'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            return redirect('/artist/?artist=' + str(album['artist_id']) + "#album" + str(album['id']))
        elif request.method == "GET":
            title = "Add Album"
            album = {}
            artist = {}
           
            # ------------------------------
            
            return render_template('pages/edit-album.html', title = title, album = album, artist = artist)
        else:
            return render_template('err/404.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# EDIT ARTIST
@app.route('/add-artist/', methods = ['GET', 'POST'])
def addArtist():
    try:
        if request.method == "POST":
            artist = {}
            artist['id'] = request.args.get('artist')
            artist['name'] = request.form['name']
            artist['bio'] = request.form['bio'].encode('utf-8')
            artist['genre'] = request.form['genre']
            artist['country'] = request.form['country']
            artist['year'] = request.form['year']
            title = artist['name']
            c, conn = connection()
            c.execute("UPDATE artists SET name = (%s), biography = (%s), genre = (%s), country = (%s), year_formed = (%s) WHERE artist_id = (%s)", [sanitize(artist['name']), artist['bio'], sanitize(artist['genre']), sanitize(artist['country']),sanitize(artist['year']), sanitize(artist['id'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            return redirect('/artist/?artist=' + str(artist['id']))
        elif request.method == "GET":
            artist_id = request.args.get('artist')
            
            # Establish connection
            c, conn = connection()
            
            
            result = c.execute("SELECT * FROM artists WHERE artist_id = (%s)", [sanitize(artist_id)])
            data = c.fetchone()
            
            artist = {}
            artist['id'] = data[0]
            artist['name'] = data[2]
            artist['bio'] = data[1].decode('utf-8')
            artist['genre'] = data[3]
            artist['country'] = data[4]
            artist['year'] = data[5]
            title = artist['name']
            result = c.execute("SELECT member_id, name, role FROM members WHERE artist_id = (%s)", [sanitize(artist_id)])
            data = c.fetchall()
            members = []
            for member in data:
                members.append({'id': member[0], 'name': member[1], 'role': member[2]})
            
            # ------------------------------
           
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            
            #title = "Edit Artist"
            
            return render_template('pages/edit-artist.html', title = title, artist = artist, members = members)
        else:
            return render_template('err/404.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------


# --------------------------------------------------
#   VIEW CONTENT PAGES
# --------------------------------------------------

# All Tracks
@app.route('/tracks/', methods = ['GET'])
def all_tracks():
    try:
        
        
        # Establish connection
        c, conn = connection()
        
        
        result = c.execute("SELECT * FROM tracks;")
        
        data = c.fetchall()
        for row in data:
            id = row['track_id']
            row['track_id'] = int(id)

        c.close()
        conn.close()
        return jsonify({'tracks': data})

    except:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# VIEW SONG
@app.route('/<int:artist_id>/<int:album_id>/<int:track_id>/', methods = ['GET'])
def song(artist_id, album_id, track_id):
    try:
         
        #track_id = request.args.get('song')
        
        # Establish connection
        c, conn = connection()
        #song = {}
        
        result = c.execute("SELECT * FROM tracks WHERE track_id = (%s)" % track_id)
        track = c.fetchone()
        
        #track = c.fetchone()
        id = track['track_id']
        track['track_id'] = int(id)
        
        
        
        result = c.execute("SELECT t.track_id, t.track_no, t.title, a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM tracks T JOIN albums a ON t.album_id=a.album_id JOIN artists ar ON a.artist_id=ar.artist_id WHERE t.album_id=(%s) ORDER BY t.track_no", [track['album_id']])
        album = c.fetchall()
        
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        track['album'] = album
        
        return jsonify({ 'track': track })
        
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# VIEW SONG
@app.route('/song/<int:track_id>/', methods = ['GET'])
def song2(track_id):
    
    try:
         
        #track_id = request.args.get('song')
        
        # Establish connection
        c, conn = connection()
        #song = {}
        
        result = c.execute("SELECT * FROM tracks WHERE track_id = (%s)" % track_id)
        track = c.fetchone()
        
        #track = c.fetchone()
        id = track['track_id']
        track['track_id'] = int(id)
        
        
        
        result = c.execute("SELECT t.track_id, t.track_no, t.title, a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM tracks T JOIN albums a ON t.album_id=a.album_id JOIN artists ar ON a.artist_id=ar.artist_id WHERE t.album_id=(%s) ORDER BY t.track_no", [track['album_id']])
        album = c.fetchall()
        
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        track['album'] = album
        
        return jsonify({ 'track': track })
        
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# All Albums
@app.route('/albums/', methods = ['GET'])
def all_albums():
    try:
        
        
        # Establish connection
        c, conn = connection()
        
        
        result = c.execute("SELECT * FROM albums;")
        
        data = c.fetchall()
        for row in data:
            id = row['album_id']
            row['album_id'] = int(id)

        c.close()
        conn.close()
        return jsonify({'albums': data})

    except:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# All Artists
@app.route('/artists/', methods = ['GET'])
def all_artists():
    try:
        
        # Establish connection
        c, conn = connection()
        
        
        result = c.execute("SELECT * FROM artists;")
        
        data = c.fetchall()
        for row in data:
            id = row['artist_id']
            row['artist_id'] = int(id)

        c.close()
        conn.close()
        return jsonify({'artists': data})

    except:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# Add an Artist
@app.route('/artists/', methods = ['POST'])
def add_artist():
    try:
        
        #DEVTIP change [] to ()
        artist = {}
        artist['id'] = request.json.get('artist')
        artist['name'] = request.json.get['name']
        artist['bio'] = request.json.get['bio'].encode('utf-8')
        artist['genre'] = request.json.get['genre']
        artist['country'] = request.json.get['country']
        artist['year'] = request.json.get['year']
        title = artist['name']
        c, conn = connection()
        c.execute("INSERT INTO artists (name, biography, genre, country, year_formed) VALUES(%s, %s, %s, %s, %s);", [sanitize(artist['name']), artist['bio'], sanitize(artist['genre']), sanitize(artist['country']),sanitize(artist['year']), sanitize(artist['id'])])
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        
        return make_response(jsonify( { 'error': 'success' } ), 201)

    
    except Exception as e:
        flash(e)
        return(str(e))
# --------------------------------------------------

# Get single Artist
@app.route('/<int:artist_id>/', methods = ['GET'])
def artist(artist_id):
    try:
        
        # Establish connection
        c, conn = connection()
        
        result = c.execute("SELECT * FROM artists WHERE artist_id = (%s);" % artist_id)
        
        artist = c.fetchone()
        id = artist['artist_id']
        artist['artist_id'] = int(id)

        result = c.execute("SELECT name, role FROM members WHERE artist_id = (%s)", [artist['artist_id']])
        members = c.fetchall()
        
        result = c.execute("SELECT * FROM albums WHERE artist_id = (%s) ORDER BY year_released DESC;", [artist_id])
        albums = c.fetchall()
        
        for album in albums:
            result = c.execute("SELECT track_id, title, track_no FROM tracks WHERE album_id = (%s) ORDER BY track_no;", [album['album_id']])
            tracklist = c.fetchall()
            album['tracklist'] = tracklist
        
        artist['members'] = members
        artist['albums'] = albums
        
        c.close()
        conn.close()
        
        return jsonify({'artist': artist})
    
    except:
        abort(404)
    
# --------------------------------------------------

# Add album to artist
@app.route('/<int:artist_id>/', methods = ['POST'])
def addAlbumToArtist(artist_id):
    try:
        title = "Add Album"
        
        album = {}
        
        if request.method == "POST":
            
            # TODO modify to recieve JSON data.
            album['title'] = request.form['title']
            #album['artwork'] = request.form['artwork']
            album['genre'] = request.form['genre']
            album['year'] = request.form['year']
            
            file = request.files['artwork']
            
            title = album['title']
            
            c, conn = connection()
            
            
            
            if file and allowed_file(file.filename):
                image = secure_filename("album_img" + str(album['id']) + "." + file.filename.rsplit('.', 1)[1])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                c.execute("INSERT INTO albums ( artist_id, title, genre, year_released, artwork) VALUES(%s, %s, %s, %s, %s)", [sanitize(album['artist_id']), sanitize(album['title']), sanitize(album['genre']), sanitize(album['year']), sanitize(image)])
            else:
                c.execute("INSERT INTO albums ( artist_id, title, genre, year_released) VALUES(%s, %s, %s, %s)", [sanitize(album['artist_id']), sanitize(album['title']), sanitize(album['genre']), sanitize(album['year'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            return redirect('/artist/?artist=' + str(album['artist_id']) + "#album" + str(album['id']))
        elif request.method == "GET":
            title = "Add Album"
            album = {}
            artist = {}
           
            # ------------------------------
            
            return render_template('pages/edit-album.html', title = title, album = album, artist = artist)
        else:
            return render_template('err/404.html', title = title)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# VIEW SONG
@app.route('/album/<int:album_id>/', methods = ['GET'])
def album(album_id):
    try:
         
        #track_id = request.args.get('song')
        
        # Establish connection
        c, conn = connection()
        #song = {}
       
        
        #track = c.fetchone()
        
        
        
        
        result = c.execute("SELECT a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM albums a JOIN artists ar ON a.artist_id=ar.artist_id WHERE a.album_id=(%s)", [album_id])
        album = c.fetchone()
        
        id = album['album_id']
        album['album_id'] = int(id)
        
        result = c.execute("SELECT track_id, title, track_no FROM tracks WHERE album_id = (%s) ORDER BY track_no;", [album['album_id']])
        tracklist = c.fetchall()
        album['tracklist'] = tracklist
        
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        
        return jsonify({ 'album': album })
        
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# --------------------------------------------------
#   ERROR HANDLING PAGES
# --------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("err/404.html")

@app.errorhandler(405)
def page_not_found(e):
    return render_template("err/405.html")

@app.errorhandler(500)
def page_not_found(e):
    flash(str(e))
    return render_template("err/500.html")

if __name__=="__main__":
    app.run()