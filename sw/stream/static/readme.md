# Quick html web server on Raspberry Pi

I wanted to test these pages in three browsers (Edge, Firefox and
Safari) without hitting refresh, i.e., auto-load when the static folder
changes.

Install node via npm to get the `live-server` app:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
nvm install node
npm i -g live-server
live-server

```
Now in your browsers, open one of these:

```
http://moab:8080/grid.html
http://moab.local:8080/grid.html
```
