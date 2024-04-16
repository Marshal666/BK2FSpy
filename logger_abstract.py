from abc import ABC, abstractmethod


class LoggerAbstract(ABC):

	@abstractmethod
	def __init__(self, *args):
		pass

	@abstractmethod
	def print(self, content):
		pass
