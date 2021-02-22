class Statistics(object):
    def __init__(self):
        self._delta_dict = dict()
        self._general_dict = dict()
        self._last_name = None
        self._last_delta = None

    def __str__(self):
        return str(self._delta_dict) + "; " + str(self._general_dict)

    def change_model(self, name):
        self._last_name = name
        if name not in self._delta_dict:
            self._delta_dict[name] = dict()
        if name not in self._general_dict:
            self._general_dict[name] = dict()

    def change_delta(self, delta, clean=True):
        self._last_delta = delta
        if clean or delta not in self._delta_dict[self._last_name]:
            self.clean_delta_entries()

    def add(self, key, value):
        self._delta_dict[self._last_name][self._last_delta][key] = value

    def add_general(self, key, value):
        self._general_dict[self._last_name][key] = value

    def get_delta_entry(self, key):
        return self._delta_dict[self._last_name][self._last_delta].get(key, None)

    def clean_delta_entries(self):
        self._delta_dict[self._last_name][self._last_delta] = dict()
