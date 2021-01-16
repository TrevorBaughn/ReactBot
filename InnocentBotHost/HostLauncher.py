import sys
import os
import shutil
import tempfile
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
config.sections()


debug = config.get('Settings', 'Debug')

if(debug == 'True'):
    update = False
else:
    update  = True

#update Host
if update == True:
    # Create temporary dir
    t = tempfile.mkdtemp()
    print(t)
    # Clone into temporary dir
    os.system(f'git -C {t} clone https://github.com/TheGoatIsBetter/InnocentBot.git')
    # Copy desired file tree from temporary dir
    path = os.path.realpath(__file__)
    path = path[:-16]
    dst = path + '/Host'
    print(dst)
    src = f'{t}/InnocentBot/InnocentBotHost/Host'
    print(src)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(f'{src}', f'{dst}')


    
    # Remove temporary dir
    shutil.rmtree(t)

os.chdir('Host')
os.system('python3.8 InnocentBotHost.py')
sys.exit(0)