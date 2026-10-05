from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.metrics import dp


class VitalButton(Button):
    primary = BooleanProperty(False)


class BodyLabel(Label):
    pass


class Field(TextInput):
    pass


class ChoiceOption(SpinnerOption):
    pass


class ChoiceSpinner(Spinner):
    """Keep the selection on the button; show only alternatives in its menu."""

    def __init__(self, **kwargs):
        kwargs.setdefault("option_cls", ChoiceOption)
        super().__init__(**kwargs)
        self.bind(text=self._update_dropdown)

    def _update_dropdown(self, *_):
        super()._update_dropdown()
        if self._dropdown:
            for option in list(self._dropdown.container.children):
                if option.text == self.text:
                    self._dropdown.container.remove_widget(option)


def button(text, callback, primary=False):
    item = VitalButton(text=text, primary=primary)
    item.bind(on_release=lambda *_: callback())
    return item


def column():
    layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
    layout.bind(minimum_height=layout.setter("height"))
    return layout


def dialog(title, content, height=340):
    popup = Popup(title=title, content=content, size_hint=(.94, None), height=dp(height),
                  background="", background_color=(.94, .97, 1, 1),
                  title_color=(.06, .15, .29, 1), separator_color=(.1, .4, .7, 1))
    popup.open()
    return popup


def _wheel_dialog(title, wheel, callback):
    from kivy.core.window import Window
    content = BoxLayout(orientation="vertical", spacing=dp(8))
    content.add_widget(BodyLabel(text="Role as colunas. O valor central fica destacado.", font_size="14sp"))
    content.add_widget(wheel)
    popup = dialog(title, content, min(460, Window.height / dp(1) * .88))

    def confirm():
        callback(wheel.value())
        popup.dismiss()
    content.add_widget(button("Confirmar", confirm, True))
    content.add_widget(button("Cancelar", popup.dismiss))
    return popup


def date_picker(value, callback):
    from .wheels import DateWheelPicker
    return _wheel_dialog("Data da medição", DateWheelPicker(value), callback)


def time_picker(value, callback):
    from .wheels import TimeWheelPicker
    return _wheel_dialog("Horário da medição", TimeWheelPicker(value), callback)
