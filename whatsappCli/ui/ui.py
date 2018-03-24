from abc import ABCMeta, abstractmethod

class UI:

    @abstractmethod
    def start(self):
        """ start ui
            to be implemented by derived class
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """ free resources and stop ui
            to be implemented by derived class
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, command):
        """ execute a command
            to be implemented by derived class
        """
        raise NotImplementedError
