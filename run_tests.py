import subprocess


def main():
    subprocess.call(['coverage', 'run', '-m', 'unittest',
                     'discover', '--start-directory', 'depq'])
    print('\n\nTests completed, checking coverage...\n\n')
    subprocess.call(['coverage', 'report', '-m'])
    input('\n\nPress enter to quit ')

if __name__ == '__main__':
    main()
