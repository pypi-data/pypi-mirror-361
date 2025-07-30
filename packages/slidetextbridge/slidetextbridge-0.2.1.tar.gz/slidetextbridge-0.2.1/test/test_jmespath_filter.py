import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.plugins.jmespath_filter import JMESPathFilter
from slidetextbridge.plugins.text_filters import TextFilteredSlide
from slidetextbridge.plugins import base

class TestJMESPathFilter(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(JMESPathFilter.type_name(), 'jmespath')

    def test_config(self):
        cfg_filter = 'filter-text'
        cfg = JMESPathFilter.config(
                data = {'filter': cfg_filter}
        )

        self.assertEqual(cfg.filter, cfg_filter)

    async def test_update_filters_slide(self):
        ctx = MagicMock()

        cfg = MagicMock()
        cfg.src = 'dummy'
        cfg.filter = 'shapes[?val==`2`]'

        filter_obj = JMESPathFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()

        slide = TextFilteredSlide(data={'shapes': [{'text': 'a', 'val': 1}, {'text': 'b', 'val': 2}]})

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        emitted_slide = filter_obj.emit.await_args[0][0]
        self.assertIsInstance(emitted_slide, TextFilteredSlide)
        self.assertEqual(emitted_slide.to_dict(), {'shapes': [{'text': 'b', 'val': 2}]})
        self.assertEqual(emitted_slide.to_texts(), ['b', ])

        # If nothing is filtered,
        slide = TextFilteredSlide(data={'shapes': [{'text': 'a', 'val': 1}, {'text': 'b', 'val': 3}]})
        await filter_obj.update(slide, args=None)
        emitted_slide = filter_obj.emit.await_args[0][0]
        self.assertEqual(emitted_slide.to_texts(), [])
        self.assertEqual(emitted_slide.to_dict(), {'shapes': []})

        # TextFilteredSlide ignores shapes that does not contain the `text` field.
        slide = TextFilteredSlide(data={'shapes': [{'test': 'a', 'val': 1}, {'test': 'b', 'val': 2}]})
        await filter_obj.update(slide, args=None)
        emitted_slide = filter_obj.emit.await_args[0][0]
        self.assertEqual(emitted_slide.to_texts(), [])

        # TextFilteredSlide ignores shapes list directly having string.
        slide = TextFilteredSlide(data={'shapes': [{'text': 'c', 'val': 1}, {'text': 'd', 'val': 2}]})
        cfg.filter = 'shapes[?val==`2`].text'
        filter_obj = JMESPathFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        await filter_obj.update(slide, args=None)
        emitted_slide = filter_obj.emit.await_args[0][0]
        self.assertEqual(emitted_slide.to_dict(), {'shapes': ['d']})
        self.assertEqual(emitted_slide.to_texts(), [])

if __name__ == '__main__':
    unittest.main()
