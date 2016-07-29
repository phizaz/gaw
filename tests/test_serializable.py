try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from gaw import Serializable


class SerializableTest(unittest.TestCase):
    def test_serializable_types(self):
        dat = None
        serial = Serializable.serialize(dat)
        self.assertEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertEqual(json, dat)

        dat = True
        serial = Serializable.serialize(dat)
        self.assertEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertEqual(json, dat)

        dat = 10
        serial = Serializable.serialize(dat)
        self.assertEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertEqual(json, dat)

        dat = 10.1
        serial = Serializable.serialize(dat)
        self.assertAlmostEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertAlmostEqual(json, dat)

        dat = 'aoeu'
        serial = Serializable.serialize(dat)
        self.assertEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertEqual(json, dat)

        dat = u'aoeu'
        serial = Serializable.serialize(dat)
        self.assertEqual(serial, dat)
        json = Serializable.json(dat)
        self.assertEqual(json, dat)

    def test_default_support_types(self):
        from datetime import datetime
        import dateutil.parser
        t = dateutil.parser.parse('2016-07-29 11:18:20.480054')
        serial = Serializable.serialize(t)
        self.assertDictEqual(serial, dict(
            _t='datetime',
            _v='2016-07-29 11:18:20.480054'
        ))
        parsed = Serializable.parse(serial)
        self.assertEqual(parsed, t)
        json = Serializable.json(t)
        self.assertEqual(json, '2016-07-29 11:18:20.480054')

        t = (1, 2, 3)
        serial = Serializable.serialize(t)
        self.assertDictEqual(serial, dict(
            _t='tuple',
            _v=[1, 2, 3]
        ))
        parsed = Serializable.parse(serial)
        self.assertEqual(parsed, t)
        json = Serializable.json(t)
        self.assertListEqual(json, [1,2,3])

        import uuid
        str = '06335e84-2872-4914-8c5d-3ed07d2a2f16'
        t = uuid.UUID('{' + str + '}')  # create a UUID given string
        serial = Serializable.serialize(t)
        self.assertDictEqual(serial, dict(
            _t='uuid',
            _v=str,
        ))
        parsed = Serializable.parse(serial)
        self.assertEqual(parsed, t)
        json = Serializable.json(t)
        self.assertEqual(json, str)

        l = [i for i in range(3)]
        t = set(l)
        serial = Serializable.serialize(t)
        self.assertDictEqual(serial, dict(
            _t='set',
            _v=l
        ))
        parsed = Serializable.parse(serial)
        self.assertSetEqual(parsed, t)
        json = Serializable.json(t)
        self.assertListEqual(json, l)


    def test_object(self):
        class C(Serializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        c = C(10, 20)
        serial = Serializable.serialize(c)
        self.assertDictEqual(serial, dict(
            _t='C',
            _v=dict(
                a=10,
                b=20,
            )
        ))
        json = Serializable.json(c)
        self.assertDictEqual(json, dict(
            a=10,
            b=20,
        ))

    def test_get_subclasses(self):
        class A(Serializable):
            pass

        class B(Serializable):
            pass

        subclasses = set(Serializable.get_subclasses())
        self.assertTrue(A in subclasses)
        self.assertTrue(B in subclasses)

    def test_nested_object(self):
        from datetime import datetime

        class A(Serializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        class B(Serializable):
            def __init__(self, c):
                self.c = c

        # test nested object
        a = A(10, B(20))
        serial = Serializable.serialize(a)
        self.assertDictEqual(serial, dict(
            _t='A',
            _v=dict(
                a=10,
                b=dict(
                    _t='B',
                    _v=dict(
                        c=20
                    )
                )
            )
        ))
        json = Serializable.json(a)
        self.assertDictEqual(json, dict(
            a=10,
            b=dict(
                c=20
            )
        ))

    def test_serial_methods(self):
        class A(Serializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        class B(Serializable):
            def __init__(self, c):
                self.c = c

        a = A(10, B(20))
        serial = Serializable.serialize(a)
        serial2 = a.dict()
        serial3 = dict(a)

        self.assertDictEqual(serial, serial2)
        self.assertDictEqual(serial, serial3)
