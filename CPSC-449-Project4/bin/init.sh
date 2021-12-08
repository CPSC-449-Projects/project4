#!/bin/sh

sqlite-utils insert ./var/users.db users --csv ./share/users.csv --detect-types --pk=username
sqlite-utils create-index ./var/users.db users username email_address --unique

sqlite-utils insert ./var/users.db follows --csv ./share/following.csv --detect-types --pk=username --pk=following
sqlite-utils add-foreign-key ./var/users.db follows username users username
sqlite-utils add-foreign-key ./var/users.db follows following users username

sqlite-utils insert ./var/posts.db post --csv ./share/posts.csv --detect-types --pk=id
