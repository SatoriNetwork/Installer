''' 
this is version 2 of the installer/runner. Version 1 created an exe from the 
installer, and ran batch commands, and had those batch commands call out to the
web to get the lastest version. all of these activities were flagged by anti-
virus so windows thought it was uspicious.

so we've had to simplify it down massively. Now the installer is the runner.
each time it runs, it checks to see if the folders are installed in the correct
location, if not it creates them. Then it runs the docker container. that's it.
the :latest version of the docker container is always the one it runs.

simple.

it turns out anything created with pyinstaller is flagged by anti-virus at least
on virustotal.com so, we'll need re-write this someday, but for now I think this
wont be flagged by like windows defender so it might suffice for beta testing.
'''

# python3
# https://stackoverflow.com/questions/12059509/create-a-single-executable-from-a-python-project

# upgrade Process:
# 0. modify Satori/Neuron, make a new image put that image version in here (TAG)
# -. (deprecated) if scripts/*.py modified, follow instructions within to update the hash
# 2. push Satori/Neuron to github, and satorinet/satorineuron=vX image to docker hub
# 3. modify this file
# 4. recreate satori.exe `pyinstaller --onefile --icon=favicon256.ico satori.py`
#   a. ( cd C:\repos\Satori\Installer\windows\runner )
#   b. ( PyInstaller: 5.9.0, Python: 3.11.3   )
# 5. copy satori.exe from /dist to satoricentral/server/static/download/
#   a. cp ./dist/satori.exe /repos/Satori/Central/satoricentral/server/static/download/satori.exe
# 6. sign the downloadedable exe with signtool.exe using the smartcard (CMD):
#   a. cd "C:\Program Files (x86)\Windows Kits\10\App Certification Kit"
#   b. signtool sign /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256
#      C:\repos\Satori\Central\satoricentral\server\static\download\satori.exe
# 7. push SatoriInstaller and SatoriServer, `stop`, `pull`, `restart` on server
from typing import Union
# runner
import os
import time
import getpass
import subprocess
import docker  # pip install docker
import threading
from synapse import runSynapse


# ################################ runner #####################################


LOCAL_URL = 'http://127.0.0.1:24601'
USER_NAME = getpass.getuser()
INSTALL_DIR = os.path.join(os.environ.get('APPDATA', 'C:\\'), 'Satori')
INITIATOR_DIR = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME


def welcome():
    print(f"""
                                       @@@@                                      
                          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@                         
                     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    
                 @@@@@@@@@@@@@@@@@@@         @@@@@@@@@   @@@@@@@@                
              @@@@@@@@@@@@@                          @@@@@  @@@@@@@             
           @@@@@@@@@@@@                                   @@@ @@@@@@@@          
         @@@@@@@@@@                                          @@@@@@@@@@@        
       @@@@@@@@@@                                               @@@@@@@@@@      
      @@@@@@@@                                                    @@@@@@@@@     
    @@@@@@@@@                                                       @ @@@@@@    
   @@@@@@@@                                                          @@@@@@@@@  
  @@@@@@@@                                                            @ @@@@@@  
  @@@@@@@@                                                               @@@@@@ 
 @@@@@@@@                                                                 @@@@@@
 @@@@@@@@                                                                 @@@@@@
 @@@@@@@                                                                   @ @@@
 @@@@@@@                                                                   @ @@@
 @@@@@@@                                 @                                @@ @@@
 @@@@@@@@                              @@@@@                              @@ @@@
 @@@@@@@@                             @@@@@@@                            @@ @@@@
  @@@@@@@@                            @@@@@@@                           @@ @@@ 
   @@@@@@@@                            @@@@@                           @@ @@@  
    @@@@@@@@                        @@@@@@@@@@@                       @@ @@@   
     @@@@@@@@@                    @@@@@@@@@@@@@@@                     @ @@@    
      @@@@@@@@@@                  @@@@@@@@@@@@@@@                    @ @@@     
        @@@@@@@@@@               @@@ @@@@@@@@@ @@@                    @@@       
          @@@@@@@@@@@            @@@ @@@@@@@@@ @@@                   @@         
            @@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@             @           
               @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      @@                 
                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@@@@ @                 
                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    
                            @@@@@@@@@@@@@@@@@@@@@@@@@@@                        
                                      
###############################################################################
####                                                                       ####
####                      Starting the Satori Neuron                       ####
####                                                                       ####
####     Please don't close this window or the Satori Neuron will stop.    ####
####           The Satori UI will open in your web browser soon.           ####
####                                                                       ####
####                        {LOCAL_URL}                         ####
####                                                                       ####
###############################################################################

Please make sure that Docker is already running. 
And hold tight, this may take several minutes...

""")
####          If you don't want to see Satori Neuron engine logs           ####
####    you can close this window after Satori opens in a web browser.     ####


