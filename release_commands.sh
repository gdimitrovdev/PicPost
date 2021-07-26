cd PicPost
python manage.py migrate --fake
python manage.py makemigrations
python manage.py migrate