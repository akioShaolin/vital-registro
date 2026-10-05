"""SAF fakes cover read/cancel/errors; these are not device tests."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

class Intent:
    ACTION_OPEN_DOCUMENT = "open-document"
    CATEGORY_OPENABLE = "openable"
    def __init__(self, action): self.action = action
    def addCategory(self, value): self.category = value
    def setType(self, value): self.type = value

class ImmediateThread:
    def __init__(self, target, args, daemon): self.target, self.args = target, args
    def start(self): self.target(*self.args)

class AndroidImportTests(unittest.TestCase):
    def setUp(self):
        self.activity, self.host, self.stream = Mock(), Mock(), Mock()
        self.host.getContentResolver.return_value.openInputStream.return_value = self.stream
        self.results = []
        android = ModuleType("android"); android.activity = self.activity
        runnable = ModuleType("android.runnable"); runnable.run_on_ui_thread = lambda f: f
        clock = ModuleType("kivy.clock")
        clock.Clock = SimpleNamespace(schedule_once=lambda f, delay: f(0))
        jnius = ModuleType("jnius")
        jnius.autoclass = {"android.content.Intent": Intent,
                          "org.kivy.android.PythonActivity": SimpleNamespace(mActivity=self.host)}.__getitem__
        modules = patch.dict(sys.modules, {"android": android, "android.runnable": runnable,
                                          "kivy.clock": clock, "jnius": jnius})
        modules.start(); self.addCleanup(modules.stop)
        source = Path(__file__).resolve().parents[1]/"vitalregistro/android_import.py"
        spec=importlib.util.spec_from_file_location("vitalregistro.saf_import_under_test",source)
        self.module=importlib.util.module_from_spec(spec); spec.loader.exec_module(self.module)
        self.module.Thread=ImmediateThread
        self.reader=self.module.AndroidImporter()

    def open(self):
        self.reader.open(lambda payload,error:self.results.append((payload,error)))

    def result(self):
        self.reader._result(self.reader.REQUEST_CODE,-1,SimpleNamespace(getData=lambda:"content://fictional"))

    def test_document_intent_chunked_utf8_and_close(self):
        chunks=iter(['ação, "nota"\n'.encode(), b'end', None])
        def read(buffer):
            chunk=next(chunks)
            if chunk is None: return -1
            buffer[:len(chunk)]=chunk
            return len(chunk)
        self.stream.read.side_effect=read
        self.open()
        intent,code=self.host.startActivityForResult.call_args.args
        self.assertEqual((intent.action,intent.category,intent.type),("open-document","openable","*/*"))
        self.result()
        self.assertEqual(self.results, [('ação, "nota"\nend'.encode(),None)])
        self.stream.close.assert_called_once()
        self.assertIsNone(self.reader.pending)

    def test_cancel_repeated_and_unrelated_result(self):
        for _ in range(2):
            self.open()
            self.reader._result(0,0,None)
            self.assertIsNotNone(self.reader.pending)
            with self.assertRaises(RuntimeError): self.open()
            self.reader._result(self.reader.REQUEST_CODE,0,None)
            self.assertIsNone(self.reader.pending)
        self.stream.read.assert_not_called()
        self.assertTrue(all(payload is None and "cancelada" in error for payload,error in self.results))

    def test_read_failure_and_retry(self):
        self.stream.read.side_effect=OSError("fake")
        self.open(); self.result()
        self.assertIsNone(self.results[0][0])
        self.stream.close.assert_called_once()
        self.open()
        self.assertIsNotNone(self.reader.pending)

    def test_size_limit(self):
        self.module.MAX_BYTES=2
        self.stream.read.return_value=3
        self.open(); self.result()
        self.assertIsNone(self.results[0][0])
        self.assertIn("limite",self.results[0][1])
        self.stream.close.assert_called_once()

    def test_missing_stream_and_close_failure(self):
        self.host.getContentResolver.return_value.openInputStream.return_value=None
        self.open(); self.result()
        self.assertIsNone(self.results[-1][0])
        self.host.getContentResolver.return_value.openInputStream.return_value=self.stream
        self.stream.read.return_value=-1
        self.stream.close.side_effect=OSError("fake")
        self.open(); self.result()
        self.assertIsNone(self.results[-1][0])
        self.assertIn("fechar",self.results[-1][1])

    def test_bind_and_launch_failures_clear_pending(self):
        self.activity.bind.side_effect=RuntimeError("fake")
        with self.assertRaises(RuntimeError): self.open()
        self.assertIsNone(self.reader.pending)
        self.activity.bind.side_effect=None
        self.host.startActivityForResult.side_effect=RuntimeError("fake")
        self.open()
        self.assertIsNone(self.reader.pending)
        self.assertIn("seletor",self.results[-1][1])
