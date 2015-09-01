# UniVerse Todo's

***

## Client-side Logic

 - \\jquery filter albums/songs [stakoverflow ](http://stackoverflow.com/questions/1772035/filtering-a-list-as-you-type-with-jquery)
 
 - login/register validation
   - email regex
   - password length/confirm
   - username length

- edit pages validation
  - media type (make sure site is supported. ie: youtube, soundcloud, etc) // maybe implicit typing in song.html template
 
***
 
 
## UI Design
 
 - About/Help page
 - \\Account settings page
 - Refine navbar
   - \\home icon
   - add artist button
   - mobile collapse
 - Media Link radio buttons
 - edit button location
   - artists
   - albums
   - songs
   
***
 
## UI Templates
 
 - About/Help page
 - \\Account settings page
 - Search results
 - \\add/edit page forms
 - \\add/edit save button (mobile)
 - add website/social media fields for artists
 - verify HTML tags and attributes are correct (last)
 - Add links from song page to album/artist and vice versa
 - Code navbar refinements
 
***

## Server-side Logic
 
 
 - translate/transfer templates from Jekyll to Flask (very last)
   - remove/replace YAML front-matter
      - replace liquid includes with extends
   - make sure navbar and footer include work properly (if not, move to template)
   - add routes for all pages
   - confirm register logic
   - define login-required routes
   - attach login to db
   - write queries for each route
 
***

## Database
 
 - Establish fields needed for each table with datatypes, lengths, interdependancies, etc.
 - Update users table with image url
 - Create tables 
   - Artists
   - Albums
   - Songs
   - Comments
 
***