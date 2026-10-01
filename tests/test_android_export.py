"""Test SAF callback/error behavior with fakes, not a claim of device validation."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class Intent:
    ACTION_CREATE_DOCUMENT = "create-document"
    CATEGORY_OPENABLE = "openable"
    EXTRA_TITLE = "title"

    def __init__(self, action):
        self.action = action

    def addCategory(self, value):
        self.category = value

    def setType(self, value):
        self.type = value

    def putExtra(self, key, value):
        self.filename = value


class AndroidExportTests(unittest.TestCase):
    def setUp(self):
        self.activity = Mock()
        self.host = Mock()
        self.stream = Mock()
        self.host.getContentResolver.return_value.openOutputStream.return_value = self.stream
        self.messages = []
        android = ModuleType("android")
        android.activity = self.activity
        runnable = ModuleType("android.runnable")
        runnable.run_on_ui_thread = lambda function: function
        clock = ModuleType("kivy.clock")
        clock.Clock = SimpleNamespace(schedule_once=lambda function, delay: function(0))
        jnius = ModuleType("jnius")
        classes = {"android.content.Intent": Intent,
                   "org.kivy.android.PythonActivity": SimpleNamespace(mActivity=self.host),
                   "java.lang.String": lambda text: SimpleNamespace(getBytes=lambda encoding: text.encode(encoding))}
        jnius.autoclass = classes.__getitem__
        modules = patch.dict(sys.modules, {"android": android, "android.runnable": runnable,
                                          "kivy.clock": clock, "jnius": jnius})
        modules.start()
        self.addCleanup(modules.stop)
        source = Path(__file__).resolve().parents[1] / "vitalregistro/android_export.py"
        spec = importlib.util.spec_from_file_location("saf_under_test", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.exporter = module.AndroidExporter()

    def test_utf8_and_intent_without_storage_permissions(self):
        text = 'FICTÍCIO, "ação"\r\nsegunda linha'
        self.exporter.save(text, "example.csv", self.messages.append)
        intent, code = self.host.startActivityForResult.call_args.args
        self.assertEqual((intent.action, intent.category, intent.type), ("create-document", "openable", "text/csv"))
        self.assertEqual(intent.filename, "example.csv")
        result = SimpleNamespace(getData=lambda: "content://fictional")
        self.exporter._result(code, -1, result)
        self.stream.write.assert_called_once_with(text.encode("utf-8"))
        self.stream.close.assert_called_once()
        self.assertIsNone(self.exporter.pending)
        self.assertIn("salvo", self.messages[0])

    def test_cancel_then_export_again(self):
        for _ in range(2):
            self.exporter.save("fictitious", "example.csv", self.messages.append)
            self.exporter._result(self.exporter.REQUEST_CODE, 0, None)
            self.assertIsNone(self.exporter.pending)
        self.stream.write.assert_not_called()
        self.assertEqual(self.messages, ["Exportação cancelada."] * 2)

    def test_unrelated_result_keeps_pending_and_blocks_duplicate(self):
        self.exporter.save("fictitious", "example.csv", self.messages.append)
        self.exporter._result(0, 0, None)
        self.assertIsNotNone(self.exporter.pending)
        with self.assertRaises(RuntimeError):
            self.exporter.save("second", "second.csv", self.messages.append)

    def test_write_error_closes_stream_and_allows_retry(self):
        self.stream.write.side_effect = OSError("fake failure")
        self.exporter.save("fictitious", "example.csv", self.messages.append)
        self.exporter._result(self.exporter.REQUEST_CODE, -1, SimpleNamespace(getData=lambda: "content://fictional"))
        self.stream.close.assert_called_once()
        self.assertIsNone(self.exporter.pending)
        self.assertIn("incompleto", self.messages[0])
        self.exporter.save("retry", "retry.csv", self.messages.append)

    def test_listener_failure_does_not_leave_export_stuck(self):
        self.activity.bind.side_effect = RuntimeError("fake listener failure")
        with self.assertRaises(RuntimeError):
            self.exporter.save("fictitious", "example.csv", self.messages.append)
        self.assertIsNone(self.exporter.pending)

    def test_picker_launch_failure_is_reported_and_cleared(self):
        self.host.startActivityForResult.side_effect = RuntimeError("fake missing picker")
        self.exporter.save("fictitious", "example.csv", self.messages.append)
        self.assertIsNone(self.exporter.pending)
        self.assertIn("seletor", self.messages[0])
