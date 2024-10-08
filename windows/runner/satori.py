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
# 4. recreate satori.exe (using PyInstaller: 5.9.0, Python: 3.11.3):
# 5. copy satori.exe from /dist to satoricentral/server/static/download/:
# 6. copy synapse.py from ./ to satoricentral/server/static/download/:
#   ```
#   cd C:\repos\Satori\Installer\windows\runner
#   pyinstaller --onefile --icon=favicon256.ico satori.py
#   cp ./dist/satori.exe /repos/Satori/Central/satoricentral/server/static/download/satori.exe
#   cd C:\repos\Satori\Central
#   git status
#   start cmd.exe
#   ```
# 6. sign the downloadedable exe with signtool.exe using the smartcard (CMD):
#   ```
#   cd "C:\Program Files (x86)\Windows Kits\10\App Certification Kit"
#   signtool sign /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 C:\repos\Satori\Central\satoricentral\server\static\download\satori.exe
#   ```
# 7. push SatoriInstaller and SatoriServer, `stop`, `pull`, `restart` on server
# runner
import os
import sys
import time
import shutil
import getpass
import subprocess
import threading
from satorisynapse.lib.domain import SYNAPSE_PORT
from satorisynapse.synapse.asynchronous import runSynapse, silentlyWaitForNeuron


# ################################ runner #####################################


LOCAL_URL = 'http://127.0.0.1:24601'
USER_NAME = getpass.getuser()
INSTALL_DIR = os.path.join(os.environ.get('APPDATA', 'C:\\'), 'Satori')
INITIATOR_DIR = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
RESTART_PATH = os.path.join(INSTALL_DIR, 'satori.exe')
IMAGE_VERSION = 'v1'


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
    '''
    will setup a run script in startup folder to wait 5 minutes then run the
    satori container
    '''
    def ui(installed=False) -> bool:
        if installed:
            print('Satori Installed to:', INSTALL_DIR)
            print('Satori Startup file:', linkPath, '\n')
            return False
        print('Installing Satori to:', INSTALL_DIR)
        print('Installing Satori Startup file:', linkPath, '\n')
        return True

    def copyToInstallDir():
        source = sys.executable
        try:
            global RESTART_PATH
            RESTART_PATH = os.path.join(INSTALL_DIR, 'satori.exe')
            shutil.copy(source, RESTART_PATH)
            return RESTART_PATH
        except Exception as _:
            return source

    def createLinks():
        import os
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
            target = copyToInstallDir()
            startup = os.path.join(
                os.environ['APPDATA'],
                r'Microsoft\Windows\Start Menu\Programs\Startup',
                'Satori.lnk')
            shell, _shortcut = createShortcut(target, path=startup)
            desktopPath = os.path.join(os.environ['USERPROFILE'], 'desktop')
            if not os.path.exists(desktopPath):
                desktopPath = shell.SpecialFolders('Desktop')
            desktop = os.path.join(desktopPath, 'Satori.lnk')
            createShortcut(target, path=desktop)
        finally:
            # Release COM objects
            _shortcut = None
            shell = None

        # Uninitialize COM
        pythoncom.CoUninitialize()

    linkPath = os.path.join(INITIATOR_DIR, 'Satori.lnk')
    # if ui(installed=os.path.exists(linkPath)):
    #    createLinks()
    # actually, always recreate links, in case they download a new installer:
    ui(installed=os.path.exists(linkPath))
    createLinks()


def setVersion() -> str:
    global IMAGE_VERSION
    import requests
    response = requests.get('https://satorinet.io/version/docker')
    if response.status_code == 200:
        IMAGE_VERSION = response.text
    else:
        IMAGE_VERSION = 'latest'
    return IMAGE_VERSION


def removeDanglingImages():
    command = (
        'docker rmi $('
        'docker images -q '
        '-f "reference=satorinet/satorineuron" '
        '-f "dangling=true")')
    try:
        _ = subprocess.run(
            ["powershell", "-Command", command], capture_output=True, text=True)
        # if result.stderr:
        #    print("Error:", result.stderr)
        # else:
        #    print("Output:", result.stdout)
    except Exception as e:
        print("unable to remove old satori images automatically:", e)


