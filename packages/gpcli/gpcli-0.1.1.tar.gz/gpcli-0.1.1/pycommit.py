import subprocess, sys


def main():
    if len(sys.argv) < 2:
        print("Usage: gp \"commit message\"")
    else:
        msg = sys.argv[1]
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', msg])
        subprocess.run(['git', 'push'])
