"""Read a user-selected document through SAF; no storage permission."""
from threading import Thread
from kivy.clock import Clock
from .import_csv import MAX_BYTES

class AndroidImporter:
    REQUEST_CODE = 7413

    def __init__(self):
        self.pending = None

    def open(self, callback):
        from android import activity
        from android.runnable import run_on_ui_thread
        from jnius import autoclass
        if self.pending is not None:
            raise RuntimeError("Uma importação já está em andamento.")
        self.pending = callback
        try:
            activity.bind(on_activity_result=self._result)
        except Exception as exc:
            self.pending = None
            raise RuntimeError("Não foi possível iniciar a importação.") from exc

        @run_on_ui_thread
        def launch():
            try:
                Intent = autoclass("android.content.Intent")
                host = autoclass("org.kivy.android.PythonActivity").mActivity
                intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
                intent.addCategory(Intent.CATEGORY_OPENABLE)
                # Providers use different MIME types for CSV; content is validated strictly.
                intent.setType("*/*")
                host.startActivityForResult(intent, self.REQUEST_CODE)
            except Exception:
                self._finish(None, "Não foi possível abrir o seletor de arquivos.")
        launch()

    def _finish(self, payload, error):
        from android import activity
        activity.unbind(on_activity_result=self._result)
        callback, self.pending = self.pending, None
        if callback:
            Clock.schedule_once(lambda _: callback(payload, error), 0)

    def _result(self, request_code, result_code, intent):
        if request_code != self.REQUEST_CODE or self.pending is None:
            return
        if result_code != -1 or intent is None:
            self._finish(None, "Importação cancelada.")
            return
        try:
            uri = intent.getData()
            if uri is None:
                raise ValueError()
        except Exception:
            self._finish(None, "Documento indisponível.")
            return
        Thread(target=self._read, args=(uri,), daemon=True).start()

    def _read(self, uri):
        stream = None
        payload = bytearray()
        error = None
        try:
            from jnius import autoclass
            host = autoclass("org.kivy.android.PythonActivity").mActivity
            stream = host.getContentResolver().openInputStream(uri)
            if stream is None:
                raise OSError()
            buffer = bytearray(8192)
            while True:
                count = stream.read(buffer)
                if count == -1:
                    break
                if count <= 0:
                    raise OSError("Document stream made no progress")
                if len(payload) + count > MAX_BYTES:
                    raise ValueError("CSV excede o limite de 10 MiB.")
                payload.extend(buffer[:count])
        except ValueError as exc:
            error = str(exc)
        except Exception:
            error = "Não foi possível ler o documento. Nada foi importado."
        finally:
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    error = "Falha ao fechar o documento. Nada foi importado."
        result = bytes(payload) if error is None else None
        Clock.schedule_once(lambda _: self._finish(result, error), 0)
