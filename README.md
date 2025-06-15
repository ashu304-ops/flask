#  Configure CI/CD Pipeline: Jenkins + Ansible + Docker (All from Scratch) 
Note: No DockerHub/ready images 
● Implement a CI/CD pipeline that pulls code, builds Docker image, and runs 
Ansible for remote deployment on a Linux server 



# Setup  is  made between host machine is macos  and target machine is wsl runing on windows

Set up a Jenkins pipeline (on macOS) that:

Pulls code from Git.

Transfers the code to a remote target machine (WSL2).

Builds the Docker image on WSL2 (no DockerHub).

Uses Ansible (on macOS or Jenkins node) to manage deployment on WSL2.



# Infrastructure  Overview 

Wsl ---python,openssh server,docker
Macos -- jenkins , ansible,java

# ssh config on Wsl on  windows 

1)start ssh server on  wsl 

sudo  service ssh start

2)check ip address  in  which port 22 ssh is hosting

ip adddr show eth0

3) click on cmd or powershell
ssh -p 22 <username  of  wsl>@<ip address of eth0>

successful then go  to step4

4) Port forwarding 22 to  22  which can be accessible and go  to powershell  as administrator

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=22 connectaddress= <ip address of eh0> connectport=22
5) allow  firewall to pass port 22

New-NetFirewallRule -DisplayName "Allow SSH" -Direction Inbound -LocalPort 22 -Protocol TCP -Action Allow

6) verifying on  powershell   
ssh -p 22 <username  of  wsl>@<ip address of windows>

7) know the  ip  address of  windows 

ipconfig

drag on  to ipv4 address 

# ssh config on macos

1) click  on terminal 

 ssh -p 22 <username  of  wsl>@<ip address of windows>

if conection is  established move  to step2

2) password less configuration annd ssh key generation

ssh-keygen -t rsa -b 4096 -C "name of key"

3) copy  ssh public key  to  wsl  machine

ssh-copy-id -i ~/.ssh/id_rsa.pub username@<ip addres of  windows>

# Ansible configuration

1) create  a folder  where  set up  hosts.ini file  for  connection  of machine  via  ansible

------------------------
[wsl]
wslhost ansible_host=<ip address of  windows> ansible_user=username of wsl   ansible_port=22 ansible_ssh_private_key_file=~/.ssh/id_rsa (path to ssh rivate key)

--------------------------

2) cross  verifying  the connection  

ansible wslhost -i inventory.ini -m ping

it is successfull 

3) create a  deploy.yml 

----------------------------------------------

- name: Deploy Docker app in WSL
  hosts: wsl
  #become: yes
  tasks:
    - name: Stop existing container if running
      shell: docker stop app || true
      ignore_errors: yes

    - name: Remove container if it exists
      shell: docker rm app || true
      ignore_errors: yes

    - name: Run new container
      docker_container:
        name: app
        image: app-image:latest
        state: started
        restart_policy: always
        ports:
          - "5000:5000"
-----------------------------------------------------------


# Create  a dummy app.py and  dockerfile for deployment

1) create flask  app  hosting  on port 5000
----------------------------------------------
from  flask  import Flask

app= Flask(__name__)

@app.route('/')
def home():
    return "Hello  from flask"

@app.route('/about')
def about():
    return "This  is flask app from jenkins"

@app.route('/hello/<name>')
def hello(name):
    return f"hello myself {name} !"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
-------------------------------------------------
2)create docker file for containerized purpose
-------------------------------------------------
# Use an official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container
COPY .  /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]

--------------------------------------------------------
3) create requirement.txt
--------------------------------------------------------
Flask==2.3.3

--------------------------------------------------------

# Note  it is mandatory to push this app.py,dockerfile,requirement.txt  to github  before moving to next steps




#Access to  jenkins  and made  new  pipeline 

-----------------------------------

pipeline {
    agent any

    environment {
        WSL_USER = "username of wsl"
        WSL_HOST = "ip  address of wsl "
        WSL_PORT = "22"
        REPO_URL = "git hub link"
        REMOTE_DIR = "directory to work "
        IMAGE_NAME = "app-image"
    }

    stages {
        stage('Test SSH Connection to WSL') {
            steps {
                sh """
                ssh -p ${WSL_PORT} ${WSL_USER}@${WSL_HOST} "echo 'Connected to WSL host!'"
                """
            }
        }

        stage('Clone Repo in WSL') {
            steps {
                sh """
                ssh -p ${WSL_PORT} ${WSL_USER}@${WSL_HOST} '
                    rm -rf ${REMOTE_DIR} &&
                    git clone -b main ${REPO_URL} ${REMOTE_DIR}
                '
                """
            }
        }

        stage('Build Docker Image in WSL') {
            steps {
                sh """
                ssh -p ${WSL_PORT} ${WSL_USER}@${WSL_HOST} '
                    cd ${REMOTE_DIR} &&
                    docker build -t ${IMAGE_NAME} .
                '
                """
            }
        }

        stage('Deploy with Ansible') {
            steps {
                sh 'path to ansible-playbook -i path to hosts.ini  path to deploy.yml'
            }
        }
    }
}

--------------------------------------------------------------------------------------------------------------------


# verifying  the  task

1)  check on  local  browser and  see display output

http://localhost:5000








 


   

