class DuplicateEventException(Exception):
    def __init__(self, event_id:str, inner_exception:Exception, message:str="Skip process event due to duplicated event id [{}]"):
        self.event_id = event_id
        self.inner_exception = inner_exception
        self.message = message.format(self.event_id)
        super().__init__(self.message)