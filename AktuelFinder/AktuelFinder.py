import sys
from multiprocessing import Pool

import requests

from .markets.A101Aktuel import A101Aktuel
from .markets.BimAktuel import BimAktuel
from .markets.SokAktuel import SokAktuel
from .operations.AktuelDB import AktuelDB

if not sys.warnoptions:  # https://stackoverflow.com/questions/49939085/xref-table-not-zero-indexed-id-numbers-for-objects-will-be-corrected-wont-con
    import warnings

    warnings.simplefilter("ignore")


class AktuelFinder:

    def __init__(self):
        self.exception = False
        self.markets = {'BİM': BimAktuel, 'A101': A101Aktuel, 'ŞOK': SokAktuel}
        self.aktuel_db = AktuelDB('aktuels')
        self.active_aktuels = {}
        self.still_active_aktuels = {}
        self.expired_aktuels = {}
        self.new_aktuels = {}

    def get_aktuels(self):
        aktuels = []
        processes = {}
        with Pool() as pool:
            for name, market in self.markets.items():
                processes[name] = pool.apply_async(market().get_aktuels)
            for name, process in processes.items():
                try:
                    aktuels += process.get()
                except requests.exceptions.ConnectionError as e:
                    # print(e, 11)
                    aktuels += self.aktuel_db.read_aktuel(name)
                    self.exception = True

        aktuels = sorted(aktuels, key=lambda k: k['tarih'], reverse=False)
        aktuels = sorted(aktuels, key=lambda k: k['magaza'], reverse=False)

        return aktuels

    def show_summary(self):
        saved_aktuels = self.aktuel_db.read_aktuels()
        aktuels = self.get_aktuels()

        self.active_aktuels = self.get_active_aktuels(saved_aktuels)
        self.still_active_aktuels = {}
        self.expired_aktuels = self.get_expired_aktuels(aktuels, self.active_aktuels)
        self.new_aktuels = self.get_new_aktuels(aktuels, self.active_aktuels)

        if self.exception:
            print('')

        if self.active_aktuels:
            print("Chosen campaigns:")
            for key, active_aktuel in self.active_aktuels.items():
                print(active_aktuel['magaza'], active_aktuel['aktuel'])
            print('')
        else:
            pass

        if self.expired_aktuels:
            print("Expired campaigns:")
            for key, expired_aktuel in self.expired_aktuels.items():
                print(str(key) + '.', expired_aktuel['magaza'], expired_aktuel['aktuel'])
            print(
                "* Please enter the IDs of campaigns you want to delete by adding ':' to beginning. (Enter :0 for deleting all of them)\n")
        else:
            pass

        if self.new_aktuels:
            print("New campaigns:")
            for key, new_aktuel in self.new_aktuels.items():
                print(str(key) + '.', new_aktuel['magaza'], new_aktuel['aktuel'])
            print("* Please enter the IDs of campaigns you choose. (Enter 0 for choose all of them)\n")
        else:
            pass

        if not self.expired_aktuels and not self.new_aktuels:
            print("No new campaign.")
            input()

    @staticmethod
    def get_active_aktuels(saved_aktuels):
        active_aktuels = {}
        count = 1

        for aktuel in saved_aktuels:
            if aktuel['durum'] == 'active':
                active_aktuels[count] = aktuel
                count += 1
            else:
                pass

        return active_aktuels

    def get_expired_aktuels(self, aktuels, active_aktuels):
        expired_aktuels = {}
        count = 1
        count0 = 1

        for key, active_aktuel in active_aktuels.items():
            active_market = active_aktuel['magaza']
            active_aktuel_name = active_aktuel['aktuel']

            exist = False
            for aktuel in aktuels:
                if aktuel['magaza'] == active_market and aktuel['aktuel'] == active_aktuel_name:
                    exist = True
                    break
            if not exist:
                expired_aktuels[count] = active_aktuel
                count += 1
            else:
                self.still_active_aktuels[count0] = active_aktuel
                count0 += 1

        return expired_aktuels

    @staticmethod
    def get_new_aktuels(aktuels, active_aktuels):
        new_aktuels = {}
        count = 1

        for aktuel in aktuels:
            market = aktuel['magaza']
            aktuel_name = aktuel['aktuel']

            exist = False
            for key, active_aktuel in active_aktuels.items():
                if active_aktuel['magaza'] == market and active_aktuel['aktuel'] == aktuel_name:
                    exist = True
                    break
            if not exist:
                new_aktuels[count] = aktuel
                count += 1
        return new_aktuels

    def command(self):
        user_inputs = []
        if self.expired_aktuels or self.new_aktuels:
            print("* Split every command with ',' character. (Enter '#' for saving the session)\n")
            while not self.command_control(user_inputs, len(self.new_aktuels), len(self.expired_aktuels)):
                user_inputs = input("Command Line: ")
                user_inputs = self.command_optimizer(user_inputs)
            self.command_execution(user_inputs)
            self.save_aktuels()
        else:
            pass

    @staticmethod
    def command_control(user_inputs, new_max, expired_max):
        try:
            if not user_inputs:
                return False
            for key in user_inputs:
                if key == '#':
                    return True
                elif key[0] == ':':
                    if not key[1:].isnumeric() or int(key[1:]) < 0 or int(key[1:]) > expired_max or expired_max == 0:
                        return False
                elif not key.isnumeric() or int(key) < 0 or int(key) > new_max or new_max == 0:
                    return False
                else:
                    pass
            return True
        except Exception as e:
            print(e, 12)
            return False

    @staticmethod
    def command_optimizer(user_inputs):
        user_inputs = sorted(set(''.join(user_inputs.split()).split(',')))
        for a in user_inputs:
            if not a:
                user_inputs.remove(a)

        return user_inputs

    def command_execution(self, user_inputs):
        for user_input in user_inputs:
            if user_input == '#':
                break
            elif user_input[0] == ':':
                if user_input[1] == '0':
                    self.expired_aktuels = {}
                else:
                    self.expired_aktuels.pop(int(user_input[1:]), None)
            elif user_input == '0':
                for key, new_aktuel in self.new_aktuels.items():
                    new_aktuel['durum'] = 'active'
            else:
                self.new_aktuels[int(user_input)]['durum'] = 'active'

    def save_aktuels(self):
        aktuels = []
        for key, value in self.new_aktuels.items():
            aktuels.append(value)
        for key, value in self.expired_aktuels.items():
            aktuels.append(value)
        for key, value in self.still_active_aktuels.items():
            aktuels.append(value)

        self.aktuel_db.save_aktuels(aktuels)
