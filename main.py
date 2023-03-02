from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
import os
from ftplib import FTP
import plyer
import time


Window.size = (310, 580)


class Client:
    def __init__(self, user, pw):
        self.username = user
        self.password = pw

    def run(self):
        ftp = FTP()
        server = "ftp.epizy.com"
        port = 21
        ftp.connect(server, port)
        ftp.login(self.username, self.password)
        # ftp.login("epiz_33608356", "HwGN8xvq7ut")

        files = ftp.nlst()  # list of files on the server
        # print(files)

        if not os.getcwd()[-9:] == "Intruders":
            try:
                os.chdir("Intruders")
            except:
                os.mkdir("Intruders")
                os.chdir("Intruders")

        new = False
        for file in files:
            if file[-4:] == ".jpg":
                date = file[:file.find("_")]  # folder name will be the date
                if not date in os.listdir() or not file in os.listdir(date):  # if photo does not exist
                    new = True
                    if not os.path.isdir(date):
                        os.mkdir(date)

                    path = os.path.join(date, file)
                    r = ftp.retrbinary('RETR %s' % file, open(path, 'wb').write)
                    print(r)
                else:
                    print("File already downloaded")
        ftp.quit()
        return new


class Watchdog(MDApp):
    def on_start(self):
       pass

    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("main.kv"))
        screen_manager.add_widget(Builder.load_file("login.kv"))
        screen_manager.add_widget(Builder.load_file("home.kv"))
        return screen_manager

    def logger(self):
        username = "epiz_33608356"
        password = "HwGN8xvq7ut"

        #username = self.root.get_screen('login').ids.user.text
        #password = self.root.get_screen('login').ids.pw.text
        print(username)
        print(password)

        obj = Client(username, password)
        new = obj.run()
        if new:
            self.send_notification()
        else:
            print("No new intruders")

        Clock.schedule_interval(self.keep_checking_for_intruders, 5)

    def keep_checking_for_intruders(self, *args):
        username = "epiz_33608356"
        password = "HwGN8xvq7ut"
        obj = Client(username, password)
        new = obj.run()
        if new:
            self.send_notification()
        else:
            print("No new intruders")


    def send_notification(self):
        plyer.notification.notify(title='INTRUDER ALERT!', message='Watchdog has detected a new intruder! Tap to view!')
        '''
        folder_names = os.listdir()

        for folder in folder_names:
            panel = MDExpansionPanel(title=folder, icon="google.png", content=MyContent())
            self.root.ids.panel_container.add_widget(panel)
        '''

    def on_action(self):
        ftp = FTP()
        server = "ftp.epizy.com"
        port = 21
        ftp.connect(server, port)
        ftp.login("epiz_33608356", "HwGN8xvq7ut")
        try:
            ftp.rename("off.txt", "on.txt")
        except:
            pass
        print("switched on")

    def off_action(self):
        ftp = FTP()
        server = "ftp.epizy.com"
        port = 21
        ftp.connect(server, port)
        ftp.login("epiz_33608356", "HwGN8xvq7ut")
        try:
            ftp.rename("on.txt", "off.txt")
        except:
            pass
        print("switched off")


if __name__ == "__main__":
    LabelBase.register(name="MPoppins", fn_regular="E:/Work/Projects/Final-App/MPoppins.ttf")
    LabelBase.register(name="BPoppins", fn_regular="E:/Work/Projects/Final-App/BPoppins.ttf")
    Watchdog().run()