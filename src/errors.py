class BaseError(Exception):
    def __init__(self, message=""):
        self.message = message

    def print_message(self):
        print("{}".format(self.message))

    def get_message(self):
        return self.message

class ExistingFormatValue(BaseError):
    def __init__(self, key, value, old_value):
        print("A symbol '{}' has already been included in your dictionary before.".format(key), end=" ")
        print("Old value '{}' for '{}' can't be overwritten by new value '{}'".format(old_value, key, value))


class ConstructorError(BaseError):
    def __init__(self, message):
        super().__init__(message)


class LayerError(BaseError):
    def __init__(self, message):
        super().__init__(message)