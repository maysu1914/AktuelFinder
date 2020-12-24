import ast
import datetime
import json
import os


class AktuelDB:

    def __init__(self, filename):
        self.filename = filename

    def save_aktuels(self, data):
        old_filename = self.filename + ".txt.{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        if os.path.isfile(self.filename + ".txt"):
            if os.path.isfile(old_filename):
                os.remove(old_filename)
            else:
                pass
            os.rename(self.filename + ".txt", old_filename)
        else:
            pass

        with open('{name}.txt'.format(name=self.filename), 'w', encoding="utf8") as file:
            file.write(json.dumps(data))
        print('\n{name}.txt created.'.format(name=self.filename))

    def read_aktuels(self):
        try:
            if os.path.isfile(self.filename + ".txt"):
                with open('{}.txt'.format(self.filename), encoding='utf-8') as f:
                    data = f.readline()

                data = ast.literal_eval(data)
                data = sorted(data, key=lambda k: k['tarih'], reverse=False)
                data = sorted(data, key=lambda k: k['magaza'], reverse=False)
                return data
            else:
                return []
        except Exception as e:
            print(e, 10)
            return []

    def read_aktuel(self, aktuel):
        local_aktuel = []
        if os.path.isfile(self.filename + ".txt"):
            with open('{}.txt'.format(self.filename), encoding='utf-8') as f:
                data = f.readline()
            for i in ast.literal_eval(data):
                if i['magaza'] == aktuel:
                    local_aktuel.append(i)
            local_aktuel = sorted(local_aktuel, key=lambda k: k['tarih'], reverse=False)
            local_aktuel = sorted(local_aktuel, key=lambda k: k['magaza'], reverse=False)
            return local_aktuel
        else:
            return local_aktuel
