# Medical Appointment System - Odoo 15

This project is a training task for an internship for learning **ODOO-15** development.  
The goal is to build a basic **Medical Appointment System** for a hypothetical hospital using ODOO framework.

Tasked project : [Odoo_Training](Odoo_Training.docx)

Official odoo documentation: [Odoo 15 Documentation](https://www.odoo.com/documentation/15.0/)

![logo](static/description/icon.png)

## Project Overview



# Setup

Follow this guide step-by-step depending on your system.


## Prerequisites
- Ubuntu(20.04.6)
- Or Installed WSL2 + Ubuntu (if on Windows)  

---

<details>
<summary><h2>Setting up Odoo 15 on Linux / WSL2 (Ubuntu)</h2></summary>

### 1. Directory Structure

```bash
mkdir ~/odoo
cd ~/odoo
mkdir odoo15
cd odoo15
mkdir custom
```


### 2. Install Git

```bash
sudo apt update
sudo apt install -y git
```


### 3. Clone Odoo 15 Source Code

```bash
git clone https://github.com/odoo/odoo --depth 1 --branch 15.0 --single-branch
```


### 4. Update and Upgrade Packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```


### 5. Install Python and Dependencies

```bash
sudo apt-get install -y python3-pip python3-dev python-dev \
libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev \
build-essential libssl-dev libffi-dev libmysqlclient-dev \
libjpeg-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev \
libatlas-base-dev
```


### 6. Install Node.js and LESS Compiler

```bash
sudo apt-get install -y npm
sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install -g less less-plugin-clean-css
sudo apt-get install -y node-less
```


### 7. Install PostgreSQL

```bash
sudo apt-get install -y postgresql
```


### 8. Create PostgreSQL User

Switch to the `postgres` user:

```bash
sudo su - postgres
```

Create your new database user:

```bash
createuser --createdb --username postgres --no-createrole --no-superuser --pwprompt your_user
```

Set a password (e.g., `odoo` when prompted).

Enter PostgreSQL shell:

```bash
psql
```

Grant Superuser privileges:

```sql
ALTER USER your_user WITH SUPERUSER;
```

Exit PostgreSQL shell:

```bash
\q
exit
```

---

### 9. Install Python Packages for Odoo

```bash
cd ~/odoo/odoo15/odoo
sudo pip3 install -r requirements.txt
```


### 10. Install wkhtmltopdf (for PDF reports)

```bash
sudo wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo apt install -f
```


### 11. Create Odoo Configuration File

```bash
mkdir ~/odoo/odoo15/custom/configs
nano ~/odoo/odoo15/custom/configs/odoo.conf
```

Paste inside `odoo.conf`:

```ini
[options]
addons_path = /home/your_username/odoo/odoo15/odoo/addons,/home/your_username/odoo/odoo15/custom/addons
admin_passwd = admin
db_host = False
db_port = False
db_user = your_user
db_password = your_password
```
(Replace paths and credentials as needed.)


### 12. Starting the Odoo Server

```bash
python3 ~/odoo/odoo15/odoo/odoo-bin -c ~/odoo/odoo15/custom/configs/odoo.conf
```

Odoo portal will open at:  
[http://localhost:8069](http://localhost:8069)

</details>


<details>
<summary><h2>🖥️ WSL2 + VS Code Setup (Windows Users)</h2></summary>

1. **Install WSL2 and Ubuntu** if not already installed.  
Follow Microsoft's guide: [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)

2. **Install VS Code** from [VS Code Website](https://code.visualstudio.com/).

3. **Install these Extensions** inside VS Code:
    - Remote - WSL
    - Python
    - GitHub Pull Requests and Issues

4. **Open Ubuntu in WSL2**.

5. **Use "Remote - WSL" or "Remote Explorer" tab to open your WSL2 workspace** in VS Code.

6. Follow the exact same **Linux setup** instructions inside your Ubuntu terminal


</details>

---

<details>
<summary><h2>Running this module in your ODOO installation</h2></summary>

1. Go to your custom addons directory:

```bash
cd ~/odoo/odoo15/custom/addons
```

2. Clone this project:

```bash
git clone https://github.com/metehan-karaca/odoo_medical_module
```


3. Update the Apps list inside Odoo and install the module from Odoo interface.
(localhost:8069/web?*debug=1*...  instert *debug=1* to activate developer mode first.)

</details>


## Example Directory Structure

```
~/odoo/
└── odoo15/
    ├── custom/
    │   ├── addons/
    │   │   └── hospital_management_module/
    │   └── configs/
    │       └── odoo.conf
    └── odoo/
```

---


### Recommended installation guide:  
[How to Install Odoo 15 on Ubuntu 20.04 LTS](https://www.cybrosys.com/blog/how-to-install-odoo-15-on-ubuntu-2004-lts-server)

---

# Project Details

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

