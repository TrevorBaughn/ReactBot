import sys
import os
os.system('python3.8 -m pip install socket.py')
import socket  
import time       
os.system('python3.8 -m pip install configparser')
import configparser
os.system('python3.8 -m pip install gpiozero')
from gpiozero import LED, Button
os.system('python3.8 -m pip install RPi.GPIO')
import RPi.GPIO as GPIO    

  
# Create a socket object  
s = socket.socket()       

#create the config
config = configparser.ConfigParser()

#read the config
os.chdir('..')
config.read('config.ini')

config.sections()

#get client version
client_version = config.get('Version', 'ClientVersion')

# Define the ip and port on which you want to connect  
server_ip = config.get('Server Address', 'ServerIP')
server_port = int(config.get('Server Address', 'ServerPort'))
print(f"Server IP: {server_ip}")
print(f"Server Port: {server_port}")

#get client id  
client_id = config.get('Settings', 'CLIENTID')
client_id = client_id.lower()
print(f'Client ID: {client_id}')


#update checker
def update():
    updateFlagged = False

    print("Checking version...")
    hosted_client_version = s.recv(1024).decode()
    s.send((client_version).encode())

    if hosted_client_version != client_version:
        print('Not up to date with host...')
        updateFlagged = True
    else:
        print('Client version is already up to date.')


    if updateFlagged:
        print("Updating to most recent version (Note: it will only update once with the host as it checks the version number the host has,\n which may not be the one actually pulled from github,\n this may be fixed in the future)")
        path = os.path.realpath(__file__)
        path = path[:-21]
        os.chdir(path)

        #lines below sets version potentially wrong depending on what was actually pulled from github to prevent activation loop with host (should eventually be fixed)
        f = open("config.ini", 'r')
        config = f.read()
        config = config.replace(f"ClientVersion = {client_version}", f"ClientVersion = {hosted_client_version}")
        f.close()
        f = open("config.ini", "w")
        f.write(config)
        f.close()
        print(config)


        os.system('python3.8 ClientLauncher.py')
        sys.exit(0)


#connect to the server
def connect():
    global s
    connected = False
    while not connected:
        try:
            #connect
            s.connect((server_ip, server_port))
            print('Connected to server...')

            #send client id
            print("Sending client id...")
            s.send((client_id).encode())

            #update check
            update()

            #settings
            taser_set = config.get("Settings", "Taser")
            print(f"Taser: {taser_set}")

            #send settings
            s.send(f"{taser_set}".encode())
            
            print("Client ready.")

            connected = True

        except:
            time.sleep(2)
            s = socket.socket()
            print("Trying to connect...") 



connect()

####################################### CONNECTION END - COMMANDS ################################

def Taser(shock_length):
    print(f"Taser:\n  Shock_Length: {shock_length}")

    #spams taser for a set time
    #tase_endtime = time.monotonic() + int(shock_length)/10
    #while time.monotonic() < tase_endtime:
    #    LED.on()
    #    time.sleep(0.05)
    #    LED.off()
    #    time.sleep(0.05)

    #turns taser on for set amount of time
    LED.on()
    time.sleep(int(shock_length)/10)
    LED.off()

####################################### COMMANDS END - MAIN LOOP #################################

while(True):
    #get data from server
    try:
        raw_recieve = s.recv(1024).decode()
        print("Data Recieved")
    except:
        connect()
                
    try:        
        recieve = raw_recieve.split()
    except:
        print("Failed to retrieve data, most likely due to a reconnection")
        recieve = ['failed', 'to', 'pull', 'info']
    
    #################################### MAIN LOOP CONT. - USE COMMANDS ##########################

    do_thing = recieve[0]

    if do_thing == "recieve_shock_perms":
        print("Sending shock perms...")
        perms = GPIO.input(2)
        s.send(str(perms).encode())
    if do_thing == "shock":
        shock_length = recieve[1]
        Taser(shock_length)


#close the connection  
s.close()