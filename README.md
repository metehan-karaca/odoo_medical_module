# Medical Appointment System - Odoo 15

This project is a training task for an internship for learning **ODOO-15** development.  
The goal is to build a basic **Medical Appointment System** for a hypothetical hospital using ODOO framework.

Tasked Project : [Odoo_Training]()

Official odoo documentation: [Odoo 15 Documentation](https://www.odoo.com/documentation/15.0/)

## Project Overview

This module introduces five main models:

- Doctor
- Patient
- Department
- Appointment
- Treatment


## Setup
Enter the commands into terminal to follow instructions.
### Directory Config
mkdir ~/odoo \
cd ~/odoo \
mkdir odoo15 \
cd odoo15 \
mkdir custom 

### Install Git
sudo apt install -y git

### Clone Odoo 15 and update packages
git clone https://www.github.com/odoo/odoo --depth 1 --branch 15.0 --single-branch

sudo apt-get update
sudo apt-get upgrade -y

### Install Python and its dependencies
sudo apt-get install -y python3-pip python3-dev python-dev \
libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev \
build-essential libssl-dev libffi-dev libmysqlclient-dev \
libjpeg-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev \
libatlas-base-dev

### Install Node.js and LESS compiler
sudo apt-get install -y npm
sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install -g less less-plugin-clean-css
sudo apt-get install -y node-less

### Install PostgreSQL
sudo apt-get install -y postgresql

### Switch to the postgres user
sudo su - postgres

### Create a new PostgreSQL user (replace <your_user> with your desired username)
createuser --createdb --username postgres --no-createrole --no-superuser --pwprompt <your_user>

### Set a password when prompted (e.g., odoo)

### Open PostgreSQL shell
psql

### Grant superuser privileges
ALTER USER <your_user> WITH SUPERUSER;

### Exit PostgreSQL shell
\q

### Exit postgres user
exit

### Install Odoo requirements
cd odoo \
sudo pip3 install -r requirements.txt

### Download wkhtmltopdf
sudo wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb

sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb

sudo apt install -f
### Create a configs file inside
mkdir ~/odoo/odoo15/custom/configs/odoo.conf

odoo.conf: \
addons_path = /path/to/odoo15/odoo/addons,/path/to/odoo15/custom/addons(both custom and vanilla addon paths here)

### To start server:
python3 odoo/odoo-bin -c /path/to/your/odoo.conf

### To open portal:
http://localhost:8069



### Recommended installation guide:  
[How to Install Odoo 15 on Ubuntu 20.04 LTS](https://www.cybrosys.com/blog/how-to-install-odoo-15-on-ubuntu-2004-lts-server)


## Stakeholders

- Doctors
- Patients

## Models and Fields

### Doctor

| Field         | Type              | Note                                    |
|---------------|--------------------|-----------------------------------------|
| First Name    | Char               |                                         |
| Last Name     | Char               |                                         |
| Full Name     | Computed Char      | Auto-computed from first and last name  |
| Date of Birth | Date               |                                         |
| Age           | Integer (readonly) | Auto-calculated from date of birth      |
| Phone         | Char               |                                         |
| Email         | Char               | Constraint: no duplicate emails allowed |
| Department    | Many2one           | Linked to Department model              |
| Shift Start   | Float (Time Widget) |                                         |
| Shift End     | Float (Time Widget) |                                         |



### Patient

### Department


### Appointment

### Treatment

## Functionalities

### Appointment Wizard


### Validations

## Additional Notes

## License

This project is intended for educational and training purposes only.

