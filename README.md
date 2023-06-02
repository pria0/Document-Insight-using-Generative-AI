### Create virtualenv
- virtualenv venv

### Activate virtualenv
- source venv/bin/activate

### Install dependency
- pip install -r requirements.txt

### Create new app or module
- Go to app folder
- python ../manage.py startapp app_name

### Run migrations
- python manage.py migrate

### Create super user
- python manage.py createsuperuser

### Run server
- python manage.py runserver