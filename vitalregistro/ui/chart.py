"""Time-scaled charts rendered with Kivy, without matplotlib/native dependencies."""

from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.uix.widget import Widget


class HistoryChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.records = []
        self.series = []
        self.bind(pos=self.redraw, size=self.redraw)

    def set_data(self, records, series):
        self.records, self.series = records, series
        self.redraw()

    def label(self, text, x, y, anchor="left"):
        label = CoreLabel(text=text, font_size=dp(11), color=(.12, .2, .3, 1))
        label.refresh()
        texture = label.texture
        if anchor == "right":
            x -= texture.width
        Color(1, 1, 1, 1)
        Rectangle(texture=texture, pos=(x, y), size=texture.size)

    def redraw(self, *_):
        self.canvas.clear()
        with self.canvas:
            if not self.records:
                self.label("Sem registros neste período.", self.x + dp(12), self.center_y)
                return
            values = [float(getattr(r, field)) for field, _ in self.series for r in self.records]
            low, high = min(values), max(values)
            margin = max((high - low) * .15, 1)
            low, high = max(0, low - margin), high + margin
            ticks = [f"{low + (high - low) * i / 4:.1f}" for i in range(5)]
            # Measure axis labels instead of assuming a fixed 44dp gutter.
            label_width = 0
            for text in ticks:
                label = CoreLabel(text=text, font_size=dp(11))
                label.refresh()
                label_width = max(label_width, label.texture.width)
            left, bottom = self.x + label_width + dp(12), self.y + dp(40)
            width, height = max(1, self.right - left - dp(16)), max(1, self.height - dp(65))
            first, last = self.records[0].measured_at, self.records[-1].measured_at
            seconds = (last - first).total_seconds()
            for i in range(5):
                y = bottom + height * i / 4
                Color(.82, .87, .92, 1)
                Line(points=[left, y, left + width, y], width=1)
                self.label(ticks[i], left - dp(8), y - dp(5), "right")
            self.label(first.strftime("%d/%m/%y"), left, self.y + dp(12))
            if seconds:
                self.label(last.strftime("%d/%m/%y"), left + width, self.y + dp(12), "right")
            for field, color in self.series:
                points = []
                for record in self.records:
                    x = left + width * ((record.measured_at - first).total_seconds() / seconds if seconds else .5)
                    y = bottom + height * (float(getattr(record, field)) - low) / (high - low)
                    points.extend((x, y))
                Color(*color)
                if len(points) > 2:
                    Line(points=points, width=dp(1.5))
                for x, y in zip(points[::2], points[1::2]):
                    Ellipse(pos=(x - dp(3), y - dp(3)), size=(dp(6), dp(6)))
