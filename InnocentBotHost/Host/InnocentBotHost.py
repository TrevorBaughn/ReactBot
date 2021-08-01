print("Importing libraries...")
while(True):
    try:
        import os
        import time
        import multiprocessing as mp
        from multiprocessing.pool import ThreadPool

        import discord
        from discord.ext import commands, tasks
        import configparser
        import socket

        print("Imported libraries successfully")
        break
    except:
        print("Failed to import libraries, trying to install them and retrying...")
        os.system('pip3 install discord.py')
        os.system('pip3 install socket.py')
        os.system('pip3 install configparser')

#setup to grab from config
config = configparser.ConfigParser()
os.chdir('..') #go back 1 directory
config.read('config.ini')
config.sections()

#create miscellanious variables from config
print('\nMISC--------------')
host_version = config.get('Version', 'HostVersion')
print(f'Host Version   : {host_version}')
client_version = config.get('Version', 'ClientVersion')
print(f'Client Version : {client_version}')

#connect to client
print('\nSOCKET------------')
server_ip = config.get('Server Address', 'ServerIP')
print(f"IP             : {server_ip}")
server_port = int(config.get('Server Address', 'ServerPort'))
print(f"Port           : {server_port}")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created successfully')
s.bind(('', server_port))
print(f"Socket binded to port {server_port}")
s.listen(5)
print('Socket now listening')

#set up Discord bot
print('\nDISCORDBOT--------')
bot = discord.Client()
print("Client set up")
discord_token = config.get('Discord', 'DiscordToken')
print(f'Discord Token  : {discord_token}')
bot = commands.Bot(command_prefix=config.get('Discord', 'BotPrefix'))
print(f'Command Prefix : {bot.command_prefix}')
print('Connecting to Discord...')

@bot.event
async def on_ready():
    #wait for the bot to be ready
    await bot.wait_until_ready()

    #print the names of guilds connected to
    print(f'{bot.user} has connected to Discord in:')
    for guild in bot.guilds:
        print(f'  {guild.name}(id:{guild.id})')

    print("Bot initialization complete...\n\n")
    
    #start listening for connections
    check_for_connection.start()

########################### INITIALIZATION END - CLASSES ###########################

#makes Target client object
class ClientTarget:
    def __init__(self,client_id):
        self.shock_switch = 0
        self.client_id = client_id
        self.code = 'dummy'
        self.addr = 'dummy'

#target maker
#https://stackoverflow.com/questions/553784/can-you-use-a-string-to-instantiate-a-class
class CreateTarget:
    def __init__(self):
        self.client = {}

    def create(self, client_id):
        instance = ClientTarget(client_id)
        self.client[str(client_id)] = instance

#create the target-making object
Target = CreateTarget() 

###################################################################################

#client add_ons
add_ons = ['taser','pwm_toggle','pwm_max']

#listens for connections
def listener():
    print("Listening for connections...")
    attempting_to_connect = False
    try:
        #accept connection
        c, addr = s.accept()
        #sets flag for trying to connect
        attempting_to_connect = True    

        #get client id
        client_id = c.recv(1024).decode()

        #create client object
        Target.create(client_id)

        #set socket connection to other variable to allow for more
        Target.client[client_id].code = c
        Target.client[client_id].addr = addr

        #print connection status
        print(f'{client_id.capitalize()} has connected.\n   Code: {Target.client[client_id].code}\n   Addr: {Target.client[client_id].addr}')

        #sending host version
        print(client_version)
        c.send(client_version.encode())
        #input()

        #check versions
        print("   Checking for version differences...")
        check_version = c.recv(1024).decode()
        if check_version == 'different version':
            print("   Client version is different, updating client...")
            c.close()
        else:
            print("   Client version is the same, no need to update...")
        print(check_version)

        #recieve add-ons
        for add_on in add_ons:
            exec(f'Target.client[client_id].{add_on} = c.recv(1024).decode()')
            exec(f"print(Target.client[client_id].{add_on})")
            

        #ready message
        ready = c.recv(1024).decode()
        print(ready)


        return Target.client
    except:
        if attempting_to_connect:
            print('Failed to connect...')
        else:
            print('No new connections...')



#listens for new objects created upon connection
@tasks.loop(seconds=5)
async def check_for_connection():
    #set up a thread that can return values
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(listener)
    #gets the client connections from the listener and sets the client connections outside it to be equal to it
    return_client_list = async_result.get()
    Target.client = return_client_list
    print(Target.client)


###################################################################################

@bot.command()
async def shock(ctx, target, shock_length, pwm_level='None'): #pwm_level is a string so that it sends over socket
    print(f"\n{ctx.author.name} has attempted to shock {target}...")
    
    #set target to universally used name
    target = target.lower()

    #check taser perms for target
    if Target.client[target].taser != True:
        raise commands.UserInputError(message = f"UserError: target '{target}' not a valid target")

    #get perms
    Target.client[target].code.send('get_shock_perms'.encode())
    shock_switch = Target.client[target].code.recv(1024).decode()
    
    #check shock perms
    if shock_switch != 1:
        raise commands.CommandOnCooldown(message= f"CommandOnCooldown: target '{target}' has their shock switch turned off")

    #make sure shock length is within range
    if shock_length <= 0 or shock_length > 5:
        raise commands.UserInputError(message= f"UserInputError: shock length must be within 0-500 milliseconds")

    #check to see if target has PWM
    if bool(Target.client[target].pwm_toggle) != True and pwm_level != 'None':
        raise commands.BadArgument(message= f"BadArgument: target '{target}' does not have PWM")

    #tase message
    print(f'Taser activated by {ctx.author.name}:')
    print(f'  Target: {target.capitalize()}')
    print(f'  Shock Length: {shock_length}')
    print(f'  PWM: {pwm_level}')
    message = f"""############################
    ***The taser has been activated.***
    Target: {target.capitalize()}
    Shock: Length: {shock_length} milliseconds
    PWM: {pwm_level}
    Screams: Loud
    ############################"""
    await ctx.channel.send(message)

    #send tase instruction to client
    Target.client[target].code.send(f"taser {shock_length} {pwm_level}")

@shock.error
async def shock_error(ctx, error):
    print(f'Shock Error:\n  {error}')
    if str(error) == "Command raised an exception: ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host":
        await ctx.channel.send(f"```\nError:\nClient not connected to server...\nPlease try again later.\n```")
        print("Error:\n  Client not connected to server")
    elif not isinstance(error, commands.DisabledCommand):
        await ctx.channel.send(f"```\nError:\n{error}\nCorrect syntax is as follows:\n|shock <target> <shock length>\nValid Targets: {shock_targets}\nValid Shock Lengths: 1-5\n```")
    else:
        await ctx.channel.send(f"```\nError:\n{error}\nPlease try again later.\n```")

bot.run(discord_token)

