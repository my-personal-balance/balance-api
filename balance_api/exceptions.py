from connexion import ProblemException


class ResourceBadRequest(ProblemException):
    def __init__(self, detail):
        super().__init__(status=400, title="Bad request", detail=detail)


class AssetNotFoundException(ProblemException):
    def __init__(self, detail):
        super().__init__(status=400, title="Bad request", detail=detail)
