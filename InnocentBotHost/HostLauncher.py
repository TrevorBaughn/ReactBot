print("Importing libraries...")
while(True):
    try:
        import sys
        import os

        import tempfile
        import shutil
        import configparser

        print("Imported libraries successfully")
        break
    except:
        print("Failed to import libraries, trying to install them and retrying...")
        os.system('pip3 install tempfile')
        os.system('pip3 install shutil')
        os.system('pip3 install configparser')

#opens the config
config = configparser.ConfigParser()
config.read('config.ini')
config.sections()

debug = bool(config.get('Settings', 'Debug'))
if debug != True:
    # Create temporary dir
    t = tempfile.mkdtemp()
    print(t)
    # Clone into temporary dir
    os.system(f'git -C {t} clone https://github.com/TheGoatIsBetter/InnocentBot.git')
    
    # Pathsetting magic
    path = os.path.realpath(__file__)
    path = path[:-16]
    dst = path + '/Host'
    print(dst)
    src = f'{t}/InnocentBot/InnocentBotHost/Host'
    print(src)

    # take out the destination dir if it exists
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    # move the temp dir to the destination dir
    shutil.copytree(f'{src}', f'{dst}')

    #the same thing again but with lots of different things because the host also needs the updated Client
    # Pathsetting magic
    path = os.path.realpath(__file__)
    path = path[:-33]
    dst = path + 'InnocentBotClient/Client'
    print(dst)
    src = f'{t}/InnocentBot/InnocentBotClient/Client'
    print(src)

    # take out the destination dir if it exists
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    # move the temp dir to the destination dir
    shutil.copytree(f'{src}', f'{dst}')

    # Remove temporary dir
    shutil.rmtree(t)

os.chdir('Host')
os.system('python3 InnocentBotHost.py')
sys.exit(0)