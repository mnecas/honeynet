# Honeynet
## Info
This is BUT thesis project for modular honeypot system base on containers.

## Start the web
To run the project in your enviroment you can either run
`docker-compose up`.

This will create three containers the postgres database, Django website and the syslogserver to which all containers will send all syslogs.

## Admin page
The container automatically creates one default admin account with which you can log in to the admin part of the website.


## Development
To run the web server you need to install all necessary python dependencies for it you can run:

`pip3 install -r ./requirements.txt`

For database initialization:

`python3 manage.py makemigrations`

`python3 manage.py migrate`

To run the server use:

`python3 maange.py runserver`

(Recommend chaning the `DEBUG` in settings to `True`)
