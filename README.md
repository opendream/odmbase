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

### For project implement by odmbase
- cp odmbase/README.md .
- cp odmbase/requirements.txt .
- cp odmbase/conf.default conf
- cp odmbase/managment.py .

find all word "project_implement" and implement

### Account fields implementation
account.models
class AbstractAccountField(models.Model):

    .... your fields implement here ....

    class Meta:
        abstract = True
