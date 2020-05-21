

class ExportException(Exception):

    def __init__(self, msg, result):
        super().__init__(msg)
        self._result = result

    @property
    def result(self):
        return self._result


class JsonException(Exception):

    def __init__(self, msg):
        super().__init__(msg)