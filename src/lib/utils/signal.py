import signal
import threading
lock = threading.RLock()

class LifeSpanMgr():
    
    IS_SHUTDOWN:bool = False

    @staticmethod
    def is_shutdown():
        return LifeSpanMgr.IS_SHUTDOWN

    @staticmethod
    def shutdown():
        with lock:
            LifeSpanMgr.IS_SHUTDOWN = True

    @staticmethod
    def interrupted_process(**kwargs):
        LifeSpanMgr.shutdown()

    @staticmethod
    def register_signal():
        signal.signal(signal.SIGTERM, LifeSpanMgr.interrupted_process)
        signal.signal(signal.SIGINT, LifeSpanMgr.interrupted_process)
        signal.signal(signal.SIGQUIT, LifeSpanMgr.interrupted_process)
        signal.signal(signal.SIGHUP, LifeSpanMgr.interrupted_process)