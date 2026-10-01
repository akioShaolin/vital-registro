"""Apply actual Android system-bar/IME overlap without new dependencies."""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger

from vitalregistro.insets import content_insets


class AndroidInsets:
    def __init__(self, callback):
        self.callback = callback
        self.event = None
        self.busy = False
        self.warned = False

    def start(self):
        if self.event is None:
            self.event = Clock.schedule_interval(self.refresh, .25)
            self.refresh()

    def stop(self):
        if self.event is not None:
            self.event.cancel()
            self.event = None

    def refresh(self, *_):
        if self.busy:
            return
        self.busy = True
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def read():
            result = None
            try:
                from jnius import autoclass
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                window = activity.getWindow()
                decor = window.getDecorView()
                view = activity.findViewById(16908290)  # android.R.id.content
                sdk = autoclass("android.os.Build$VERSION").SDK_INT
                # Light background: dark status/navigation icons.
                flags = decor.getSystemUiVisibility() | 8192
                if sdk >= 26:
                    flags |= 16
                if flags != decor.getSystemUiVisibility():
                    decor.setSystemUiVisibility(flags)
                location = [0, 0]
                view.getLocationOnScreen(location)
                vw, vh = view.getWidth(), view.getHeight()
                if vw <= 0 or vh <= 0:
                    return
                if sdk >= 30:
                    metrics = activity.getWindowManager().getCurrentWindowMetrics()
                    bounds = metrics.getBounds()
                    insets = decor.getRootWindowInsets()
                    if insets is None:
                        return
                    kinds = autoclass("android.view.WindowInsets$Type")
                    edge = insets.getInsets(kinds.systemBars() | kinds.displayCutout() | kinds.ime())
                    width, height = bounds.width(), bounds.height()
                    x, y = location[0] - bounds.left, location[1] - bounds.top
                    safe = (edge.left, edge.top, width - edge.right, height - edge.bottom)
                else:
                    visible = autoclass("android.graphics.Rect")()
                    decor.getWindowVisibleDisplayFrame(visible)
                    origin = [0, 0]
                    decor.getLocationOnScreen(origin)
                    width, height = decor.getWidth(), decor.getHeight()
                    x, y = location[0] - origin[0], location[1] - origin[1]
                    safe = (visible.left - origin[0], visible.top - origin[1],
                            visible.right - origin[0], visible.bottom - origin[1])
                result = content_insets((width, height), (x, y, x + vw, y + vh), safe,
                                        (Window.width / vw, Window.height / vh))
            except Exception:
                if not self.warned:
                    Logger.warning("VitalRegistro: Android insets unavailable; retaining safe padding")
                    self.warned = True
            finally:
                Clock.schedule_once(lambda dt: self.deliver(result), 0)
        read()

    def deliver(self, result):
        self.busy = False
        if self.event is not None and result is not None:
            self.callback(result)
