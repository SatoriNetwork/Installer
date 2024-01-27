# Installation and Setup Guide for Satori on macOS:

## Install Docker:
Download Docker for Mac from https://desktop.docker.com/mac/main/arm64/Docker.dmg

## Install Python and Dependencies:

#### Install Homebrew:
You'll need Homebrew to install Python. If you don't have Homebrew you can install it with this commands:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Install pyenv
Now you can install Python>=3.8 and pyenv:
```
brew install pyenv
Install Python 3.12:
pyenv install 3.12
```

## Download Satori:
Use curl to download Satori:
```
curl -o satori.zip https://satorinet.io/static/download/mac/satori.zip
```

## Unzip Satori:
Unzip the downloaded Satori package:
```
unzip satori.zip
```

## Install Satori:
Navigate to the '.satori' directory:
```
cd .satori
```

## Install Dependencies:  (replace these files with the ones provided earlier)
Run this command to install dependencies:
```
./install
```
If there are no errors, execute:
```
./install_service
```

Remember to start Docker (step 1) before proceeding with step 7. If Satori doesn't start automatically after a restart, you should find a desktop icon to launch it manually. (edited)