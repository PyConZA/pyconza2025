#!/bin/bash


# Steps for deploying an update to the website (that doesn't involve upgrading wafer)

sudo -u pyconza -i

cd pyconza2025/
. ./ve/bin/activate
git pull
# Rerun tailwind if required
npm i
npm run tailwind
./manage.py collectstatic --noinput

# Reload uwsgi workers
uwsgi --reload /run/uwsgi/app/pyconza/pid

# if the above command doesn't work for some reason, use a bigger stick as root
#    service uwsgi restart