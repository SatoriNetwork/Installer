# build instructions

## requirements

visual studio build tools
https://visualstudio.microsoft.com/downloads/

download cmake latest release version
https://cmake.org/download/
...-windows-x86_64.msi

install vscode extensions from microsoft:
CMake Tools
C/C++


## open the folder in file explorer

C:\repos\Satori\Installer\windows\runner-cpp
"Open in VS Code"

click on Cmake extension,
and click on select kit,
and select Visual Studio Build Tools 2022 Windows AMD64

for debug:
runner-cpp/.vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": []
        }
    ]
}

## notes

if you change the CMakeLists.txt file you have to:
CMake Ext -> Project Outline -> Configure All Projects
