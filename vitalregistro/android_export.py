"""Storage Access Framework; no storage permission or public temporary files."""

from kivy.clock import Clock


class AndroidExporter:
    REQUEST_CODE = 7412

    def __init__(self):
        self.pending = None

    def save(self, text, filename, callback):
        from android import activity
        from android.runnable import run_on_ui_thread
        from jnius import autoclass

        if self.pending is not None:
            raise RuntimeError("Uma exportação já está em andamento.")
        self.pending = (text, callback)
        activity.bind(on_activity_result=self._result)

        @run_on_ui_thread
        def launch():
            try:
                Intent = autoclass("android.content.Intent")
                host = autoclass("org.kivy.android.PythonActivity").mActivity
                intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
                intent.addCategory(Intent.CATEGORY_OPENABLE)
                intent.setType("text/csv")
                intent.putExtra(Intent.EXTRA_TITLE, filename)
                host.startActivityForResult(intent, self.REQUEST_CODE)
            except Exception:
                self._finish("Não foi possível abrir o seletor de arquivos.")
        launch()

    def _finish(self, message):
        from android import activity
        activity.unbind(on_activity_result=self._result)
        pending, self.pending = self.pending, None
        if pending:
            callback = pending[1]
            Clock.schedule_once(lambda dt: callback(message), 0)

    def _result(self, request_code, result_code, intent):
        if request_code != self.REQUEST_CODE or self.pending is None:
            return
        if result_code != -1 or intent is None:
            self._finish("Exportação cancelada.")
            return
        stream = None
        try:
            from jnius import autoclass
            host = autoclass("org.kivy.android.PythonActivity").mActivity
            stream = host.getContentResolver().openOutputStream(intent.getData(), "wt")
            if stream is None:
                raise OSError("Unavailable output stream")
            # Java String handles UTF-8 conversion without signed-byte ambiguity.
            payload = autoclass("java.lang.String")(self.pending[0]).getBytes("UTF-8")
            stream.write(payload)
            stream.flush()
            stream.close()
            stream = None
        except Exception:
            self._finish("Falha ao salvar CSV. O destino pode conter um arquivo incompleto; exporte novamente.")
        else:
            self._finish("CSV salvo no local escolhido.")
        finally:
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
