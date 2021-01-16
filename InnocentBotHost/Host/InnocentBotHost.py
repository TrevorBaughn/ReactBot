import os
os.system('python3.8 -m pip install discord')
import discord
os.system('python3.8 -m pip install discord.py')
from discord.ext import commands
os.system('python3.8 -m pip install configparser')
import configparser
import time
os.system('python3.8 -m pip install socket.py')
import socket
import threading


print('Running...')

#create the config
config = configparser.ConfigParser()

#read the config
os.chdir('..')
config.read('config.ini')

config.sections()

#get versions
host_version = config.get('Version', 'HostVersion')
client_version = config.get('Version', 'ClientVersion')


#get bot token
token = config.get('Settings', 'DiscordToken')
print(f'Discord Token: {token}')


#set up bot
bot = commands.Bot(command_prefix='|')
print(f"Command prefix set to: '{bot.command_prefix}'")

#setup conectoin to client
s = socket.socket()
print("Socket successfully created")

server_port = int(config.get('Server Address', 'ServerPort'))
print(f"Port: {server_port}")

s.bind(('', server_port))
print(f"Socket binded to port {server_port}")

s.listen(5)   
print ("Socket is now listening...")     

print("Connecting to Discord...")

@bot.event
async def on_ready():

    #print the names of guilds connected to
    print(f'{bot.user} has connected to Discord in:')
    for guild in bot.guilds:
        print(f'  {guild.name}(id:{guild.id})')

    print("Bot initialization complete...")

########################### INITIALIZATION END - TARGET CLASS ###########################

#makes shock target object
class Target:
    def __init__(self,name):
        self.shock_switch = 0
        self.name = name
        self.code = 'dummy'
        self.addr = 'dummy'

################### Add People to Bot Network Here ###################

#possible targets for different commands
shock_targets = []

########################################################################

def listener():
    print("Starting to listen for connections...")
    while True:
        while True:
            try:
                #accept incoming
                c, addr = s.accept()

                #get client id
                client_id = c.recv(1024).decode()
                
                exec(f'{client_id} = Target(str(client_id))')

                #set code and address to those of the id
                exec(f'{client_id}.code = c')
                exec(f'{client_id}.addr = addr')


                print(f"{eval(client_id).name.capitalize()} has connected.\n  Code: {eval(client_id).code}\n  Addr: {eval(client_id).addr}")
                
                #check client version
                print(f"{client_id.capitalize()}: Checking client version...")
                c.send((client_version).encode())
                their_version = c.recv(1024).decode()

                if their_version != client_version:
                    print(f"{client_id.capitalize()}: Updating client...")
                    break
                    #updates client on the client side (should be updated to check github's client version rather than the one labelled here to allow for 
                    # the client to update to whatever version the host has marked to update to which would prevent the client being more updated than
                    # the host is prepared for (shouldn't be a problem anyways))
                else:
                    print(f"{client_id.capitalize()}: Client version is up to date")

                #Order: taser,
                settings = c.recv(1025).decode().split(',')

                #if Taser setting exists
                try:
                    print(f"{client_id.capitalize()} Settings:\n  Taser: {settings[0]}")
                    if settings[0] == 'True' and str(client_id) not in shock_targets:
                        shock_targets.append(str(client_id))
                    elif settings[0] == 'False' and str(client_id) in shock_targets:
                        shock_targets.remove(str(client_id))
                except:
                    print("No Taser settings...")

                print(f'{client_id.capitalize()}: Client Ready.')
            except:
                print("Something tried to connect and failed.")

#multithread the listener
threading.Thread(target=listener).start()


########################### TARGET CLASS END - COMMANDS ##################################


@bot.command()
async def shock(ctx, target, shock_length):
    
    #checks to see if target is a valid shock target
    target = target.lower()
    if (target not in shock_targets):
        print(target)
        raise commands.UserInputError(message = f"UserError: target '{target}' not in shock_targets list.")

    #checks to see if taser is turned on by target
    print('asking for shock perms...')
    eval(target).code.send("recieve_shock_perms".encode())
    print('getting shock perms...')
    eval(target).shock_switch = int(eval(target).code.recv(1024).decode())
    if eval(target).shock_switch == 1:
        print("Taser is on")
    else:
        print(f"Taser isn't currently turned on, aborting shock...\n Attempted by: {ctx.author.name}")
        raise commands.DisabledCommand(message = "Taser is currently disabled...")


    shock_length = int(shock_length)

    #sends errors if shock length is invalid but it would otherwise let it run
    if (shock_length <= 0 or shock_length > 5):
        print(shock_length)
        raise commands.UserInputError(message = f"ValueError: number '{shock_length}' either too big or too small.")
        
    #tase message
    print(f'Taser activated by {ctx.author.name}:')
    print(f'  Target: {target.capitalize()}')
    print(f'  Shock Length: {shock_length}')
    await ctx.channel.send(f"############################\n***The taser has been activated.***\nTarget: {target.capitalize()}\nShock Length: {shock_length}00 milliseconds\nScreams: Loud\n############################")

    #tases client
    eval(target).code.send(f"shock {shock_length}".encode())


@shock.error
async def shock_error(ctx, error):
    print(f'Shock Error:\n  {error}')
    if str(error) == "Command raised an exception: ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host":
        await ctx.channel.send(f"```\nError:\nClient not connected to server...\nPlease try again later.\n```")
        print("Error:\n  Client not connected to server")
    #error below is a lie... only happens if client hasn't ever connected and server looks for client on the first time though so fuck it, this is what we tell the users
    elif str(error) == "Command raised an exception: AttributeError: 'str' object has no attribute 'send'":
        await ctx.channel.send(f"```\nError:\nClient not connected to server...\nPlease try again later.\n```")
        print("Error:\n  Client not connected to server")
    elif not isinstance(error, commands.DisabledCommand):
        await ctx.channel.send(f"```\nError:\n{error}\nCorrect syntax is as follows:\n|shock <target> <shock length>\nValid Targets: {shock_targets}\nValid Shock Lengths: 1-5\n```")
    else:
        await ctx.channel.send(f"```\nError:\n{error}\nPlease try again later.\n```")






bot.run(token)
