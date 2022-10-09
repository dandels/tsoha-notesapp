# Project goals
I'm making a notes/TODO app that supports multiple authenticated users. Passwords
shall be salted and hashed with some recently modern password hashing algorithm.

I aim to make both notes and TODO entries. Both will support creation and
deletion. Notes can have tags attached to them and can be filtered by tag. TODO
tasks have dates related to them and are sorted chronologically. Expired entries
will be filtered by default.

The user interface aims to be simple, with enough CSS to hide the ugliness of
default HTML elements. I'll also look into using JS to not require page reloads
after every click, but it's a secondary goal.

# Current state & testing
Users can register, log in and log out. Notes can be created. Todo entries are
not yet implemented, but they will be functionally quite close to notes.
Tagging notes is not yet supported, although the database tables are created.

The app can be tested at [https://tsoha-notesapp.herokuapp.com/](https://tsoha-notesapp.herokuapp.com/).
