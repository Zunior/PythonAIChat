import abc

class AiResponderInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'return_answer') and
                callable(subclass.return_answer))