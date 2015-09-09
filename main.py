# --------------------------------------------------
#   APP     UniVerse v0.0.1
#   AUTHOR  David Leger
#   DATE    August, 2015 
# --------------------------------------------------

import os

# import Flask dependancies
from flask import Flask, render_template, flash, request, url_for, redirect, session

# import other dependancies
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as sanitize

from werkzeug import secure_filename
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

#import custom scripts
from db_connect import connection

app = Flask(__name__)
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
#   SECTION Define Routes & Templates
# --------------------------------------------------

# HOME
@app.route('/')
def home():
    try:
        title = "Home"
        return render_template("pages/home.html", title = title)
    
    except Exception as e:
        #flash(e)
        return str(e)

@app.route('/search/', methods = ['GET', 'POST'])
def search():
    try:
        title = "Search"
        search = request.args.get('search')
        query = "%" + request.args.get('search') + "%"
        # Establish connection
        c, conn = connection()
        
        result = c.execute("SELECT t.track_id, t.title,  FROM tracks t JOIN WHERE (t.title LIKE (%s) OR t.lyrics LIKE (%s))", [sanitize(query), sanitize(query)])
        songResults = c.fetchall()
        
        result = c.execute("SELECT * FROM albums WHERE (title LIKE (%s) OR genre LIKE (%s))", [sanitize(query), sanitize(query)])
        albumResults = c.fetchall()
        
        result = c.execute("SELECT * FROM artists WHERE (name LIKE (%s) OR genre LIKE (%s) OR country LIKE (%s))", [sanitize(query), sanitize(query), sanitize(query)])
        artistResults = c.fetchall()
        
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        #flash(data)
        
        songs = []
        albums = []
        artists = []
        
        for song in songResults:
            songs.append({'id': song[0], 'album_id': song[1], 'track_number': song[2], 'title': song[3], 'lyrics': song[4], 'media_link': song[5]})
            
        for album in albumResults:
            albums.append({'id': album[0], 'artist_id': album[1], 'title': album[2], 'genre': album[3], 'year': album[4], 'artwork': song[5]})
            
        for artist in artistResults:
            artists.append({'id': artist[0], 'biography': artist[1], 'name': artist[2], 'genre': artist[3], 'country': artist[4], 'year': artist[5]})
        
        #TODO search albums
        
        #TODO search artists
        
        return render_template("pages/search.html", title = title, search = search, songs = songs, albums = albums, artists = artists)
    except Exception as e:
        #flash(e)
        return str(e)

# --------------------------------------------------


# --------------------------------------------------
#   USER AUTHENTICATION
# --------------------------------------------------

# LOGIN
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    
    #error = "Hey"
    title = "Login"
    request.form.email = "test"
    try:
        if request.method == "POST":
            attempted_username = request.form['email']
            attempted_password = request.form['password']
            
            flash(attempted_username)
            flash(attempted_password)
            
            #TODO check username and password with db; set session vars
            c, conn = connection()
            res = c.execute("SELECT * FROM users WHERE username = (%s)", [sanitize(attempted_username)])
            data = c.fetchone()
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            
            if int(res) > 0:
                db_password = data[2]
                if sha256_crypt.verify(attempted_password, db_password):
                    session['logged_in'] = True
                    session['user_id'] = data[0]
                    session['username'] = data[1]
                    session['user_email'] = data[3]
                    session['user_type'] = data[4]
                    session['user_fname'] = data[5]
                    session['user_lname'] = data[6]
                    session['user_active'] = data[7]
                    session['user_image'] = data[8]
                    flash(data)
                    return redirect(url_for('home'))
            
            flash("Username or password was incorrect. Please try again.")
            #TODO end --------------------------------------------------
            
        return render_template("pages/login.html", title=title)
         
        
    except Exception as e:
        flash(e)
        error = "Failed."
    
    return render_template("pages/login.html", title=title, error = error)

# --------------------------------------------------

# LOGOUT
@app.route('/logout/')
def logout():
    
    session.clear()
    
    return redirect(url_for('login'))

