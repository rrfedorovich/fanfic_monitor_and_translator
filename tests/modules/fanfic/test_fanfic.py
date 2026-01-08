import unittest


from src.modules.fanfic import SpaceBattles

CSV = [
    "Russian Caravan",
    "https://forums.spacebattles.com/threads/russian-caravan-worm-eldritch-horror-crossover-au.1044966/",
    "405",
]
TITLE = "Epilogue VIII"
TEXT = """\n\n\n\nEpilogue VIII



Bangkok had a suite of names.



City of angels, great city of immortals, magnificent city of the nine gems, seat of the king, city of royal palaces, home of the gods incarnate, erected by Vishvakarman at Indra's behest.



And right now, it was wet.



Bangkok rained. The klongs swelled and in some cases burst their banks, flooding into streets that were still half-deserted, even now. Grey, silty water pooled in the narrow streets, and there was a wave of shoes being removed, small platform-sandals replacing them as people struggled on regardless. Bells were ringing across the city, barely audible through the thick curtains of rain. There was a faint air of chanting as well, a mixture of languages and styles and... schools, really. Tibetan monks, still wondering if they might be able to go back home now the human hives were being demolished, sang cautiously while their Thai counterparts worked without reservation. You could tell where a Tibetan temple was whenever the floods came. The waters would rise, washing into the small compounds, and sand mandalas would be completely swept away. And for a little while, the flood was turn all manner of colours, bright dust kept visible by the current, incapable of sinking downwards. The monks didn't seem to mind the delay - added to the effect of the exercise.



The city was quiet. Unusually so."""


class TestSpaceBattles(unittest.TestCase):
    """Класс для тестирования SpaceBattles."""

    def test_get_data_for_csv(self):
        """Тестирование вывода для csv."""
        fanfic = SpaceBattles(*CSV)
        self.assertEqual(CSV, fanfic.get_data_for_csv())

    def test_get_update(self):
        """Тестирование получения обновлений."""
        fanfic = SpaceBattles(*CSV)
        fanfic.get_update()
        self.assertEqual(407, fanfic.last_chapter)
        self.assertEqual(TITLE, fanfic._new_chapters[-2].title)
        self.assertEqual(TEXT[:300], fanfic._new_chapters[-2].text[:300])
