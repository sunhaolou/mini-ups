#!/bin/bash
echo "here is initserver.sh"
# python3 manage.py makemigrations
# while ! python3 manage.py migrate; do
#     echo "Migration failed, retrying in 3 seconds..."
#     sleep 3
# done
# Uncomment the next line to enable superuser creation
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python3 manage.py shell
