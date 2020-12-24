import os

from AktuelFinder.AktuelFinder import AktuelFinder


def clear():  # https://stackoverflow.com/a/4810595
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


if __name__ == "__main__":
    app = AktuelFinder()
    while True:
        app.show_summary()
        app.command()
        clear()  # when running on command window
