import os
import re
from functools import reduce

from src.errors import *


class Processor:
    """
    This class is a main class which produces processing of files and directories.
    It's a really flexible tool to use. It can rename files and directories using an inner or an user dictionary.
    The main idea this process is that all directories and files are in hierarchy. It's a good for us.
    So, you can set root path to process. If it's only file, we'll just rename it. If it's directory, it'll be more
    interesting case. An hierarchy of dictionaries and files is a graph. This graph will have root and leafs. So, you
    can compute a distance from a root to an any node of it. All same distances are layer in the hierarchy.
    If you need to rename files and dictionaries before some layer, will just set it!
    Also, you can exclude files of dictionaries for renaming.
    An example of Processor class gets path to directory or file to rename.
    """

    def __init__(self, path, translator=None, path_to_translator=None, layer=1, exclude_dirs=False,
                 exclude_files=False):
        """
        :param path: a path to directory to rename. It must be string type
        :param translator: an user's translator given as dictionary. It must be string type. None by default
        :param path_to_translator: a path to file where there is an user's translator. It must be string type.
                                   None by default
        :param layer: a layer in hierarchy of directories to rename files and directories. If 0 then processing all
                      files and directories recursively. It must be int type. 1 by default
        :param exclude_dirs: if this flag is True, directories won't be renamed. It must have bool type.
                             False by default.
        :param exclude_files: if this flag is True, files won't be renamed. It must have bool type. False by default.
        """
        try:
            self.root_path = self._create_root_path(path)
        except BaseError as e:
            raise ConstructorError(e.get_message())

        try:
            self.layer = self._create_layer(layer)
        except BaseError as e:
            raise ConstructorError(e.get_message())

        try:
            self.translator = self._create_translator(translator, path_to_translator)
            self.print_translator()
        except BaseError as e:
            raise ConstructorError(e.get_message())

        if not isinstance(exclude_dirs, bool):
            raise ConstructorError(
                "Exclude dirs flag must be type {}. Actually it has type {}".format(bool, type(exclude_dirs)))
        else:
            self.exclude_dirs = exclude_dirs

        if not isinstance(exclude_dirs, bool):
            raise ConstructorError(
                "Exclude files flag must be type {}. Actually it has type {}".format(bool, type(exclude_files)))
        else:
            self.exclude_files = exclude_files

    def _create_root_path(self, path):
        if not isinstance(path, str):
            raise BaseError("path must be type {}. Actually it has type {}".format(str, type(path)))
        else:
            if os.path.exists(path):
                return path
            else:
                raise BaseError("Given path {} doesn't exist.".format(path))

    def _create_layer(self, layer):
        if not isinstance(layer, int):
            raise BaseError("Layer must be type {}. Actually it has type {}".format(int, type(layer)))
        elif layer < 0:
            raise BaseError("Layer cannot be less then 0.")
        else:
            return layer

    def _create_translator(self, translator, path_to_translator):
        if translator is not None:
            if isinstance(translator, dict):
                return translator
            else:
                raise BaseError("The given translator doesn't have a type 'dict'")
        else:
            try:
                translator =  self._create_translator_for_path(path_to_translator)
            except ExistingFormatValue:
                raise BaseError("Can't create an object of class {}".format(Processor.__name__))
            except FileNotFoundError:
                raise BaseError("No such file containing dictionary: {}".format(path_to_translator))
            except IsADirectoryError:
                raise BaseError("Given path '{}' isn't a file ".format(path_to_translator))

            return translator

    def _create_translator_for_path(self, path_to_translator=None):
        """
        This method creates a dictionary for translating.
        NOTE: if we want to except some symbols for your dictionary, we'll be able to set a tag "#exclude" for it.
        For example: a,#exclude. In this case we except a symbol "a" from your future dictionary.
        :return: translator
        """
        if path_to_translator is None:
            path_to_translator = os.path.join(os.getcwd(), "config", "translit.txt")

        translator = {}
        with open(path_to_translator, "r") as file:
            for line in file:
                if "#exclude" in line:
                    continue
                else:
                    splitted_line = line.split(",")
                    key, value = splitted_line[0], splitted_line[1].strip()
                    if key in translator:
                        raise ExistingFormatValue(key, value, translator[key])
                    translator[key] = value
        return translator

    def print_translator(self):
        print("Dictionary for transliting is:")
        if len(self.translator) == 0:
            print("Void dictionary")
        for item in sorted(self.translator.items(), key=lambda item: item[0]):
            print("{} -> {}".format(item[0], item[1]))

    def run(self):
        for current_path, dirs, files in os.walk(self.root_path, topdown=False):
            # the condition below is to check if a current layer in hierarchy deeper then given layer (self.layer)
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
        self._process(path, dirs)

    def _process_files(self, path, files):
        self._process(path, files)

    def _process(self, path, array):
        for name in array:
            low__name = str(name).lower()
            trans__name = self._transliterate(low__name)

            sub_pattern = ""
            if len(self.translator.values()) > 0:
                sub_pattern = reduce(lambda x, y: str(x) + str(y), self.translator.values())
            pattern = "[^a-zA-Z0-9_." + sub_pattern + "]"

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
        conc_str = str(array[0])
        for item in array[1:]:
            conc_str = conc_str + "_" + str(item)
        return conc_str
