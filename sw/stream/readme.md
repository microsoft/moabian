pip3 install --user requirements.txt
python3 app.py

-or-

gunicorn --threads 5 --works 1 --bind 0.0.0.0:8080 app:app
