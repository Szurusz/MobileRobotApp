# -*- coding: utf-8 -*-

from kivy.clock import Clock

import GlobalShared
import threading
import time
import kivy
from socket import *
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


# warunek rozmiaru okna dla systemów innych niż android
if kivy.platform != 'android' or kivy.platform != 'ios':
    Window.size = (700, 500)


class StartPage(Screen):
    def connect_button(self, widget):
        try:
            # deklaracja socketu
            global s
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((self.manager.get_screen("start").ids.IP.text, 8000))
            # do robota 192.168.2.(numer robota); do matlaba "127.0.0.1"
            s.settimeout(10)
            widget.text = "Połączono"
            self.manager.current = "main"
            GlobalShared.online = True
        except Exception:
            widget.text = "Błąd połączenia"
            GlobalShared.online = False

    def reset_data(self):
        self.manager.get_screen("start").ids.IP.text = ''
        self.manager.get_screen("main").ids.send.text = "[000000]"
        self.manager.get_screen("main").ids.left.value = 0
        self.manager.get_screen("main").ids.right.value = 0


class MainPage(Screen):

    def lost_connection(self):
        self.manager.current = 'start'
        self.manager.transition.direction = 'right'
        self.manager.get_screen("start").ids.is_connect.text = "Utracono połączenie"

    def disconnect_button(self):
        self.manager.current = 'start'
        self.manager.get_screen("start").ids.is_connect.text = "Rozłączono"
        GlobalShared.online = False
        s.close()

    def thread_send(self):
        ref_to_send = self.manager.get_screen("main").ids.send
        ref_to_recv = self.manager.get_screen("main").ids.recv
        global T
        T = threading.Thread(target=self.manager.get_screen("main").sending_data, args=(ref_to_send, ref_to_recv))
        T.daemon = True
        T.start()

    def sending_data(self, send_data, recv_data):
        try:
            while GlobalShared.online:
                time.sleep(0.1)
                global s
                s.send(send_data.text.encode())
                data = s.recv(1024)
                recv_data.text = data.decode("utf-8")
                self.update_widgets(recv_data.text)
                if not recv_data:
                    GlobalShared.online = False
        except Exception:
            Clock.schedule_once(lambda dt: self.lost_connection(), 0)

    def get_sensor_vals(self, recv):
        recv_list = list(recv)
        state = int("".join(recv_list[1:3]), 16)
        battery = int("".join(recv_list[3:7]), 16)
        sensor1 = int("".join(recv_list[7:11]), 16)
        sensor2 = int("".join(recv_list[11:15]), 16)
        sensor3 = int("".join(recv_list[15:19]), 16)
        sensor4 = int("".join(recv_list[19:23]), 16)
        sensor5 = int("".join(recv_list[23:27]), 16)
        return state, battery, sensor1, sensor2, sensor3, sensor4, sensor5

    def update_widgets(self, recv):
        max_sensor_level = 53255
        data = self.get_sensor_vals(recv)
        state_label = self.manager.get_screen("setting").ids.state_label
        battery_widget = self.manager.get_screen("setting").ids.battery_widget
        sensor1_widget = self.manager.get_screen("setting").ids.sensor1_widget
        sensor2_widget = self.manager.get_screen("setting").ids.sensor2_widget
        sensor3_widget = self.manager.get_screen("setting").ids.sensor3_widget
        sensor4_widget = self.manager.get_screen("setting").ids.sensor4_widget
        sensor5_widget = self.manager.get_screen("setting").ids.sensor5_widget
        match str(data[0]):
            case "0":
                state_label.text = "Dane odczytano prawidłowo."
            case "1":
                state_label.text = "Brak znaku kończącego ramkę przed znakiem rozpoczynającym."
            case "2":
                state_label.text = "Ramka zbyt długa."
            case "3":
                state_label.text = "Brak znaku rozpoczynającego ramkę przed znakiem kończącym."
            case "4":
                state_label.text = "Zła wielkość ramki."
            case "5":
                state_label.text = "Błąd dekodowania danych"
            case "6":
                state_label.text = "Błąd połączenia z robotem Pololu3Pi"
            case _:
                pass
        battery_widget.text = str(data[1])
        sensor1_widget.level = data[2] / max_sensor_level
        sensor2_widget.level = data[3] / max_sensor_level
        sensor3_widget.level = data[4] / max_sensor_level
        sensor4_widget.level = data[5] / max_sensor_level
        sensor5_widget.level = data[6] / max_sensor_level

    def update_led1_value(self, state, data):
        if state == "down":
            data_list = list(data.text)
            data_list[2] = '2'
            data.text = "".join(data_list)
        if state == "normal":
            data_list = list(data.text)
            data_list[2] = '0'
            data.text = "".join(data_list)

    def update_led2_value(self, state, data):
        if state == "down":
            data_list = list(data.text)
            data_list[2] = '1'
            data.text = "".join(data_list)
        if state == "normal":
            data_list = list(data.text)
            data_list[2] = '0'
            data.text = "".join(data_list)

    def update_left_slider_values(self, slider, data):
        if slider.value < 0:
            text_value = 256 + int(slider.value)
        else:
            text_value = int(slider.value)
        slider_text = list(format(text_value, 'x').zfill(2))
        data_list = list(data.text)
        data_list[3] = slider_text[0]
        data_list[4] = slider_text[1]
        data.text = "".join(data_list)

    def update_right_slider_values(self, slider, data):
        if slider.value < 0:
            text_value = 256 + int(slider.value)
        else:
            text_value = int(slider.value)
        slider_text = list(format(text_value, 'x').zfill(2))
        data_list = list(data.text)
        data_list[5] = slider_text[0]
        data_list[6] = slider_text[1]
        data.text = "".join(data_list)


class SettingPage(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("main.kv")


class MobileRobotsApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    MobileRobotsApp().run()
