# Todo & notes app
This is a simple app that allows creation of notes and tasks.
Tasks have dates added to them and are sorted chronologically.
Notes can have tags added and removed from them, but no other tag functions are implemented.

Users can register, log in and log out. There should be sanity checks for
normal use, but the application, but it doesn't go out of its way to prevent
users from intentionally doing silly things.

The UI uses basic CSS. Not all elements are aligned as I'd like them to be.

The app can be tested at [https://tsoha-notesapp.herokuapp.com/](https://tsoha-notesapp.herokuapp.com/).

# Original project goals
I'm making a notes/tasks app that supports multiple authenticated users. Passwords
shall be salted and hashed with some recently modern password hashing algorithm.

I aim to make both notes and tasks. Both will support creation and
deletion. Notes can have tags attached to them and can be filtered by tag.
Tasks have dates related to them and are sorted chronologically. Expired
tasks will be filtered by default.

The user interface aims to be simple, with enough CSS to hide the ugliness of
default HTML elements. I'll also look into using JS to not require page reloads
after every click, but it's a secondary goal.