def setupDirectory():
    ''' setup directories to mount to /wallet, /config, /data, /models '''
    os.makedirs(os.path.join(INSTALL_DIR, 'wallet'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'config'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'models'), exist_ok=True)


def setupStartup():
    ''' will setup a run script in startup folder to wait 5 minutes then run the satori container'''
    def ui(installed=False) -> bool:
        if installed:
            print('Satori Installed to:', INSTALL_DIR)
            print('Satori Startup file:', batchPath, '\n')
            return True  # recreate links in case they download a new installer
        print('Installing Satori to:', INSTALL_DIR)
        print('Installing Satori Startup file:', batchPath, '\n')
        return True

    def createLinks():
        import os
        import sys
        import win32com.client
        import pythoncom

        def createShortcut(target: str, path: str):
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
            return shell, shortcut

        # Initialize COM
        pythoncom.CoInitialize()

        try:
            target = sys.executable
            startup = os.path.join(
                os.path.join(
                    os.environ['APPDATA'],
                    r'Microsoft\Windows\Start Menu\Programs\Startup'),
                'Satori.lnk')
            shell, shortcut = createShortcut(target, path=startup)
            desktopPath = os.path.join(os.environ['USERPROFILE'], 'desktop')
            if not os.path.exists(desktopPath):
                desktopPath = shell.SpecialFolders('Desktop')
            desktop = os.path.join(desktopPath, 'Satori.lnk')
            createShortcut(target, path=desktop)
        finally:
            # Release COM objects
            shortcut = None
            shell = None

        # Uninitialize COM
        pythoncom.CoUninitialize()

    batchPath = os.path.join(INITIATOR_DIR, 'Satori.lnk')
    if ui(installed=os.path.exists(batchPath)):
        createLinks()


def getVersion() -> str:
    import requests
    response = requests.get('https://satorinet.io/version/docker')
    if response.status_code == 200:
        return response.text
    return 'latest'


