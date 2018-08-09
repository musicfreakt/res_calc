# -*- coding: utf-8 -*-
import os
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivymd.button import MDIconButton
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.label import MDLabel
from kivymd.list import ILeftBodyTouch

ROOT_DIR = os.path.dirname(__file__)
KV_DIR = os.path.join(ROOT_DIR, "kv")

reload(sys)
sys.setdefaultencoding('utf8')

__version__ = '0.1.1'

# ------------------------ Константы и переменные ------------------------

BUTTON_COLORS = (  # все возможные цвета для колец резистора
    (.70, .70, .70, 1),  # серебряный
    (.94, .64, .4, 1),  # золотой
    (0, 0, 0, 1),  # черный
    (.36, .25, .22, 1),  # коричневый
    (.91, .30, .24, 1),  # красный
    (.90, .49, .13, 1),  # оранжевый
    (1, .92, .23, 1),  # желтый
    (.15, .68, .38, 1),  # зеленый
    (.16, .50, .73, 1),  # синий
    (.56, .27, .68, 1),  # фиолетовый
    (.58, .65, .65, 1),  # серый
    (1, 1, 1, 1)  # белый
)
MULTIPLIERS = (  # все возможные множители резистора
    0.01,
    0.1,
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000,
    10000000,
    100000000,
    1000000000
)

BUTTON_MULTIPLIERS = ('x0.01', 'x0.1', 'x1', 'x10', 'x100', 'x1k', 'x10k', 'x100k', 'x1M', 'x10M', 'x100M', 'x1G')

TOLERANCES = ("10%", "5%", "1%", "2%", "0.5%", "0.25%", "0.1%", "0.05%")  # все возможные значения допусков резистора

NUM_ROWS = 12  # количество рядов столбца


# ------------------------ Классы ------------------------
class Scr(Screen):
    ''' Класс родитель для других классов ,
        предназначенных для вычисления сопротивлений
        разных типов резисторов
        Методы класса:
            format_result(self, value):
                Изменение значений сопротивлений(value) в
                более удобный и понятный вид.
            is_int(self, value):
                Проверка того, является ли переменная(value) целочисленной или нет
    '''

    def __init__(self, **kwargs):
        '''Конструктор класса'''
        super(Scr, self).__init__(**kwargs)

    def format_result(self, value):
        '''Изменение значений сопротивлений в более удобный вид'''
        s = " Om "
        if value >= MULTIPLIERS[11]:  # если сопротивление больше 10^8 , то
            value /= MULTIPLIERS[11]  # делим сопротивление на 10^8 и
            s = " GOm "             # добавляем десятичную приставку
        elif value >= MULTIPLIERS[8]:
            value /= MULTIPLIERS[8]
            s = " MOm "
        elif value >= MULTIPLIERS[5]:
            value /= MULTIPLIERS[5]
            s = " kOm "
        if self.is_int(value):  # если значение целое число, то
            value = int(value)  # округляем float до int
        return (str(value) + s)

    def is_int(self, n):
        '''Проверка того, является ли переменная целочисленной или нет'''
        return not (n % 1)


