import subprocess


def FlagsForFile( filename, **kwargs ):
    flags = ['-x', 'c', '-Wall', '-Wextra', '-Werror']
    flags.extend(subprocess.check_output('python3.6-config --cflags', shell=True).split())
    return { 'flags': flags }

