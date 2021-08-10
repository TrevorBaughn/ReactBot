print("Importing libraries...")
while(True):
    try:
        import sys
        import os
        import time    
        
        #from gpiozero import LED, Button
        #import RPi.GPIO as GPIO    
        import configparser
        import socket  

        print("Imported libraries successfully")
        break
    except:
        print("Failed to import libraries, trying to install them and retrying...")
        os.system('pip3 install gpiozero')
        os.system('pip3 install RPi.GPIO')
        os.system('pip3 install configparser')
        os.system('pip3 install socket.py')

#setup to grab from config
config = configparser.ConfigParser()
os.chdir('..') #go back 1 directory
config.read('config.ini')
config.sections()

#create miscellanious variables and settings from config
print('\nMISC--------------')
client_id = config.get('Settings', 'ClientID').lower()
print(f'Client ID      : {client_id}')
client_version = config.get('Version', 'ClientVersion')
print(f'Client Version : {client_version}')

#disable/enable addons
print('\nAdd-ons-----------')
#default values
add_ons = {'taser': False,'pwm_toggle': False,'pwm_max': 0}
for add_on in add_ons:
    try:
        exec(f"{add_on} = config.get('Add-ons', '{add_on}')")
        exec(f"add_ons['{add_on}'] = '{add_on}'")
    except:
        exec(f"{add_on} = False")
        exec(f"add_ons['{add_on}'] = False")
    print(f"{add_on} : {eval(add_on)}")

#add-on variables
print('\nAdd-on Extras-----')
#set pdm_max within range
if int(eval(add_ons['pwm_max'])) > 256: 
    add_ons['pwm_max'] = '256'
    print('   pwm_max: 256')
elif int(eval(add_ons['pwm_max'])) < 0:
    add_ons['pwm_max'] = '0'
    print('   pwm_max: 0')

#setup socket
print('\nSOCKET------------')
server_ip = config.get('Server Address', 'ServerIP')
print(f"IP             : {server_ip}")
server_port = int(config.get('Server Address', 'ServerPort'))
print(f"Port           : {server_port}")
s = socket.socket()
print('Socket created successfully\n')
    
################################################### FUNCTIONS ########################################

#connection function
def connect_to_server():
    global s
    connected = False
    print('\nCONNECT-----------')
    while not connected:
        try:
            #connect
            print("Attempting to connect to server...")
            s.connect((server_ip, server_port))
            print("Connected to server")

            #send client id
            print("     Sending Client ID...")
            s.send(client_id.encode())
            print("     Sent Client ID")



            #check for updates
            print("     Checking for updates...")

            #receiving version number on the server
            hosted_client_version = s.recv(1024).decode()
            print(hosted_client_version)
            print(client_version)

            if hosted_client_version != client_version:
                print("     Versions are different, updating...")

                #notify server of difference and disconnect
                s.send('different version'.encode())
                s.close()
                
                #change directory to ini file
                path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) #go back a directory
                os.chdir(path)

                #set version to that of hosted
                f = open("config.ini", 'r')
                config = f.read()
                config = config.replace(f"ClientVersion = {client_version}", f"ClientVersion = {hosted_client_version}")
                f.close()
                f = open("config.ini", 'w')
                f.write(config)
                f.close()

                #close and open launcher/updater
                os.system('python3.8 ClientLauncher.py')
                sys.exit(0)
            else:
                #notify host
                s.send('versions same'.encode())
                print("     Versions are the same, no need to update")



            #send over add_ons
            print("     Sending Add-ons...")
            for add_on in add_ons:
                s.send(str(eval(add_ons[add_on])).encode())
                print(str(eval(add_ons[add_on])))
            print("     Sent Add-ons")

            #send ready message (important for breaking off for loop)
            s.send(f"Client : {client_id.capitalize()}, Ready\n".encode())

            #stop loop
            connected = True
            print('Done connecting to server')

            #ready
            print(f'Client : {client_id.capitalize()}, Ready\n')
            print('RUNTIME-----------\n')

        except:
            print("Connection failed...\n")
            time.sleep(2)
            s = socket.socket()
    



################################################### RUNTIME ###########################################

#connect to server
connect_to_server()

while True:
    try:
        receive = s.recv(1024).decode()
        receive = receive.split()
    except:
        print("Failed to receive anything... likely a disconnect...")
        connect_to_server()
        receive = ['8=D'] #prevents from crash when unable to receive (especially after disconnect)

    task = receive[0]
    if task == 'get_shock_perms':
        print('Request for shock permissions...')
        print('Sending shock perms...')
        shock_switch = 1#str(GPIO.input(2))
        s.send(str(shock_switch).encode())
        print('Sent shock perms')
    elif task == 'taser':
        print('taser')

s.close()
