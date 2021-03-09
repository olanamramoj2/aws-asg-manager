### Requirements

1. Machine should have python3 installed (suggested version is 3.7)
2. Create ~/.aws/config. Provide valid configuration values. Get aws_access_key_id & aws_secret_access_key from the admin
### Installation
1. Setup python virtual environment inside project directory
```
cd <project directory>

#if pip3 exists
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt

#if pip3 does not exists
python3 -m venv --without-pip ./venv
source ./venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source ./venv/bin/activate
pip3 install -r requirements.txt

deactivate
```
1. Create a .env file by copying the .env.dist in the root directory.
```
cp .env.dist .env
```
1. Provide valid values 
### Getting Started
1. Source from virtual environment
```
source ./venv/bin/activate
```
### If EC2 is in private subnet
1. upload ssh private key to <path_to_users>/.ssh/id_rsa
```
nano <path_to_users>/.ssh/id_rsa
chmod 400 <path_to_users>/.ssh/id_rsa
```
2. change directory to git folder/project and change origin url (get git clone url via ssh from gitlab console)
```
git remote set-url origin <ssh url>
```
3. you should be able to pull from repo after this
### Usage
1. you should be able to create image and update ASG
```
<path to this repo>/venv/bin/python <path to this repo>/create_image.py
```
2. you should be able to delete images and snapshots based from retention period
```
<path to this repo>/venv/bin/python <path to this repo>/delete_snapshot.py
```
2. 
