# Install

### Virtualenvs
- mkvirtualenv projectname

### Requirements
- pip install -r requirements.txt
- bower install

### Postgres

	psql postgres
	CREATE DATABASE projectname;
	CREATE USER projectname WITH PASSWORD 'projectname';
	GRANT ALL PRIVILEGES ON DATABASE projectname to projectname;

### Management
- python manage.py migrate
