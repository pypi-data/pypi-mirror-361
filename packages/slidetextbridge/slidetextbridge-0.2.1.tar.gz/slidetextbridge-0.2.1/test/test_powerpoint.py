import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

mock_win32com_client = types.SimpleNamespace(Dispatch=lambda x: None)
mock_win32com = types.SimpleNamespace(client=mock_win32com_client)
mock_pywintypes = types.SimpleNamespace(com_error=Exception)
sys.modules['win32com'] = mock_win32com
sys.modules['win32com.client'] = mock_win32com_client
sys.modules['pywintypes'] = mock_pywintypes

from slidetextbridge.plugins import powerpoint # pylint: disable=C0413

def mock_shape(text, shape_type=14, name='unnamed'):
    shape = MagicMock()

    shape.HasTextFrame = True
    shape.TextFrame = MagicMock()
    shape.TextFrame.TextRange = MagicMock()
    shape.TextFrame.TextRange.Text = text
    shape.TextFrame.TextRange.HasText = len(text) > 0
    shape.TextFrame.TextRange.Count = len(text)
    shape.TextFrame.TextRange.Start = 0
    shape.TextFrame.TextRange.Length = len(text)
    shape.TextFrame.TextRange.BoundLeft = 0
    shape.TextFrame.TextRange.BoundTop = 0
    shape.TextFrame.TextRange.BoundWidth = 1
    shape.TextFrame.TextRange.BoundHeight = 1
    shape.TextFrame.TextRange.Font = MagicMock()
    shape.TextFrame.TextRange.Font.Size = 24
    shape.TextFrame.TextRange.Font.Bold = False
    shape.TextFrame.TextRange.Font.Name = name
    shape.TextFrame.TextRange.Font.BaselineOffset = 0
    shape.TextFrame.TextRange.Font.Italic = False
    shape.TextFrame.TextRange.Font.Subscript = False
    shape.TextFrame.TextRange.Font.Superscript = False
    shape.TextFrame.HasText = True
    shape.TextFrame.Orientation = 0
    shape.TextFrame.WordWrap = False

    shape.PlaceholderFormat = MagicMock()
    shape.PlaceholderFormat.Name = name
    shape.PlaceholderFormat.Type = 1
    shape.PlaceholderFormat.ContainedType = 2

    shape.Type = shape_type
    shape.Name = name

    return shape

