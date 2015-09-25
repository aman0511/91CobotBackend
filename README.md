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

6. To do database schema migrations
```bash
    $ python manage.py db [command]

    where command can be any of these {upgrade,heads,merge,migrate,stamp,show,current,edit,init,downgrade,branches,history,revision}
    upgrade             Upgrade to a later version
    heads               Show current available heads in the script directory
    merge               Merge two revisions together. Creates a new migration
                        file
    migrate             Alias for 'revision --autogenerate'
    stamp               'stamp' the revision table with the given revision;
                        don't run any migrations
    show                Show the revision denoted by the given symbol.
    current             Display the current revision for each database.
    edit                Upgrade to a later version
    init                Generates a new migration
    downgrade           Revert to a previous version
    branches            Show current branch points
    history             List changeset scripts in chronological order.
    revision            Create a new revision file
```
6. To run task which gets data from cobot api and add to database tables
```bash
    $ python manage.py run_task_data [-d DATE or --date=DATE]
    # DATE should be in format 'YYYY-MM-DD'
```

7. To run task which calculate member report metrics and add to database tables
```bash
    $ python manage.py run_task_report [-d DATE or --date=DATE]
    # DATE should be in format 'YYYY-MM'
```


##Endpoints
This api only supports one endpoint, which returns a list of all member report details.
> /api/report