def pullSatoriNeuron(version: str) -> subprocess.Popen:
    return subprocess.Popen(
        f'docker pull satorinet/satorineuron:{version}',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def getConfigEnv(configPath: str) -> str:
    if os.path.exists(configPath):
        with open(configPath, mode='r') as f:
            for line in f:
                if line.startswith('env:'):
                    return line.split(':')[1].strip()
    return 'prod'


def startSatoriNeuron(version: str) -> subprocess.Popen:
    return subprocess.Popen((
        'docker run --rm -it --name satorineuron '
        '-p 24601:24601 '
        f'-v "{os.path.join(INSTALL_DIR, """wallet""")}:/Satori/Neuron/wallet" '
        f'-v "{os.path.join(INSTALL_DIR, """config""")}:/Satori/Neuron/config" '
        f'-v "{os.path.join(INSTALL_DIR, """data""")}:/Satori/Neuron/data" '
        f'-v "{os.path.join(INSTALL_DIR, """models""")}:/Satori/Neuron/models" '
        f'--env ENV="{getConfigEnv(os.path.join(INSTALL_DIR, """config""", """config.yaml"""))}" '
        f'satorinet/satorineuron:{version} ./start.sh'),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def openInBrowser():
    os.system(f'start {LOCAL_URL}')


def printOutDisplay(process: subprocess.Popen) -> str:
    errorMsg = ''
    for line in iter(process.stdout.readline, b''):
        line_decoded = line.decode('utf-8').rstrip()
        print(line_decoded)
        # 'docker: error during connect:
        # this error may indicate that the docker daemon is not running:
        # Post "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/containers/create?name=satorineuron":
        # open //./pipe/docker_engine: The system cannot find the file specified.'
        # "See 'docker run --help'."
        if line_decoded.startswith('docker: error during connect'):
            errorMsg = (
                '\n\nSatori could not start, Docker daemon may not be running. '
                'You might have to start Docker Desktop, and try again.\n\n')
    process.wait()
    print(errorMsg)
    return errorMsg


def startDocker() -> subprocess.Popen:
    return subprocess.Popen((
        r'start "docker" "C:\Program Files\Docker\Docker\Docker Desktop.exe"'),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def waitForDockerDaemon():
    x = 60*10
    while x > 0:
        result = subprocess.run(
            ['docker', 'info'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            print("Docker daemon is running.")
            break
        if x % 60 == 0:
            print("Waiting for Docker daemon to start...")
        time.sleep(1)
        x -= 1


# ################################# entry #####################################


def runHost():
    hostThread = threading.Thread(target=runSynapse, daemon=True, args=(
        SYNAPSE_PORT,
        IMAGE_VERSION,
        RESTART_PATH,
        INSTALL_DIR,
    ))
    hostThread.start()
    return hostThread


def installSatori():
    welcome()
    setupDirectory()
    setupStartup()
    setVersion()


def openSatori():

    def waitThenOpen():
        silentlyWaitForNeuron()
        openInBrowser()

    openSatoriThread = threading.Thread(target=waitThenOpen, daemon=True)
    openSatoriThread.start()
    return openSatoriThread


def runSatori(
    hostThread: threading.Thread = None,
    openSatoriThread: threading.Thread = None
):
    def startSatori():
        process = startDocker()
        errorMsg = printOutDisplay(process)
        waitForDockerDaemon()
        if errorMsg != '':
            return False
        process = pullSatoriNeuron(IMAGE_VERSION)
        errorMsg = printOutDisplay(process)
        if errorMsg != '':
            return False
        removeDanglingImages()
        process = startSatoriNeuron(IMAGE_VERSION)
        errorMsg = printOutDisplay(process)
        if errorMsg != '':
            return False
        return True

    iteration: int = 0
    while startSatori():
        time.sleep(60)
        iteration += 1
        if iteration > 10:
            print('timeout, unable to start Docker, unable to start Satori.')
            time.sleep(60)
            if hostThread is not None:
                hostThread.join()
            if openSatoriThread is not None:
                openSatoriThread.join()
            break


def runForever():
    installSatori()
    runSatori(runHost(), openSatori())


runForever()
