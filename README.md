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

3. To run application with simple flask server
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

8. To run application within [guicorn](http://gunicorn.org/) server
```bash
    $ python manage.py gunicorn
```
    This command also supports all gunicorn parameters

##Endpoints

### Cards Endpoint
A api endpoint returns all necessary information to fill some basic card's data

>/api/cards

By default, returns all information regarding all hubs

#### Parameters
* *hub_name* : a hub name, to get report details regarding a particular hub
        
        /api/cards?hub_name=91sgurgaon

#### Response
Type - **JSON**

```json
    [
        {
            "card_no": 1,
            "total_active_members": 520,
            "new_members": {
                "percent": 3.0,
                "duration": 30
            }
        },
        {
            "card_no": 2,
            "mrr_value": 4827354.00,
            "increment_revenue": {
                "percent": 4.0,
                "duration": 30
            }
        },
        {
            "card_no": 3,
            "new_members": {
                "count": 7,
                "duration": 7,
                "base_percent": 0.5
            }
        },
        {
            "card_no": 4,
            "leave_members": {
                "count": 3,
                "duration": 7,
                "base_percent": 0.6
            }
        }
    ]
```



### Report Endpoint
A api endpoint returns all details of member's report of all hubs or specific hubs to plot that data on graph.

>/api/reports

By default, returns all member's report regarding all hubs

#### Parameters
* *hub_name* : a hub name, to get report details regarding a particular hub
        
        /api/reports?hub_name=91sgurgaon

* *plan_type* : a plan type, to get report details regarding a particular types of plan. It's value can be of four types (i.e `Full Time`, `Part Time`, `Others` and `Ignore`)

        /api/reports?hub_name=91sgurgaon&plan_type=Full Time

* *from & to* : a range of dates, to get report data of a specific duration

    **Note:-** Date should be in `YYYY-MM` format
        
        /api/reports?hub_name=91sgurgaon&plan_type=Full Time&from=2015-03&to=2015-09

#### Response
Type - **JSON**
