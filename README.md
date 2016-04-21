91cobot-Web-API
===========================

A flask based web api for acquisition of memberships data from cobot and also calculate some required metrics from them to report analysis on monthly basis.

##Requirements
1. Python `2.7+`
1. `pip` installed
1. virtualenv

##Instructions
1. First install some system dependency
    ```bash
        $ sudo apt-get install python-dev libssl-dev libffi-dev libmysqlclient-dev
    ```

1. Install all python package dependencies by using `pip`
    ```bash
        $ pip install -r requirements.txt 
    ```

1. Also, set some required environment variables for this prototype
    ```bash
        $ export CONFIG='local'             # 'dev' for production
        $ export COBOT_DB_URL='<database-url>'
        $ export COBOT_TOKEN='<cobot-access-token>'
        $ export LOG_FILE_PATH='<log-file-folder-path>'
    ```

1. To run application with simple flask server
    ```bash
        $ python manage.py runserver
    ```

1. To create database tables
    ```bash
        $ python manage.py create_db
    ```

1. To delete database tables
    ```bash
        $ python manage.py drop_db
    ```

1. To do database schema migrations
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

1. To run task which gets data from cobot api and add that to database tables
    ```bash
        $ python manage.py run_task_data [-sd START_DATE or --startDate=START_DATE]
          [-ed END_DATE or --endDate=END_DATE] [ -h HUB_NAME or --hub=HUB_NAME]
          
          # DATE should be in format 'YYYY-MM-DD'
    ```
    **Note:** To run task for a specific date, then you should only pass that date
    as `-sd or --startDate`.

1. To run task which calculate member report metrics and append them to database tables
    ```bash
        $ python manage.py run_task_report [-sd START_DATE or --startDate=START_DATE]
          [-ed END_DATE or --endDate=END_DATE] [ -h HUB_NAME or --hub=HUB_NAME]
          
          # DATE should be in format 'YYYY-MM'
    ```
    **Note:** To run task for a specific date, then you should only pass that date
    as `-sd or --startDate`.

1. To run application within [guicorn](http://gunicorn.org/) server
    ```bash
        $ python manage.py gunicorn
        # OR
        $ python manage.py gunicorn -c gunicorn-conf.py
    ```
    **Note:** This command also supports all gunicorn parameters


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

```json
    [
        {
            "hub_plan": {
                "hub": {
                    "name": "91springboard",
                    "location": {
                        "name": "Okhla"
                    }
                },
                "plan": {
                    "name": "Full Time (4+)",
                    "type": "FULL-TIME",
                    "price": 4999.00
                }
            },
            "time": {
                "month": 5,
                "year": 2015,
                "date": "2015-05"
            },
            "count": {
                "new_member": 23,
                "retain_member": 231,
                "leave_member": 2
            },
            "revenue": {
                "new_member": 114977.0000,
                "retain_member": 1154769.0000,
                "leave_member": 9998.0000
            }
        }
    ]
```
