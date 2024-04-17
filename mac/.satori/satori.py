#!/usr/bin/env python3
''' 
for linux the runner will be a bit different, we don't have to compile it into
an executable because we can just run it as a python script. but we need to make
sure the environment is setup properly. we still need this script running 
outside the docker image because the docker images expects it to relay messages 
in the p2p network, even though we probably don't need to do that on linux. it
seemed to be only a problem with windows.

we're going to include requests and aiohttp with the script as well as a 
redundant requirements.txt file.
'''

# python3
# https://stackoverflow.com/questions/12059509/create-a-single-executable-from-a-python-project

# upgrade Process:
# 0. modify Satori/Neuron, make a new image put that image version in here (TAG)
# 1. if scripts/*.py modified, follow instructions within to update the hash
# 2. push Satori/Neuron to github, and satorinet/satorineuron=vX image to docker hub
# 3. modify this file
# 4. using windows linux subsystem (WSL) zip up all contents of satori folder:
# 5. copy to download static folder of Central:
#   ````
#   cd /mnt/c/repos/Satori/Installer/mac
#   rm -rf satori.zip
#   zip -r satori.zip .satori
#   cp /mnt/c/repos/Satori/Installer/mac/satori.zip /mnt/c/repos/Satori/Central/satoricentral/server/static/download/mac/
#   ````
# 6. push Installer and Central, `cycle` on server

import os
import getpass
import subprocess
import threading
import platform
from synapse import runSynapse, requests, waitForNeuron

# ################################ runner #####################################


LOCAL_URL = 'http://127.0.0.1:24601'
USER_NAME = getpass.getuser()
INSTALL_DIR = os.path.expanduser('~/.satori')


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
    ''' setup directory to mount to /wallet /config /data /models'''
    os.makedirs(os.path.join(INSTALL_DIR, 'wallet'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'config'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(INSTALL_DIR, 'models'), exist_ok=True)


def getVersion() -> str:
    response = requests.get('https://satorinet.io/version/docker')
    if response == '':
        return 'latest'
    return response


def pullSatoriNeuron(version: str) -> subprocess.Popen:
    return subprocess.Popen(
        f'docker pull satorinet/satorineuron:{version}',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def startSatoriNeuronNative(version: str) -> subprocess.Popen:
    return subprocess.Popen((
        r'docker run -t --rm --name satorineuron '
        r'-p 24601:24601 '
        f'-v {os.path.join(INSTALL_DIR, "wallet")}:/Satori/Neuron/wallet '
        f'-v {os.path.join(INSTALL_DIR, "config")}:/Satori/Neuron/config '
        f'-v {os.path.join(INSTALL_DIR, "data")}:/Satori/Neuron/data '
        f'-v {os.path.join(INSTALL_DIR, "models")}:/Satori/Neuron/models '
        r'--env SATORI_RUN_MODE=prod '
        f'satorinet/satorineuron:{version} ./start.sh'),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def openInBrowserNative():
    try:
        if platform.system() == 'Linux':
            # Check if the DISPLAY environment variable is set (common in GUI environments)
            if 'DISPLAY' in os.environ:
                waitForNeuron(notified=True)
                subprocess.run(['xdg-open', LOCAL_URL], check=True)
            else:
                print("GUI environment not detected. Unable to open URL.")
    except Exception as _:
        print("Could not locate web browser.")


def printOutDisplay(process: subprocess.Popen) -> str:
    errorMsg = ''
    for line in iter(process.stdout.readline, b''):
        line_decoded = line.decode('utf-8').rstrip()
        print(line_decoded, flush=True)
        # is this the correct error on mac?
        # 'docker: error during connect: this error may indicate that the docker daemon is not running: Post "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/containers/create?name=satorineuron": open //./pipe/docker_engine: The system cannot find the file specified.'
        # "See 'docker run --help'."
        if line_decoded.startswith('docker: error during connect'):
            errorMsg = '\n\nSatori could not start, Docker daemon may not be running. You might have to start Docker Desktop, and try again.\n\n'
    process.wait()
    print(errorMsg)
    return errorMsg

# ################################# entry #####################################


def runHost():
    hostThread = threading.Thread(target=runSynapse, daemon=True)
    hostThread.start()


def installSatori():
    welcome()
    setupDirectory()


def runSatori():
    version = getVersion()
    process = pullSatoriNeuron(version)
    errorMsg = printOutDisplay(process)
    if errorMsg != '':
        print(
            'Error encountered. '
            'Docker daemon may not be running. '
            'Please ensure Docker is running and try again.')
        return
    process = startSatoriNeuronNative(version)
    errorMsg = printOutDisplay(process)
    if errorMsg != '':
        print("Error occurred while starting or running Satori Neuron.")
    openInBrowserNative()


def runForever():
    installSatori()
    runHost()
    runSatori()


runForever()
