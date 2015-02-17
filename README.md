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
	git clone git@bitbucket.org:opendream/odmbase.git
	cp -R odmbase/default/* .

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

	class AbstractAccountField(models.Model):

		.... your fields implement here ....

		class Meta:
			abstract = True