# --------------------------------------------------

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
    title = "Sign Up"
    try:
        
        if request.method == "POST":
            
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['repeatpassword']
            
            flash(username)
            flash(password)
            
            # confirm password
            if password != password2:
                flash("Passwords do not match.")
                return render_template('pages/signup.html', title = title)
            if len(password) < 8:
                flash("Password not long enough.")
                return render_template('pages/signup.html', title = title)
            password = sha256_crypt.encrypt(str(password))
            
            # Check if username is available
            c, conn = connection()
            db_username = c.execute("SELECT * FROM users WHERE username = (%s)", [sanitize(username)])
            if int(db_username) > 0:
                flash("Username taken.")
                return render_template('pages/signup.html', title = title)
            
            # Check if email is already used.
            db_email = c.execute("SELECT * FROM users WHERE email = (%s)", [sanitize(email)])
            if int(db_email) > 0:
                flash("An account already exists with that email.")
                return render_template('pages/signup.html', title = title)
            
            # Credentials are good! Add new user and close the connection.
            c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                     [sanitize(username), sanitize(password), sanitize(email)])
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()

            flash("You are now Registered!")

            session['logged_in'] = True
            session['user_id'] = 1
            session['username'] = username
            session['user_email'] = email
            session['user_type'] = 0
            session['user_active'] = 0
            session['user_image'] = 'placeholder.jpg'
            return redirect(url_for('home'))
                
        return render_template('pages/signup.html', title = title)
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
@app.route('/edit-song/', methods = ['GET', 'POST'])
def editSong():
    try:
        title = "Edit Song"
        if request.method == "POST":
            flash("one!")
            song = {}

            song['id'] = request.args.get('song')
            #song['album_id'] = data[1]
            song['track_number'] = request.form['track_number']
            song['title'] = request.form['title'].encode('utf-8')
            song['lyrics'] = request.form['lyrics'].encode('utf-8')
            song['media_link'] = request.form['media_link']
            
            title = song['title']
            flash("two!")
            c, conn = connection()
            c.execute("UPDATE tracks SET title = (%s), track_no = (%s), lyrics = (%s), media_link = (%s) WHERE track_id = (%s)", [sanitize(song['title']), sanitize(song['track_number']), song['lyrics'], sanitize(song['media_link']),sanitize(song['id'])])
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Updated!")
            
            return redirect('/song/?song=' + str(song['id']))
        
        elif request.method == "GET":
            
            track_id = request.args.get('song')
            # Establish connection
            c, conn = connection()

            result = c.execute("SELECT * FROM tracks WHERE track_id = (%s)", [sanitize(track_id)])
            data = c.fetchone()
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            
            song = {}
            
            song['id'] = data[0]
            song['album_id'] = data[1]
            song['track_number'] = data[2]
            song['title'] = data[3].decode('utf-8')
            song['lyrics'] = data[4].decode('utf-8')
            song['media_link'] = data[5]
        
        return render_template('pages/edit-song.html', title = title, song = song)
    except Exception as e:
        flash(e)
        return(str(e))
    
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
def addSong():
    try:
        title = "Edit Song"
        song = {}
        if request.method == "POST":
            

            song['album_id'] = request.args.get('album')
            #song['album_id'] = data[1]
            song['track_number'] = request.form['track_number']
            song['title'] = request.form['title'].encode('utf-8')
            song['lyrics'] = request.form['lyrics'].encode('utf-8')
            song['media_link'] = request.form['media_link']
            
            title = song['title']
            flash("two!")
            c, conn = connection()
            c.execute("INSERT INTO tracks (album_id, track_no, title, lyrics, media_link) VALUES (%s, %s, %s, %s, %s);", [sanitize(song['album_id']), sanitize(song['track_number']), sanitize(song['title']), song['lyrics'], sanitize(song['media_link'])])
            c.execute("SELECT LAST_INSERT_ID();")
            data = c.fetchone()
            # Close Connection
            conn.commit()
            c.close()
            conn.close()
            #gc.collect()
            flash("Saved!")
            flash(data)
            return redirect('/song/?song=' + str(data[0]))
        
        return render_template('pages/edit-song.html', title = title, song = song)
    except Exception as e:
        flash(e)
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
#   VIEW CONTENT PAGES
# --------------------------------------------------

