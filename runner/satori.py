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
# 1. push Satori/Neuron to github, and satorinet/satorineuron=vX image to docker hub
# 2. modify this file
# 3. recreate satori.exe `pyinstaller --onefile --icon=favicon256.ico satori.py`
#    a. ( cd C:\repos\Satori\installer\runner )
#    b. ( PyInstaller: 5.9.0, Python: 3.11.3   )
# 4. copy satori.exe from /dist to satoricentral/server/web/static/download/
# 5. push SatoriInstaller and SatoriServer, `stop`, `pull`, `restart` on server

# runner
import os
import time
import getpass
import subprocess
import docker  # pip install docker
import threading

# host
import traceback
import requests
import aiohttp
import datetime as dt
import asyncio
import socket
import ast


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
    ''' setup directory to mount to /wallet and /config and /data and /models'''
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
        # r'-v c:\repos\Satori\Neuron:/Satori/Neuron '
        # r'-v c:\repos\Satori\Lib:/Satori/Lib '
        # r'-v c:\repos\Satori\Rendezvous:/Satori/Rendezvous '
        # r'-v c:\repos\Satori\Wallet:/Satori/Wallet '
        # r'-v c:\repos\Satori\Engine:/Satori/Engine '
        r'-e IPFS_PATH=/Satori/Neuron/config/ipfs '
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
                # r'-v c:\repos\Satori\Neuron:/Satori/Neuron '
                # r'-v c:\repos\Satori\Lib:/Satori/Lib '
                # r'-v c:\repos\Satori\Rendezvous:/Satori/Rendezvous '
                # r'-v c:\repos\Satori\Wallet:/Satori/Wallet '
                # r'-v c:\repos\Satori\Engine:/Satori/Engine '
                r'-e IPFS_PATH=/Satori/Neuron/config/ipfs '
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
    #    -v c:\repos\Satori\Rendezvous:/Satori/Rendezvous
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
                '/repos/Satori/Rendezvous': {'bind': '/Satori/Rendezvous', 'mode': 'rw'},
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

# ################################ HOST.py ####################################


''' 
we discovered that udp hole punching inside docker containers is not always 
possible because of the way the docker nat works. we thought it was.
this host script is meant to run on the host machine. 
it will establish a sse connection with the flask server running inside
the container. it will handle the UDP hole punching, passing data between the
flask server and the remote peers.
'''
# from requests_toolbelt.multipart.encoder import MultipartEncoder


def greyPrint(msg: str):
    return print(
        "\033[90m"  # grey
        + msg +
        "\033[0m"  # reset
    )


class SseTimeoutFailure(Exception):
    '''
    sometimes we the connection to the neuron fails and we want to identify 
    that failure easily with this custom exception so we can handle reconnect.
    '''

    def __init__(self, message='Sse timeout failure', extra_data=None):
        super().__init__(message)
        self.extra_data = extra_data

    def __str__(self):
        return f"{self.__class__.__name__}: {self.args[0]} (Extra Data: {self.extra_data})"


