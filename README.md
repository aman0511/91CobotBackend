Cobot-Proto
===========================

This is the flask based prototype of cobot api for acquisition of memberships
related data to a local database.

##Requirements
1. Python `2.7+`
2. `pip` installed
3. virtualenv

##Instructions
1. Install all package dependencies by using `pip`
```bash
    $ pip install -r requirements.txt 
```

2. Also, set some required environment variables for this prototype
```bash
    $ export COBOT_TOKEN='<cobot-api-token>'
    $ export COBOT_DB_URL='<database-url>'
```

3. To run application
```bash
    $ python manage.py runserver
```

4. To create database tables
```bash
    $ python manage.py create_db
```

5. To delete database tables
```bash
    $ python manage.py drop_db
```

6. To run task which gets data from cobot api and add to database
```bash
    $ python manage.py run_task [-d DATE or --date=DATE]
    # DATE should be in format 'YYYY-MM-DD'
```

