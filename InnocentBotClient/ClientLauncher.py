import os
import git
import shutil
import tempfile


#always true, pain in the ass to check for version update, it's a tiny file and it deletes itself afterwards, it's fine.
update  = True

#update Host
if update == True:
    # Create temporary dir
    t = tempfile.mkdtemp()
    print(t)
    # Clone into temporary dir
    git.Repo.clone_from('https://github.com/TheGoatIsBetter/InnocentBot.git', t, branch='main', depth=1)
    # Copy desired file tree from temporary dir
    path = os.path.realpath(__file__)
    path = path[:-16]
    path = path + '\Client'
    print(path)
    shutil.copy(f'{t}\InnocentBotClient\Client', f'{path}')
    # Remove temporary dir
    shutil.rmtree(t)

os.chdir('Client')
os.system('python3 InnocentBotClient.py')