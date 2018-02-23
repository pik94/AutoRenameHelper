import os
import re
from src.errors import *
from functools import reduce


class Processor:
    """
    This class is a main class which produces processing of files.
    """
    def __init__(self, run_path, path, translator=None, path_to_translator=None, layer=1, exclude_dirs=False, exclude_files=False):
        """
        :param run_path: a path where the script is run
        :param path: a path for rename
        :param layer: a layer in hierarchy of directories
        :param exclude_dirs: if this flag is True, directories won't be renamed
        :param exclude_files: if this flag is True, files won't be renamed
        """
        self.root_path = path
        self.run_path = run_path
        if layer < 0:
            raise BaseError("Layer cannot be less 0.")
        else:
            self.layer = layer
        self.exclude_dirs = exclude_dirs
        self.exclude_files = exclude_files

        if translator is not None:
            if isinstance(translator, dict):
                self.translator = translator
            else:
                raise BaseError("The given translator doesn't have a type 'dict'")
        else:
            self.translator = {}
            try:
                self._create_translator(path_to_translator)
            except ExistingFormatValue:
                raise BaseError("Can't create an object of class {}".format(Processor.__name__))
            except FileNotFoundError:
                raise BaseError("No such file or directory: {}".format(path_to_translator))

    def _create_translator(self, path_to_translator=None):
        """
        This method creates a dictionary for translating.
        NOTE: if we want to except some symbols for your dictionary, we'll be able to set a symbol "#" for it.
        For example: a,#. In this case we except a symbol "a" from your future dictionary.
        :return:
        """
        if path_to_translator is None:
            path_to_translator = os.path.join(self.run_path, "config", "translit.txt")

        with open(path_to_translator, "r") as file:
            for line in file:
                if "#" in line:
                    continue
                else:
                    splitted_line = line.split(",")
                    key, value = splitted_line[0], splitted_line[1].strip()
                    if key in self.translator:
                        raise ExistingFormatValue(key, value, self.translator[key])
                    self.translator[key] = value

    def run(self):
        for current_path, dirs, files in os.walk(self.root_path, topdown=False):
            if self.layer != 0:
                if self._compute_current_layer(current_path) > self.layer:
                    continue
            else:
                if self.exclude_dirs and self.exclude_files:
                    return
                elif self.exclude_dirs and not self.exclude_files:
                    self._process_dirs(current_path, dirs)
                elif not self.exclude_dirs and self.exclude_files:
                    self._process_files(current_path, files)
                else:
                    self._process_files(current_path, files)
                    self._process_dirs(current_path, dirs)

    def _process_dirs(self, path, dirs):
        self._process_files(path, dirs)

    def _process_files(self, path, files):
        self._process(path, files)

    def _process(self, path, array):
        for name in array:
            # print(name)
            low__name = str(name).lower()
            trans__name = self._transliterate(low__name)
            pattern = "[^a-zA-Z0-9_." + reduce(lambda x, y: str(x) + str(y), self.translator.values()) + "]"
            splitted__name = self.split_name(trans__name, pattern)
            new_file_name = self.concatenate_elements(splitted__name)
            if new_file_name != "":
                os.rename(os.path.join(path, name), os.path.join(path, new_file_name))
        return

    def _compute_current_layer(self, path):
        """
        This method computes a current directory layer for processing represented by a variable 'path'.
        The main idea this algorithm is that we compute a distance from a current subdirectory in processing to a root
        directory represented by the root path.
        The root directory has layer 1, subdirectories of the root directory has layer 2 etc.
        If the current path is equal to a root path, the method returns 1 else the current path is path to subdirectory,
        we compute current layer.
        :param path to a current processing directory
        :return int value of the current layer.
        """
        if path == self.root_path:
            return 1
        else:
            current_level = 1
            while path != self.root_path:
                current_level += 1
                path = os.path.split(path)[0]
        return current_level

    @staticmethod
    def split_name(name, pattern):
        if name is None or pattern is None:
            return ""
        else:
            splitted_name = re.split(pattern, name)
            name = []
            for item in splitted_name:
                item = str(item)
                if item != "":
                    name.append(item)
        return name

    def _transliterate(self, name):
        """
        This method transliterates the given name into other representation according to rules of the transliterations.
        If we catch a character in a dictionary, we transliterate it into the corresponding character from the dictiona-
        ry.
        Otherwise we skip this character and concatenates it to a new name.
        :param name: the given name to transliterate
        :return: a transliterated name
        """
        new_name = ""
        for symbol in name:
            if symbol in self.translator.keys():
                new_name += str(self.translator[str(symbol)])
            else:
                new_name += str(symbol)
        return new_name

    @staticmethod
    def concatenate_elements(array):
        """
        This method concatenates all elements written through a underscore symbol '_' in the given array into a string.
        For example:
        Let we have in word_array next elements: 'a', 'b', '123'. We'll have "a_b_123" as a result of the method's call.
        :param array:
        :return:
        """
        print("array:", array)
        conc_str = str(array[0])
        for item in array[1:]:
            conc_str = conc_str + "_" + str(item)
        return conc_str
