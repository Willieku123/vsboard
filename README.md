# How it works
wip

# Deploy on a server
## venv
cd /path/to/your/flask/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## systemd
copy to 
sudo nano /etc/systemd/system/flaskapp.service

sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp  # Enables it to start on boot

sudo systemctl status flaskapp


