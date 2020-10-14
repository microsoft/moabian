First: install the requirements (not as root):

```bash
pip install -r requirements.txt
```

Show the camera (stop moab first)
```bash
down
./start.sh
```

Alternatively: run these three processes in their own shells:

```bash
./source.py
./hub.py
./web.py
```

