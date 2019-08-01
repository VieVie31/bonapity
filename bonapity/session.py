"""
This module contains all the mechanic for handling user session.

@author: VieVie31
"""
import time
import threading

from collections import defaultdict


class UserSession:
    """
    User session have similar to dict as they support 
    __setitem__ and __getitem___, but they also keep track of the timestamp 
    of the last modifiction done via getter and setters.
    """
    def __init__(self):
        self.storage = {}
        self.creation_timestamp = time.time()
        self.last_timestamp = time.time()

    def __getitem__(self, key):
        self.last_timestamp = time.time()
        return self.storage[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.storage[self.__keytransform__(key)] = value
        self.last_timestamp = time.time()

    def __delitem__(self, key):
        del self.storage[self.__keytransform__(key)]
        self.last_timestamp = time.time()

    def __iter__(self):
        self.last_timestamp = time.time()
        return iter(self.storage)

    def __len__(self):
        self.last_timestamp = time.time()
        return len(self.storage)

    def __keytransform__(self, key):
        self.last_timestamp = time.time()
        return key
    
    def update_timestamp(self):
        self.last_timestamp = time.time()
    
    def __setattr__(self, name, value):
        if name in ['storage', 'sessionid', 'creation_timestamp', 'last_timestamp']:
            self.__dict__[name] = value
        else:
            raise Exception('attr setting not allowed')

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#FIXME: not finished to be implemented
class SessionManager(metaclass=Singleton):
    def __init__(self, session_timeout: int=10):
        """
        Create a session manager if not already existing.
        There is only one session manager instancied as this is a singleton.

        :param session_timeout:
            the session content of a specific user will be deleted 
            after this number of second of inactivity (not using the session)
        """
        raise NotImplementedError()
        self.session_timeout = session_timeout
        # `self.session` will contain for each SESSIONID as key a dict 
        # of the stored session data, aslo if the SESSIONID was not registered
        # the default dict corresponding to an emtpy session is {}
        self.sessions = defaultdict(UserSession) #(UserSession look like dict)
    
    def __getitem__(self, sessionid) -> UserSession:
        return self.sessions[sessionid]
    
    def __setitem__(self, *a, **k):
        raise Exception('''
            __setattr__ is not allowed by SessionManager,
            you can only modify the returned UserSession')
        ''')
    
    def __delitem__(self, sessionid):
        del self.sessions[sessionid]
    
    def __clean_timedout_session(self):
        for session in self.session:
            #TODO: check if unused since self.timeout
            raise NotImplementedError()




