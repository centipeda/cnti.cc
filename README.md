# `cnti.cc`

A simple pastebin built with Flask and sqlite3. Now supports dark mode!

## usage

Install Flask and Waitress. Run

```
./run.py
```

## other

setup nginx:
```
sudo ln -s $(pwd)/conf/pastebin.conf /etc/nginx/sites-enabled/
```

setup service:
```
systemctl --user enable conf/pastebin.service
systemctl --user start pastebin
# enable linger
sudo userctl enable-linger $USER
```