1. Until the streaming engine is integrated into the setup, you must:

```
pip3 install --user requirements.txt
```

2. Then, to run:

```
python3 app.py
```

-or-

```
gunicorn --threads 5 --works 1 --bind 0.0.0.0:8080 app:app
```