class FourRingsScreen(Scr):
    ''' Класс, предназначенный для вычисления сопротивлений
        резисторов, имеющих четырехполосную маркировку
        Методы класса:
            calculation(self, instance):
                Метод, производящий вычисление сопротивления,
                по заданным параметрам резистора
    '''
    def __init__(self, **kwargs):
        super(FourRingsScreen, self).__init__(**kwargs)
        NUM_COLS = 4  # количество столбцов
        self.resistor_params = ["1", "0", "0.1", "1%"]  # параметры резистора
        self.cols_heads = ["1st ring", "2nd ring", "Multiplier", "Tolerance"]  # Названия каждого столбца

        parent = BoxLayout(orientation="vertical")
        params_table = BoxLayout()  # таблица с параметрами резистора
        self.result = MDLabel(text='1 Om ± 1%', font_style='Display1', theme_text_color='Primary', halign='center', size_hint_y=None)  # результат вычислений сопротивления

        # СОЗДАЕМ ТАБЛИЦУ С ПАРАМЕТРАМИ РЕЗИСТОРА
        column = 0  # текущий столбец
        for column in range(NUM_COLS):  # пока текущий столбец меньше или равен общему количеству столбцов, то
            col = GridLayout(id=str(column), cols=1, spacing=5, padding=[5, 5, 5, 5])
            col.add_widget(MDLabel(font_style='Body1', theme_text_color='Primary', text=self.cols_heads[column], halign='center'))  # Создаем Label с названием текущего столбца
            if column < 2:  # если текущий столбец меньше 3 , то
                row = 2  # текущий ряд столбца
                button = 0  # текущая позиция кнопки в столбце
                col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))  # выводим 2 Label с -, т.к
                col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))  # первых двух кнопок нет
                while row < NUM_ROWS:  # пока текущий ряд меньше 12, то
                    if row == 6 or row == 11:  # если ряд 6 или 11, то
                        col.add_widget(  # создаем кнопку с черным текстом(чтоб белый текст не сливался с желтым и белым цветом кнопки)
                            Button(
                                id=str(column),
                                text=str(button),
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                color=(0, 0, 0, 1),
                                on_press=self.calculation))
                    else:
                        col.add_widget(  # иначе создаем кнопку с белым текстом
                            Button(
                                id=str(column),
                                text=str(button),
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_press=self.calculation))
                    row += 1  # увеличиваем ряд столбца
                    button += 1  # увеличиваем текущую позицию кнопки в столбце
            elif column == 2:  # если текущий столбец - 3 , то
                row = 0  # текущий ряд столбца
                for row in range(NUM_ROWS):  # пока текущий ряд меньше 12, то
                    if row == 6 or row == 11:   # если ряд 6 или 11, то
                        col.add_widget(  # создаем кнопку с черным текстом(чтоб белый текст не сливался с желтым и белым цветом кнопки)
                            Button(
                                id=str(column),
                                text=BUTTON_MULTIPLIERS[row],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                color=(0, 0, 0, 1),
                                on_release=self.calculation))
                    else:
                        col.add_widget(
                            Button(  # иначе создаем кнопку с белым текстом
                                id=str(column),
                                text=BUTTON_MULTIPLIERS[row],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_release=self.calculation))
            elif column == 3:
                row = 0  # текущий ряд
                button = 0  # текущая позиция кнопки в столбце
                for row in range(NUM_ROWS):  # пока текущий ряд меньше 12, то
                    if (row == 2 or row == 5 or row == 6 or row == 11):   # если номер ряда 2, 5, 6 или 11, то
                        col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))  # отображаем заглушку вместо кнопки
                    else:
                        col.add_widget(  # иначе отображаем кнопку
                            Button(
                                id=str(column),
                                text=TOLERANCES[button],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_release=self.calculation))
                        button += 1  # увеличиваем текущую позицию кнопки в столбце
            params_table.add_widget(col)  # добавляем текущий столбец в таблицу

        parent.add_widget(self.result)
        parent.add_widget(params_table)
        self.add_widget(parent)

    def calculation(self, instance):
        '''Метод, производящий вычисление сопротивления, по заданным параметрам резистора'''
        self.resistor_params[int(instance.id)] = str(instance.text)   # устанавливаем параметры резистора
        resistance = int(self.resistor_params[0] + self.resistor_params[1]) * float(self.resistor_params[2])   # первые 2 значения резистора умножаем на множитель
        self.result.text = self.format_result(resistance) + "± " + self.resistor_params[3]   # изменяем значение Label


