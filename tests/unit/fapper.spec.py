import unittest
from utils.fapper import Map

data = {
    "kurwa": [0, 1, 2, 3, 4, 5],
    "oh_kurwa": {
        "kek": "suka",
        "c_kaifom": {
            "ahahahah": True,
            "meh": {
                "loop": {},
                "poop": {
                    "heh": [3, 5]
                }
            }
        }
    }
}

data_map = Map(data)


class MyTestCase(unittest.TestCase):
    def test_shallow(self):
        self.assertEqual(data_map.kurwa[2], 2)
        self.assertEqual(data_map.oh_kurwa, data["oh_kurwa"])

    def test_deep(self):
        self.assertEqual(data_map.oh_kurwa.kek, "suka")
        self.assertEqual(data_map.oh_kurwa.c_kaifom.ahahahah, True)
        self.assertEqual(data_map.oh_kurwa.c_kaifom.meh.poop.heh[0], 3)

    def test_invalid_key(self):
        self.assertEqual(data_map.invalid, None)


if __name__ == '__main__':
    unittest.main()
