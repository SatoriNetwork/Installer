import subprocess


def run_in_terminal():
    apple_script = '''
    tell application "Terminal"
        do script "/Applications/Satori.app/Contents/MacOS/Satori"
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script])


if __name__ == "__main__":
    run_in_terminal()
