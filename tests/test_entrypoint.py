try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gaw.entrypoint import Entrypoint, entrypoint

class EntrypointTest(unittest.TestCase):

    def test_get_entrypoints_from_class(self):

        class Test(object):
            @entrypoint
            def a(self):
                pass

            @entrypoint
            def b(self):
                pass

            def c(self):
                pass

        l = Entrypoint.get_entrypoints_from_class(Test)
        self.assertListEqual(l, ['a', 'b'])

    def test_mark_method_as_entrypoint(self):

        def fn(): pass
        Entrypoint.mark_method_as_entrypoint(fn)

        from gaw.entrypoint import ENTRYPOINT_ATTR
        self.assertTrue(hasattr(fn, ENTRYPOINT_ATTR))

    def test_decorator(self):

        @Entrypoint.decorator
        def fn(): pass

        from gaw.entrypoint import ENTRYPOINT_ATTR
        self.assertTrue(hasattr(fn, ENTRYPOINT_ATTR))

        @entrypoint
        def fn2(): pass
        self.assertTrue(hasattr(fn2, ENTRYPOINT_ATTR))

