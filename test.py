import unittest2
loader = unittest2.TestLoader()
tests = loader.discover('spells/')
testRunner = unittest2.runner.TextTestRunner(verbosity=2)
testRunner.run(tests)
