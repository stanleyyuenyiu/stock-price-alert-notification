class RetryableImpl():
    pass

class RetrableEventException(Exception, RetryableImpl):
    pass