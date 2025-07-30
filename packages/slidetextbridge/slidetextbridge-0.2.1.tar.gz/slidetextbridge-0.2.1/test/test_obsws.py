import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from slidetextbridge.plugins import obsws, base

class TestObsWsEmitter(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(obsws.ObsWsEmitter.type_name(), 'obsws')

    def test_config(self):
        cfg_data = {'url': 'ws://192.0.2.1:4455/', 'password': 'pw', 'source_name': 'TestSource'}
        cfg = obsws.ObsWsEmitter.config(cfg_data)
        self.assertEqual(cfg.url, 'ws://192.0.2.1:4455/')
        self.assertEqual(cfg.password, 'pw')
        self.assertEqual(cfg.source_name, 'TestSource')


    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_connect_and_update(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src = 'dummy'
        cfg_url = 'ws://localhost:4455/'
        cfg_password = 'secret'
        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'src': cfg_src,
                'url': cfg_url,
                'password': cfg_password,
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.return_value = None
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.return_value = mock_res
        mock_res.ok.return_value = True
        mock_res.responseData = {'status': 'ok'}

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        ctx.get_instance.assert_called_once_with(name=cfg_src)

        await obj.update('test text', args=None)

        MockWebSocketClient.assert_called_with(url=cfg_url, password=cfg_password)
        mock_ws.connect.assert_awaited_once()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': 'test text'},
            }
        ))

        await obj.update('2nd text', args=None)

        mock_ws.connect.assert_awaited_once()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': '2nd text'},
            }
        ))

    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_update_failure(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src_name = 'test-source-name'
        cfg_url = 'ws://192.0.2.2:4455/'
        cfg = obsws.ObsWsEmitter.config({
                'url': cfg_url,
                'source_name': cfg_src_name,
        })

        mock_ws = AsyncMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.side_effect = (Exception('error test 1'), Exception('error test 2'))
        mock_ws.wait_until_identified.return_value = False

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        obj.logger.warning = MagicMock()
        ctx.get_instance.assert_called_once_with(name=None)

        await obj.update(None, args=None)

        MockWebSocketClient.assert_called_with(url=cfg_url, password=None)
        mock_ws.wait_until_identified.assert_not_called()
        mock_ws.connect.assert_awaited()
        self._assert_logging(obj.logger.warning, (
            ('Could not connect to %s. %s', cfg_url, 'error test 1'),
            ('Could not connect to %s. %s', cfg_url, 'error test 2'),
        ));

    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_identify_failure(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src_name = 'test-source-name'
        cfg_url = 'ws://192.0.2.2:4455/'
        cfg = obsws.ObsWsEmitter.config({
                'url': cfg_url,
                'source_name': cfg_src_name,
        })

        mock_ws = AsyncMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.wait_until_identified.side_effect = (False, True)
        mock_ws.call.return_value = MagicMock()
        mock_ws.call.return_value.ok.return_value = True
        mock_ws.call.return_value.responseData = {'status': 'ok'}

        mock_ws.disconnect = MagicMock()

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        obj.logger.warning = MagicMock()
        ctx.get_instance.assert_called_once_with(name=None)

        await obj.update('', args=None)

        MockWebSocketClient.assert_called_with(url=cfg_url, password=None)
        mock_ws.wait_until_identified.assert_awaited()
        mock_ws.connect.assert_awaited()
        mock_ws.disconnect.assert_called_with()
        self._assert_logging(obj.logger.warning, (
            ('Could not connect to %s. %s', cfg.url, 'Identification error'),
        ));

        # The 2nd attempt will successfully send the request.
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': ''},
            }
        ))


    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_update_retry_1(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.return_value = None
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.side_effect = (Exception('error 1'), mock_res)
        mock_res.ok.return_value = True
        mock_res.responseData = {'status': 'ok'}

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        obj.logger.warning = MagicMock()
        ctx.get_instance.assert_called_once_with(name=None)

        await obj.update('test text', args=None)

        MockWebSocketClient.assert_called_with(url='ws://localhost:4455/', password=None)
        mock_ws.connect.assert_awaited()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': 'test text'},
            }
        ))
        self._assert_logging(obj.logger.warning, (
            ('Failed to send text. %s', 'error 1'),
        ));

    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_update_retry_2(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.return_value = None
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.side_effect = (Exception('error 1'), Exception('error 2'), mock_res)
        mock_res.ok.return_value = True
        mock_res.responseData = {'status': 'ok'}

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        obj.logger.warning = MagicMock()
        ctx.get_instance.assert_called_once_with(name=None)

        await obj.update(base.SlideBase(), args=None)

        MockWebSocketClient.assert_called_with(url='ws://localhost:4455/', password=None)
        mock_ws.connect.assert_awaited()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': ''},
            }
        ))
        self._assert_logging(obj.logger.warning, (
            ('Failed to send text. %s', 'error 1'),
            ('Failed to send text. %s', 'error 2'),
            ('Could not send text. %s', 'error 2'),
        ))

    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_update_retry_connect_failure(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.side_effect = (None, Exception('connect error test'))
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.side_effect = (Exception('error 1'), mock_res)
        mock_res.ok.return_value = True
        mock_res.responseData = {'status': 'ok'}

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        obj.logger.warning = MagicMock()
        ctx.get_instance.assert_called_once_with(name=None)

        await obj.update(base.SlideBase(), args=None)

        MockWebSocketClient.assert_called_with(url='ws://localhost:4455/', password=None)
        mock_ws.connect.assert_awaited()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': ''},
            }
        ))
        self._assert_logging(obj.logger.warning, (
            ('Failed to send text. %s', 'error 1'),
            ('Could not connect to %s. %s', cfg.url, 'connect error test'),
        ))
        self.assertEqual(obj.ws, None)

    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_wrong_source_name(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src = 'dummy'
        cfg_url = 'ws://localhost:4455/'
        cfg_password = 'secret'
        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'src': cfg_src,
                'url': cfg_url,
                'password': cfg_password,
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.return_value = None
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.return_value = mock_res
        mock_res.ok.return_value = False
        mock_res.requestType = 'SetInputSettings'
        mock_res.requestStatus.code = 600
        mock_res.requestStatus.comment = f'No source was found by the name of `{cfg_src_name}`.'

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        ctx.get_instance.assert_called_once_with(name=cfg_src)

        obj.logger.warning = MagicMock()

        await obj.update('test text', args=None)

        MockWebSocketClient.assert_called_with(url=cfg_url, password=cfg_password)
        mock_ws.connect.assert_awaited()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': 'test text'},
            }
        ))
        self._assert_logging(obj.logger.warning, (
            ('%s: %d: %s', 'SetInputSettings', 600, f'No source was found by the name of `{cfg_src_name}`.'),
            ('%s: %d: %s', 'SetInputSettings', 600, f'No source was found by the name of `{cfg_src_name}`.'),
        ))


    def _assert_logging(self, mock_logging, expects):
        for ix, exp in enumerate(expects):
            for j, e in enumerate(exp):
                self.assertEqual(str(mock_logging.call_args_list[ix][0][j]), str(e))
        self.assertEqual(len(mock_logging.call_args_list), len(expects))

if __name__ == '__main__':
    unittest.main()
