## Why?
- Keep time
- Keep time
- Keep time

## Overview
- Django api base by opendream
- Account authenticate
- Social connect
- Common model for plug everything

## Install

### setup
	mkdir projectname
	cd projectname
	git clone git@github.com:opendream/odmbase.git
	cp -R odmbase/default/. .


### Virtualenvs
	mkvirtualenv projectname

### Requirements
	pip install -r requirements.txt

### Postgres

	psql postgres
	CREATE DATABASE projectname;
	CREATE USER projectname WITH PASSWORD 'projectname';
	GRANT ALL PRIVILEGES ON DATABASE projectname to projectname;

### Management
	python manage.py migrate


find all word "project_implement" and implement

### Account fields implementation
account.models

	class User(ODMUser):
		.... your fields implement here ....


### Add modules
- comments
- likes

conf/settings.py

	APPEND_INSTALLED_APPS = (
		....
		'odmbase.comments',
		'odmbase.likes',
		....
	)

api/registers.py

	from odmbase.comments.api import CommentResource
    from odmbase.likes.api import LikeResource

    API_RESOURCES = (
		....
		CommentResource(),
        LikeResource(),
		....
	)