class FiveRingsScreen(Scr):
    ''' Класс, предназначенный для вычисления сопротивлений
        резисторов, имеющих пятиполосную маркировку
        Методы класса:
            calculation(self, instance):
                Метод, производящий вычисление сопротивления,
                по заданным параметрам резистора
    '''
    def __init__(self, **kwargs):
        super(FiveRingsScreen, self).__init__(**kwargs)
        NUM_COLS = 5

        self.resistor_params = ["1", "0", "0", "0.01", "1%"]
        self.cols_heads = ["1st ring", "2nd ring", "3rd ring", "Multiplier", "Tolerance"]
        parent = BoxLayout(orientation="vertical")
        params_table = BoxLayout()
        self.result = MDLabel(text='1 Om ± 1%', font_style='Display1', theme_text_color='Primary', halign='center', size_hint_y=None)

        column = 0
        for column in range(NUM_COLS):
            col = GridLayout(id=str(column), cols=1, spacing=5, padding=[5, 5, 5, 5])
            col.add_widget(MDLabel(font_style='Body1', theme_text_color='Primary', text=self.cols_heads[column], halign='center'))
            if column < 3:
                row = 2
                button = 0
                col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))
                col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))
                while row < NUM_ROWS:
                    if row == 6 or row == 11:
                        col.add_widget(
                            Button(
                                id=str(column),
                                text=str(button),
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                color=(0, 0, 0, 1),
                                on_press=self.calculation))
                    else:
                        col.add_widget(
                            Button(
                                id=str(column),
                                text=str(button),
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_press=self.calculation))
                    row += 1
                    button += 1
            elif column == 3:
                row = 0
                for row in range(NUM_ROWS):
                    if row == 6 or row == 11:
                        col.add_widget(
                            Button(
                                id=str(column),
                                text=BUTTON_MULTIPLIERS[row],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                color=(0, 0, 0, 1),
                                on_release=self.calculation))
                    else:
                        col.add_widget(
                            Button(
                                id=str(column),
                                text=BUTTON_MULTIPLIERS[row],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_release=self.calculation))
            elif column == 4:
                row = 0
                button = 0
                for row in range(NUM_ROWS):
                    if (row == 2 or row == 5 or row == 6 or row == 11):
                        col.add_widget(MDLabel(text="-", font_style='Body1', theme_text_color='Primary', halign='center'))
                    else:
                        col.add_widget(
                            Button(
                                id=str(column),
                                text=TOLERANCES[button],
                                background_normal='',
                                background_color=BUTTON_COLORS[row],
                                on_release=self.calculation))
                        button += 1
            params_table.add_widget(col)

        parent.add_widget(self.result)
        parent.add_widget(params_table)
        self.add_widget(parent)

    def calculation(self, instance):
        '''Метод, производящий вычисление сопротивления, по заданным параметрам резистора'''
        self.resistor_params[int(instance.id)] = str(instance.text)  # устанавливаем параметры резистора
        resistance = int(self.resistor_params[0] + self.resistor_params[1] + self.resistor_params[2]) * float(self.resistor_params[3])  # первые 3 значения резистора умножаем на множитель
        self.result.text = self.format_result(resistance) + "± " + self.resistor_params[4]  # изменяем значение Label


