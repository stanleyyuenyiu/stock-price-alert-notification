from abc import abstractproperty
class Repo:
    @abstractproperty
    @property
    def session_factory(self):
        raise NotImplementedError
