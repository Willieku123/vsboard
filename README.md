# How it works
On every server `gpu_logger.py` will parse all data and save to NAS, and on one server (QAQ for now) `monitor.py` will read all server data from NAS and serve the webpage.

For security reasons the dashboard can only be accessed when connected to the lab VPN (at least for now).

# Deploy on a server

Environment setup:
```
sudo adduser vsboard_user
su - vsboard_user
python3 -m venv vsboard_env
source vsboard_env/bin/activate
pip install -r /media/Pluto/willie/VSBoard/requirements.txt
```

You may need this in the process:
```
sudo apt-get install python3-venv
```

## vsboard_logger
Need to setup this on every servers.

copy `vsboard_logger.service` to the file below: 
```
sudo nano /etc/systemd/system/vsboard_logger.service
```

systemctl stuff to setup a service:
```
sudo systemctl daemon-reload
sudo systemctl start vsboard_logger
sudo systemctl enable vsboard_logger  # Enables it to start on boot
```

Check it's up and running:
```
sudo systemctl status vsboard_logger
journalctl -u vsboard_logger -f --no-pager
```

## vsboard_webpage

Only setup this on one server (QAQ for now)
You may want to change the port in `monitor.py` if the port has been occupied.

copy "vsboard_webpage.service to the file below: 
```
sudo nano /etc/systemd/system/vsboard_webpage.service
```

systemctl stuff to setup a service:
```
sudo systemctl daemon-reload
sudo systemctl start vsboard_webpage
sudo systemctl enable vsboard_webpage  # Enables it to start on boot
```

Check it's up and running:
```
sudo systemctl status vsboard_webpage
journalctl -u vsboard_webpage -f --no-pager
```