class SMDScreen(Scr):
    ''' Класс, предназначенный для вычисления
        сопротивлений SMD резисторов
        Методы класса:
            calculation(self, instance):
                Метод, производящий вычисление сопротивления,
                по заданным параметрам резистора
            get_code_value(self, digits, letter):
                Получение значения сопротивления резистора
                с маркировкой EIA-96. По таблице находим
                значения, совпадающие с кодом digits, и множитель.
                Возвращаем произведение значения и множителя
    '''
    result = StringProperty()

    def __init__(self, **kwargs):
        super(SMDScreen, self).__init__(**kwargs)
        self.result = ""

    def calculation(self, instance):
        '''Метод, производящий вычисление сопротивления, по заданным параметрам резистора'''
        user_input = instance.text  # значение, полученное из textinputа
        resistance = ''  # сопротивление
        tolerance = ''  # допуск
        if user_input.isdigit():  # если полученное значение - число , то
            if len(user_input) == 3:  # если длина user_input - 3 , то
                resistance = int(user_input[0] + user_input[1]) * pow(10, int(user_input[2]))  # первые два числа из полученного значения умножаем на 10 в степени 3 числа
                tolerance = TOLERANCES[1]
            elif len(user_input) == 4:  # если длина user_input - 4 , то
                resistance = int(user_input[0] + user_input[1] + user_input[2]) * pow(10, int(user_input[3]))   # первые три числа из полученного значения умножаем на 10 в степени 4 числа
                tolerance = TOLERANCES[2]
            self.result = self.format_result(resistance) + "± " + tolerance  # изменяем значение Label
        else:  # если полученное значение не полностью число , то
            try:
                if (user_input.index("R") >= 0) and not(user_input.index("R") == len(user_input) - 1):  # если в полученном значении если Буква R и она находится не на последнем месте, то
                    if(user_input.index("R") == 0):  # если в полученном значении R находится на 1 месте , то
                        resistance = float(user_input.replace("R", "0."))  # заменяем букву R в строке на 0.
                    else:
                        resistance = float(user_input.replace("R", "."))  # иначе заменяем букву R в строке на .
                    self.result = self.format_result(resistance)  # изменяем значение Label
            except ValueError:  # если буквы R в строке нет, то
                if len(user_input) == 3:  # если длина строки - 3
                    tolerance = TOLERANCES[2]
                    digits_code = user_input[0] + user_input[1]  # Первые два символа в строке
                    letter_code = user_input[2]  # последний символ в строке
                    if digits_code.isdigit():  # если первые два символа в строке - число
                        resistance = self.get_code_value(digits_code, letter_code)  # находим в таблице значения и получаем результат
                    self.result = self.format_result(resistance) + "± " + tolerance  # изменяем значение Label

    def get_code_value(self, digits, letter):
        ''' Получение значения сопротивления резистора
            с маркировкой EIA-96. По таблице находим
            значения, совпадающие с кодом digits, и множитель.
            Возвращаем произведение значения и множителя
        '''
        value = 0  # значение сопротивления
        multiplier = 0  # множитель
        digits = int(digits)
        digits_codes = (  # таблица кодов
            0, 100, 102, 105, 107, 110, 113,
            115, 118, 121, 124, 127, 130,
            133, 137, 140, 143, 147, 150,
            154, 158, 162, 165, 169, 174,
            178, 182, 187, 191, 196, 200,
            205, 210, 215, 221, 226, 232,
            237, 243, 249, 255, 261, 267,
            274, 280, 287, 294, 301, 309,
            316, 324, 332, 340, 348, 357,
            365, 374, 383, 392, 402, 412,
            422, 432, 442, 453, 464, 475,
            487, 499, 511, 523, 536, 549,
            562, 576, 590, 604, 619, 634,
            649, 665, 681, 698, 715, 732,
            750, 768, 787, 806, 825, 845,
            866, 887, 909, 931, 953, 976
        )
        if digits < 97:
            value = digits_codes[digits]
        if letter == "Z" or letter == "z":
            multiplier = 0.001
        elif letter == "Y" or letter == "y":
            multiplier = MULTIPLIERS[0]
        elif letter == "X" or letter == "x" or letter == "S" or letter == "s":
            multiplier = MULTIPLIERS[1]
        elif letter == "A" or letter == "a":
            multiplier = MULTIPLIERS[2]
        elif letter == "B" or letter == "b" or letter == "H" or letter == "h":
            multiplier = MULTIPLIERS[3]
        elif letter == "C" or letter == "c":
            multiplier = MULTIPLIERS[4]
        elif letter == "D" or letter == "d":
            multiplier = MULTIPLIERS[5]
        elif letter == "E" or letter == "e":
            multiplier = MULTIPLIERS[6]
        elif letter == "F" or letter == "f":
            multiplier = MULTIPLIERS[7]
        return value * multiplier

    def update_padding(self, text_input, *args):
        text_width = text_input._get_text_width(
            text_input.text,
            text_input.tab_width,
            text_input._label_cached
        )
        text_input.padding_x = (text_input.width - text_width) / 2


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)
        self.add_widget(FourRingsScreen(name="4rings"))
        self.add_widget(FiveRingsScreen(name="5rings"))
        self.add_widget(SMDScreen(name="smd"))
        self.add_widget(SettingsScreen(name="settings"))
        self.add_widget(AboutScreen(name="about"))


class ResCalcApp(App):
    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    title = "ResCalc"
    icon = "data/icon.png"

    def build(self):
        self.load_kv_files(KV_DIR)
        main_widget = Builder.load_file(os.path.join(KV_DIR, "startscreen.kv"))
        self.theme_cls.theme_style = 'Dark'
        return main_widget

    def load_kv_files(self, directory_kv_files):
        Builder.load_file(os.path.join(directory_kv_files, "startscreen.kv"))
        Builder.load_file(os.path.join(directory_kv_files, "smd.kv"))
        Builder.load_file(os.path.join(directory_kv_files, "settings.kv"))
        Builder.load_file(os.path.join(directory_kv_files, "about.kv"))

    def settings(self):
        self.root.ids.manager.current = 'settings'
        return True

    def about(self):
        self.root.ids.manager.current = 'about'
        return True

    def smd(self):
        self.root.ids.manager.current = 'smd'
        return True

    def four_rings(self):
        self.root.ids.manager.current = '4rings'
        return True

    def five_rings(self):
        self.root.ids.manager.current = '5rings'
        return True

    def show_snackbar(self, snack_text):
        Snackbar(text=snack_text).show()


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


if __name__ == '__main__':
    ResCalcApp().run()
