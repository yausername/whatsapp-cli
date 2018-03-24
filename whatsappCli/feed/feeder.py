from abc import ABCMeta, abstractmethod

class Feeder:

    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, user = None):
        """ return a stream of messages filtered by user
            to be implemented by derived class
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, user, msg):
        """ send msg to a user
            to be implemented by derived class
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_user(self, name):
        """ return user where name matches `name`
            to be implemented by derived class
        """
        raise NotImplementedError

    @abstractmethod
    def add_user(self, number, name):
        """ add user to contacts
            to be implemented by derived class
        """
        raise NotImplementedError


    @abstractmethod
    def users(self):
        """ return list of all contacts
            to be implemented by derived class
        """
        raise NotImplementedError