def pullSatoriNeuron(version: str) -> subprocess.Popen:
    return subprocess.Popen(
        f'docker pull satorinet/satorineuron:{version}',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def startSatoriNeuronNative(version: str) -> subprocess.Popen:
    return subprocess.Popen((
        r'docker run --rm -it --name satorineuron '
        r'-p 24601:24601 -p 24602:4001 -p 24603:5001 -p 24604:23384 '
        r'-v %APPDATA%\Satori\wallet:/Satori/Neuron/wallet '
        r'-v %APPDATA%\Satori\config:/Satori/Neuron/config '
        r'-v %APPDATA%\Satori\data:/Satori/Neuron/data '
        r'-v %APPDATA%\Satori\models:/Satori/Neuron/models '
        f'--env SATORI_RUN_MODE=prod satorinet/satorineuron:{version} ./start.sh'),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def startSatoriNeuronThread(version: str) -> threading.Thread:
    def dockerCommand():
        version = getVersion()
        with subprocess.Popen(
            (
                r'docker run --rm -it --name satorineuron '
                r'-p 24601:24601 -p 24602:4001 -p 24603:5001 -p 24604:23384 '
                r'-v %APPDATA%\Satori\wallet:/Satori/Neuron/wallet '
                r'-v %APPDATA%\Satori\config:/Satori/Neuron/config '
                r'-v %APPDATA%\Satori\data:/Satori/Neuron/data '
                r'-v %APPDATA%\Satori\models:/Satori/Neuron/models '
                f'--env SATORI_RUN_MODE=prod '
                f'satorinet/satorineuron:{version} ./start.sh'),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        ) as proc:
            for line in iter(proc.stdout.readline, ''):
                print(line, end='')

    thread = threading.Thread(target=dockerCommand, args=(version,))
    thread.start()
    return thread


def startSatoriNeuron():
    # '''
    # docker run --rm -it --name satorineuron
    #    -p 24601:24601 -p 24602:4001 -p 24603:5001 -p 24604:23384
    #    -v %APPDATA%\Satori\wallet:/Satori/Neuron/wallet
    #    -v %APPDATA%\Satori\config:/Satori/Neuron/config
    #    -v %APPDATA%\Satori\data:/Satori/Neuron/data
    #    -v %APPDATA%\Satori\models:/Satori/Neuron/models
    #    -e IPFS_PATH=/Satori/Neuron/config/ipfs
    #    --env SATORI_RUN_MODE=prod
    #    satorinet/satorineuron:v1
    #    ./start.sh
    # docker run --rm -it --name satorineuron
    #    -p 24601:24601 -p 24602:4001 -p 24603:5001 -p 24604:23384
    #    -v c:\repos\Satori\Neuron:/Satori/Neuron
    #    -v c:\repos\Satori\Lib:/Satori/Lib
    #    -v c:\repos\Satori\Wallet:/Satori/Wallet
    #    -v c:\repos\Satori\Engine:/Satori/Engine
    #    -e IPFS_PATH=/Satori/Neuron/config/ipfs
    #    --env SATORI_RUN_MODE=prod
    #    satorinet/satorineuron:v1 ./start.sh
    # '''
    client = docker.from_env()
    try:
        client.containers.run(
            image='satorinet/satorineuron:v1',
            command='/Satori/Neuron/satorineuron/web/start.sh',
            name='satorineuron',
            ports={
                '24601/tcp': '24601', '24602/tcp': '4001',
                '24603/tcp': '5001/tcp', '24604/tcp': '23384'},
            # volumes=[
            #    '%APPDATA%\Satori\wallet:/Satori/Neuron/wallet',
            #    '%APPDATA%\Satori\config:/Satori/Neuron/config',
            #    '%APPDATA%\Satori\data:/Satori/Neuron/data',
            #    '%APPDATA%\Satori\models:/Satori/Neuron/models',
            # ]
            volumes={
                '/repos/Satori/Neuron': {'bind': '/Satori/Neuron', 'mode': 'rw'},
                '/repos/Satori/Lib': {'bind': '/Satori/Lib', 'mode': 'rw'},
                '/repos/Satori/Wallet': {'bind': '/Satori/Wallet', 'mode': 'rw'},
                '/repos/Satori/Engine': {'bind': '/Satori/Engine', 'mode': 'rw'}},
            # environment={["SATORI_RUN_MODE=prod"]},
            environment={'SATORI_RUN_MODE': 'prod',
                         'IPFS_PATH': '/Satori/Neuron/config/ipfs'},
            network_mode='bridge',
            privileged=True,
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
            # detach=True,
            # cpu_count=16
            # cpu_percent=90
        )
    except Exception as e:
        print('Error starting Satori Neuron:', e)
        print('please restart the docker daemon (Docker Desktop) and try again.')
        _awaitSeconds(30)
        exit()


def openInBrowserNative():
    os.system(f'start {LOCAL_URL}')


def openInBrowser():
    import webbrowser
    try:
        # For Windows, specifying the default browser explicitly
        browser = webbrowser.get('windows-default')
        browser.open_new_tab(LOCAL_URL)
    except webbrowser.Error:
        print("Could not locate default browser.")
        webbrowser.open(LOCAL_URL)


def printOutDisplay(process: subprocess.Popen) -> str:
    errorMsg = ''
    for line in iter(process.stdout.readline, b''):
        line_decoded = line.decode('utf-8').rstrip()
        print(line_decoded)
        # 'docker: error during connect: this error may indicate that the docker daemon is not running: Post "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/containers/create?name=satorineuron": open //./pipe/docker_engine: The system cannot find the file specified.'
        # "See 'docker run --help'."
        if line_decoded.startswith('docker: error during connect'):
            errorMsg = '\n\nSatori could not start, Docker daemon may not be running. You might have to start Docker Desktop, and try again.\n\n'
    process.wait()
    print(errorMsg)
    return errorMsg


def _awaitSeconds(
    seconds: int,
    show=True,
    msg='this windows will close in {} seconds...',
):
    if show:
        if msg is not None:
            print(msg.format(seconds))
        for _ in range(seconds):
            print('.', end='')
            time.sleep(1)
    else:
        time.sleep(seconds)


def startDocker() -> subprocess.Popen:
    return subprocess.Popen((
        r'start "docker" "C:\Program Files\Docker\Docker\Docker Desktop.exe"'),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# ################################# entry #####################################


def runHost():
    hostThread = threading.Thread(target=runSynapse, daemon=True)
    hostThread.start()


def installSatori():
    welcome()
    setupDirectory()
    setupStartup()


def runSatori(iteration: int = 0):
    time.sleep(60)
    version = getVersion()
    process = pullSatoriNeuron(version)
    time.sleep(10)
    errorMsg = printOutDisplay(process)
    while errorMsg != '':
        _ = startDocker()
        time.sleep(60)
        process = pullSatoriNeuron(version)
        errorMsg = printOutDisplay(process)
    time.sleep(60*2)
    openInBrowserNative()
    process = startSatoriNeuronNative(version)
    time.sleep(10)
    errorMsg = printOutDisplay(process)
    print(errorMsg)
    time.sleep(10)
    if errorMsg != '':
        if iteration > 10:
            print('15-minute timeout, docker not detected, too many attempts, giving up.')
            time.sleep(60)
            exit()
        runSatori(iteration+1)


def runForever():
    installSatori()
    runHost()
    runSatori()


runForever()