class TestPowerPointCapture(unittest.IsolatedAsyncioTestCase):
    def test_type_name(self):
        self.assertEqual(powerpoint.PowerPointCapture.type_name(), 'ppt')

    async def test_loop(self):
        ctx = MagicMock()
        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        obj._loop_once = AsyncMock()
        obj._loop_once.side_effect = (None, )
        obj.logger = MagicMock()
        with patch('asyncio.sleep', side_effect=(None, )) as mock_sleep:
            with self.assertRaises(StopAsyncIteration):
                await obj._loop()

        self.assertEqual(obj._loop_once.await_count, 3)
        self.assertEqual(mock_sleep.await_count, 2)

    @patch('win32com.client.Dispatch', autospec=True)
    async def test_update(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        win = MagicMock()
        api_slide = MagicMock()
        ppt.SlideShowWindows.Count = 1
        ppt.SlideShowWindows.return_value = win
        win.View = MagicMock()
        win.View.State = 0
        win.View.Slide = api_slide

        api_slide.Shapes = [
                mock_shape(text='a'),
                mock_shape(text='b'),
        ]
        api_slide.Shapes[1].Type = 13 # Not a placeholder

        obj.emit = AsyncMock()

        await obj._loop_once()

        obj.emit.assert_called_once()
        slide = obj.emit.call_args[0][0]

        MockDispatch.assert_called_once_with('PowerPoint.Application')

        self.assertEqual(str(slide), 'a')
        # self.maxDiff = None
        d = slide.to_dict()
        self.assertEqual(d['shapes'][0]['text_frame']['has_text'], True)
        self.assertEqual(d['shapes'][0]['text_frame']['text_range']['text'], 'a')
        # TODO: Check other fields. I should copy the expected data from actual PowerPoint.

        self.assertEqual(slide.to_texts(), ['a'])

        # Call again, Dispatch should not be called again.
        await obj._loop_once()
        MockDispatch.assert_called_once_with('PowerPoint.Application')

    @patch('win32com.client.Dispatch', autospec=True)
    async def test_multi_windows(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        win1 = MagicMock()
        api_slide = MagicMock()
        win1.View = MagicMock()
        win1.View.State = 0
        win1.View.Slide = api_slide
        win1.Active = False

        api_slide.Shapes = [
                mock_shape(text='win1-shape'),
        ]

        win2 = MagicMock()
        api_slide = MagicMock()
        win2.View = MagicMock()
        win2.View.State = 0
        win2.View.Slide = api_slide
        win2.Active = True

        api_slide.Shapes = [
                mock_shape(text='win2-shape'),
        ]

        ppt.SlideShowWindows.Count = 2
        ppt.SlideShowWindows.side_effect = (win1, win2)

        obj.emit = AsyncMock()

        await obj._loop_once()

        obj.emit.assert_called_once()
        slide = obj.emit.call_args[0][0]

        self.assertEqual(str(slide), 'win2-shape')

        ppt.SlideShowWindows.Count = 2
        ppt.SlideShowWindows.side_effect = (win1, win2)
        api_slide = MagicMock()
        win2.Active = False
        win2.View.Slide = api_slide
        api_slide.Shapes = [
                mock_shape(text='win2-shape modified'),
        ]

        obj.emit = AsyncMock()
        await obj._loop_once()
        obj.emit.assert_called_once()
        slide = obj.emit.call_args[0][0]
        self.assertEqual(str(slide), 'win2-shape modified')

    @patch('win32com.client.Dispatch', autospec=True)
    async def test_dispatch_failure(self, MockDispatch):
        ctx = MagicMock()

        MockDispatch.side_effect = mock_pywintypes.com_error
        MockDispatch.return_value = None

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        obj.emit = AsyncMock()

        await obj._loop_once()

        self._assert_empty_slide(obj.emit)

    @patch('win32com.client.Dispatch', autospec=True)
    async def test_ppt_windows_count_exception(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        def _raise_error(*args, **kwargs):
            raise mock_pywintypes.com_error
        type(ppt.SlideShowWindows).Count = property(_raise_error)

        obj.emit = AsyncMock()

        await obj._loop_once()

        self._assert_empty_slide(obj.emit)

    @patch('win32com.client.Dispatch', autospec=True)
    async def test_ppt_windows_count_0(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        ppt.SlideShowWindows.Count = 0

        obj.emit = AsyncMock()

        await obj._loop_once()

        self._assert_empty_slide(obj.emit)

    def _assert_empty_slide(self, mock_emit):
        mock_emit.assert_called_once()
        slide = mock_emit.call_args[0][0]
        self.assertEqual(slide._slide, None)
        self.assertEqual(slide._dict, None)

    @patch('win32com.client.Dispatch', autospec=True)
    def test_blank(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        win = MagicMock()
        ppt.SlideShowWindows.Count = 1
        ppt.SlideShowWindows.return_value = win
        win.View = MagicMock()
        win.View.State = powerpoint._Const.ppSlideShowBlackScreen

        int_slide = obj._get_slide()

        self.assertEqual(int_slide, None)

    def test_accumulate_powerpoint(self):
        import importlib
        with patch('os.name', 'nt-test'):
            accumulate_name = 'slidetextbridge.plugins.accumulate'
            if accumulate_name in sys.modules:
                importlib.reload(sys.modules[accumulate_name])
            else:
                importlib.import_module(accumulate_name)
            accumulate = sys.modules[accumulate_name]
            self.assertEqual(accumulate._is_win, True)
            self.assertIn('ppt', accumulate.plugins)


if __name__ == "__main__":
    unittest.main()