class UDPRelay():
    def __init__(self, ports: dict[int, list[tuple[str, int]]]):
        ''' {localport: [(remoteIp, remotePort)]} '''
        self.ports: dict[int, list[tuple[str, int]]] = ports
        self.socks: list[socket.socket] = []
        self.peerListeners = []
        self.neuronListeners = []
        self.loop = asyncio.get_event_loop()

    @staticmethod
    def satoriUrl(endpoint='') -> str:
        return 'http://localhost:24601/udp' + endpoint

    @property
    def listeners(self) -> list:
        return self.peerListeners + self.neuronListeners

    async def neuronListener(self, url: str):
        # timeout = aiohttp.ClientTimeout(total=None, sock_read=3600)
        timeout = aiohttp.ClientTimeout(total=None, sock_read=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    async for line in response.content:
                        if line.startswith(b'data:'):
                            self.relayToPeer(line.decode('utf-8')[5:].strip())
            except asyncio.TimeoutError:
                greyPrint("SSE connection timed out...")
                raise SseTimeoutFailure()

    def cancelNeuronListener(self):
        for listener in self.neuronListeners:
            listener.cancel()
        self.neuronListeners = []

    def initNeuronListener(self, url: str):
        if (len(self.neuronListeners) > 0):
            self.cancelNeuronListener()
        self.neuronListeners = [asyncio.create_task(self.neuronListener(url))]

    def relayToPeer(self, messages: str):
        def parseMessages() -> list[tuple[int, str, int, bytes]]:
            ''' 
            parse messages into a 
            list of [tuples of (tuples of local port, and data)]
            '''
            try:
                literal: list[tuple[int, str, int, bytes]] = (
                    ast.literal_eval(messages))
                if isinstance(literal, list) and len(literal) > 0:
                    return literal
            except Exception as e:
                greyPrint(f'unable to parse messages: {messages}, error: {e}')
            return []

        def parseMessage(msg) -> tuple[int, str, int, bytes]:
            ''' localPort, remoteIp, remotePort, data '''
            if (
                isinstance(msg, tuple) and
                len(msg) == 4 and
                isinstance(msg[0], int) and
                isinstance(msg[1], str) and
                isinstance(msg[2], int) and
                isinstance(msg[3], bytes)
            ):
                return msg[0], msg[1], msg[2], msg[3]
            return None, None, None, None

        for msg in parseMessages():
            localPort, remoteIp, remotePort, data = parseMessage(msg)
            if localPort is None:
                return
            # greyPrint('parsed:',
            #      'localPort:', localPort, 'remoteIp:', remoteIp,
            #      'remotePort', remotePort, 'data', data)
            sock = self.getSocketByLocalPort(localPort)
            if sock is None:
                return
            UDPRelay.speak(sock, remoteIp, remotePort, data)

    def getSocketByLocalPort(self, localPort: int) -> socket.socket:
        for sock in self.socks:
            if UDPRelay.getLocalPort(sock) == localPort:
                return sock
        return None

    @staticmethod
    def getLocalPort(sock: socket.socket) -> int:
        return sock.getsockname()[1]

    async def listenTo(self, sock: socket.socket):
        while True:
            try:
                data, addr = await self.loop.sock_recvfrom(sock, 1024)
                self.handle(sock, data, addr)
            except Exception as e:
                greyPrint('listenTo erorr:', e)
                break
        # close?

    async def initSockets(self):
        def bind(localPort: int) -> socket.socket | None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.bind(('0.0.0.0', localPort))
                sock.setblocking(False)
                return sock
            except Exception as e:
                greyPrint('unable to bind to port', localPort, e)
            return None

        def punch(sock: socket.socket, remoteIp: str, remotePort: int):
            sock.sendto(b'punch', (remoteIp, remotePort))

        def createAllSockets():
            self.socks = []
            for localPort, remotes in self.ports.items():
                sock = bind(localPort)
                if sock is not None:
                    self.socks.append(sock)
                    for remoteIp, remotePort in remotes:
                        punch(sock, remoteIp, remotePort)

        createAllSockets()

    async def listen(self):
        self.initNeuronListener(UDPRelay.satoriUrl('/stream'))
        self.peerListeners += [
            asyncio.create_task(self.listenTo(sock))
            for sock in self.socks]
        return await asyncio.gather(*self.listeners)

    @staticmethod
    def speak(
        sock: socket.socket,
        remoteIp: str,
        remotePort: int,
        data: bytes
    ):
        greyPrint('sending to', remoteIp, remotePort, data)
        sock.sendto(data, (remoteIp, remotePort))

    async def cancel(self):
        ''' cancel all listen_to_socket tasks '''
        for task in self.peerListeners:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.peerListeners = []

    async def shutdown(self):

        def close():
            ''' close all sockets '''
            for sock in self.socks:
                sock.close()

        await self.cancel()
        close()
        self.socks = []

    def handle(self, sock: socket.socket, data: bytes, addr: tuple[str, int]):
        ''' send to flask server with identifying information '''
        greyPrint(
            f"Received {data} from {addr} on {UDPRelay.getLocalPort(sock)}")
        # # this isn't ideal because it converts data to a string automatically
        # r = requests.post(
        #    UDPRelay.satoriUrl('/message'),
        #    json={
        #        'data': data,
        #        'address': {
        #            'remote': {'ip': addr[0], 'port': addr[1]},
        #            'local': {'port': UDPRelay.getLocalPort(sock)}}})

        # # this is probably proper but requires an additional package
        # # and we want this to be as light as possible
        # multipart_data = MultipartEncoder(
        #    fields={
        #        # JSON part
        #        'json_data': ('json_data', '{"address": {"remote": {"ip": "' + addr[0] + '", "port": ' + str(addr[1]) + '}, "local": {"port": ' + UDPRelay.getLocalPort(sock) + '}}}', 'application/json'),
        #        # Byte data part
        #        'byte_data': ('filename', data, 'application/octet-stream')
        #    }
        # )
        # r = requests.post(
        #    UDPRelay.satoriUrl('/message'),
        #    data=multipart_data,
        #    headers={'Content-Type': multipart_data.content_type})
        if data in [b'punch', b'payload']:
            greyPrint('skipping punch or payload')
            return
        requests.post(
            UDPRelay.satoriUrl('/message'),
            data=data,
            headers={
                'Content-Type': 'application/octet-stream',
                'remoteIp': addr[0],
                'remotePort': str(addr[1]),
                'localPort': str(UDPRelay.getLocalPort(sock))})


async def main():
    def seconds() -> float:
        ''' calculate number of seconds until the start of the next hour'''
        now = dt.datetime.now()
        nextHour = (now + dt.timedelta(hours=1)).replace(
            minute=0,
            second=0,
            microsecond=0)
        return (nextHour - now).total_seconds()

    def getPorts() -> dict[int, list[tuple[str, int]]]:
        ''' gets ports from the flask server '''
        r = requests.get(UDPRelay.satoriUrl('/ports'))
        # greyPrint(r.status_code)
        # greyPrint(r.text)
        if r.status_code == 200:
            try:
                ports: dict = ast.literal_eval(r.text)
                validatedPorts = {}
                # greyPrint(ports)
                # greyPrint('---')
                for localPort, remotes in ports.items():
                    # greyPrint(localPort, remotes)
                    if (
                        isinstance(localPort, int) and
                        isinstance(remotes, list)
                    ):
                        # greyPrint('valid')
                        validatedPorts[localPort] = []
                        # greyPrint(validatedPorts)
                        for remote in remotes:
                            # greyPrint('remote', remote)
                            if (
                                isinstance(remote, tuple) and
                                len(remote) == 2 and
                                isinstance(remote[0], str) and
                                isinstance(remote[1], int)
                            ):
                                # greyPrint('valid---')
                                validatedPorts[localPort].append(remote)
                return validatedPorts
            except (ValueError, TypeError):
                greyPrint('Invalid format of received data')
                return {}
        return {}

    def triggerReconnect() -> None:
        ''' tells neuron to reconnect to rendezvous (to refresh ports) '''
        r = requests.get(UDPRelay.satoriUrl('/reconnect'))
        if r.status_code == 200:
            greyPrint('reconnected to rendezvous server')

    async def waitForNeuron():
        notified = False
        while True:
            try:
                r = requests.get(UDPRelay.satoriUrl('/ports'))
                if r.status_code == 200:
                    if notified:
                        greyPrint('established connection to Satori Neuron')
                    return
            except Exception as _:
                if not notified:
                    greyPrint('waiting for Satori Neuron to start')
                    notified = True
            await asyncio.sleep(1)

    while True:
        try:
            reconnect = True
            udpRelay = UDPRelay(getPorts())
            await udpRelay.initSockets()
            try:
                secs = seconds()
                await asyncio.wait_for(udpRelay.listen(), secs)
            except asyncio.TimeoutError:
                greyPrint('udpRelay cycling')
            except SseTimeoutFailure:
                greyPrint("...attempting to reconnect to neuron...")
                # udpRelay.cancelNeuronListener()
                # udpRelay.initNeuronListener(UDPRelay.satoriUrl('/stream'))
        except requests.exceptions.ConnectionError as e:
            # greyPrint(f'An error occurred: {e}')
            await waitForNeuron()
            reconnect = False
        except Exception as e:
            greyPrint(f'An error occurred: {e}')
            traceback.print_exc()
        try:
            if reconnect:
                triggerReconnect()
            udpRelay.cancelNeuronListener()
            await udpRelay.cancel()
            await udpRelay.shutdown()
        except Exception as _:
            pass


# ################################# entry #####################################

def runHost():
    asyncio.run(main())


def installSatori():
    welcome()
    setupDirectory()
    setupStartup()


def runSatori():
    # # process attempt - blocking, trying a threaded version
    version = getVersion()
    process = pullSatoriNeuron(version)
    time.sleep(10)
    errorMsg = printOutDisplay(process)
    if errorMsg != '':
        _ = startDocker()
        time.sleep(60)
        process = pullSatoriNeuron(version)
        errorMsg = printOutDisplay(process)
        print(errorMsg)
    process = startSatoriNeuronNative(version)
    time.sleep(10)
    errorMsg = printOutDisplay(process)
    openInBrowserNative()
    print(errorMsg)
    time.sleep(10)

    # # threading attempt - actaully we just threaded host instead
    # process = startSatoriNeuronNative()
    # time.sleep(60)
    # openInBrowserNative()
    # errorMsg = printOutDisplay(process)
    # if errorMsg != '':
    #    process = startDocker()
    #    printOutDisplay(process)
    #    time.sleep(60)
    #    process = startSatoriNeuronNative()
    #    # printOutDisplay(process)
    # _awaitSeconds(60, msg=None)


def runForever():
    installSatori()
    hostThread = threading.Thread(target=runHost, daemon=True)
    hostThread.start()
    runSatori()


runForever()
