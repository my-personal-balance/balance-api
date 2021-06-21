from connexion import ProblemException


class ResourceNotFound(ProblemException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status=404, title="Not found", detail=detail)


class Resource:
    fields = ()

    def __init__(self, instance):
        self._instance = instance

    @property
    def instance(self):
        return self._instance

    @classmethod
    def deserialize(cls, data, create=True) -> dict:
        raise NotImplementedError

    def serialize(self, **kwargs) -> dict:
        serialized = {}

        if not self._instance:
            raise ResourceNotFound()

        for field in self.fields:
            serialized[field] = getattr(self._instance, field)

        return serialized
