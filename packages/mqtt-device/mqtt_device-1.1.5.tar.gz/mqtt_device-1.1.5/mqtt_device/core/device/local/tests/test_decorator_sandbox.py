import unittest


class MyDecorator(object):

	def __init__(self, kikoo):
		self._arg = kikoo

	def __call__(self, arg):
		print("before")
		return arg

		# retval = self._arg(a, b)
		# return retval ** 2

	# def __call__(self, a, b):
	# 	retval = self._arg(a, b)
	# 	return retval ** 2

# @MyDecorator
# def kikoo():
#     print("KIKOO")

class MyTest:

	@MyDecorator(kikoo="lol")
	def abc(self):
		print("ABC")


class TestDecoratorSandbox(unittest.TestCase):
	def test(self):
		test = MyTest()

		test.abc()

		# print("abc")





if __name__ == '__main__':
    unittest.main()