# VIEW SONG
@app.route('/song/', methods = ['GET', 'POST'])
def song():
    try:
         
        track_id = request.args.get('song')
        
        # Establish connection
        c, conn = connection()
        song = {}
        
        result = c.execute("SELECT * FROM tracks WHERE track_id = (%s)", [sanitize(track_id)])
        data = c.fetchone()
        flash("hi")
        song['id'] = data[0]
        song['album_id'] = data[1]
        song['track_number'] = data[2]
        song['title'] = data[3].decode('utf-8')
        song['lyrics'] = nl2br(data[4].decode('utf-8'))
        if data[5] != None and 'youtube' in data[5]:
            song['media_link'] = data[5].split("=")[1]
        else:
            song['media_link'] = ''
        result = c.execute("SELECT t.track_id, t.track_no, t.title, a.album_id, a.title, a.genre, a.year_released, a.artwork, ar.artist_id, ar.name FROM tracks T JOIN albums a ON t.album_id=a.album_id JOIN artists ar ON a.artist_id=ar.artist_id WHERE t.album_id=(%s) ORDER BY t.track_no", [song['album_id']])
        data = c.fetchall()
        
        album = {}
        
        album['id'] = data[0][3]
        album['title'] = data[0][4]
        album['artwork'] = data[0][7]
        album['genre'] = data[0][5]
        album['year'] = data[0][6]
        
        album['tracklist'] = {}
        album['tracklist']['tracks'] = []
        for track in data:
            album['tracklist']['tracks'].append({'title': track[2], 'track_no': track[1], 'id': track[0]})
            
        # Close Connection
        conn.commit()
        c.close()
        conn.close()
        #gc.collect()
        
        title = song['title']
        
        artist = {}
        artist['id'] = data[0][8]
        artist['name'] = data[0][9]
        
        return render_template('pages/song.html', title = title, song = song, album = album, artist = artist)
    except Exception as e:
        flash(e)
        return(str(e))
    
# --------------------------------------------------

# EDIT ARTIST
@app.route('/artist/', methods = ['GET', 'POST'])
def artist():
    try:
        
        artist_id = request.args.get('artist')
        
        # Establish connection
        c, conn = connection()
        
        
        result = c.execute("SELECT * FROM artists WHERE artist_id = (%s)", [sanitize(artist_id)])
        data = c.fetchone()
        
        artist = {}
        artist['id'] = data[0]
        artist['name'] = data[2]
        artist['bio'] = nl2br(data[1].decode('utf-8'))
        artist['genre'] = data[3]
        artist['country'] = data[4]
        artist['year'] = data[5]
        title = artist['name']
        result = c.execute("SELECT name, role FROM members WHERE artist_id = (%s)", [sanitize(artist_id)])
        data = c.fetchall()
        
        members = []
        for member in data:
            members.append({'name': member[0], 'role': member[1]})
        
        result = c.execute("SELECT * FROM albums WHERE artist_id = (%s) ORDER BY year_released DESC;", [artist['id']])
        data = c.fetchall()
        
        albums = []
        for album in data:
            result = c.execute("SELECT track_id, title, track_no FROM tracks WHERE album_id = (%s) ORDER BY track_no;", [album[0]])
            data2 = c.fetchall()
            tracklist = []
            for track in data2:
                tracklist.append({'id': track[0], 'title': track[1], 'track_no': track[2]})
            albums.append({'id': album[0], 'title': album[2], 'genre': album[3], 'year': album[4], 'artwork': album[5], 'tracklist': tracklist})
        return render_template('pages/artist.html', title = title, artist = artist, members = members, albums = albums)
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