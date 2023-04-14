class AbortableImpl():
    pass

class AbortEventException(Exception, AbortableImpl):
    pass