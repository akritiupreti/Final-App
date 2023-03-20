from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
import os
from ftplib import FTP
import plyer
from kivy.factory import Factory
import time
from functools import partial


Window.size = (310, 580)


class Client:
    def __init__(self, user, pw):
        self.username = user
        self.password = pw

        self.ftpMain = FTP()
        server = "ftp.epizy.com"
        port = 21

        print("Connecting to server...")
        self.ftpMain.connect(server, port)
        self.ftpMain.login(self.username, self.password)
        print("Connected!")

    def change_status(self, fromStatus, toStatus):
        self.ftpMain.rename(fromStatus, toStatus)

    def change_known_flag(self, toFlag, name=None):
        '''
        00 -> intruder is not friendly so keep gate closed.
        10 -> intruder is friendly but do not register face. Open gate.
        11 -> intruder is friendly and register face. Open gate.
        '''
        files = self.ftpMain.nlst()
        if toFlag == "11":
            name = "name_"+name+".txt"
            prevName = "none_NONE"
            for file in files:
                if file[:5] == "name_":
                    prevName = file
                    break
            self.ftpMain.rename(prevName, name)

        toFlag = toFlag + ".txt"
        flags = ["00.txt", "10.txt", "11.txt"]
        for file in files:
            if file in flags:
                self.ftpMain.rename(file, toFlag)
                break

        try:
            self.ftpMain.rename("incomplete.txt", "complete.txt")
        except:
            print("Could not be renamed")

    def run(self):
        ftp = self.ftpMain
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
        path = ""
        ext = [".png", ".jpg"]
        for file in files:
            if file[-4:] in ext:
                date = file[:file.find("_")]  # folder name will be the date
                if date not in os.listdir() or file not in os.listdir(date):  # if photo does not exist
                    new = True
                    if not os.path.isdir(date):
                        os.mkdir(date)

                    path = os.path.join(date, file)
                    r = ftp.retrbinary('RETR %s' % file, open(path, 'wb').write)
                    #print(r)
                else:
                    pass
                    #print("File already downloaded")
        #ftp.quit()
        print(path)

        folders = os.listdir()
        folderFiles = os.listdir(folders[-1])[-1]  # latest intruder


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
        self.status = 1

        username = "epiz_33608356"
        password = "HwGN8xvq7ut"

        #username = self.root.get_screen('login').ids.user.text
        #password = self.root.get_screen('login').ids.pw.text
        print(username)
        print(password)

        self.obj = Client(username, password)
        new = self.obj.run()
        if new:
            self.send_notification()
        else:
            print("No new intruders")

        Clock.schedule_interval(self.keep_checking_for_intruders, 5)

    def keep_checking_for_intruders(self, *args):
        username = "epiz_33608356"
        password = "HwGN8xvq7ut"
        #obj = Client(username, password)
        new = self.obj.run()
        if new:
            self.send_notification()
        else:
            print("No new intruders")

    def send_notification(self):
        plyer.notification.notify(title='INTRUDER ALERT!', message='Watchdog has detected a new intruder! Tap to view!')
        if self.status:
            self.callPopupMain()


        '''
        folder_names = os.listdir()

        for folder in folder_names:
            panel = MDExpansionPanel(title=folder, icon="google.png", content=MyContent())
            self.root.ids.panel_container.add_widget(panel)
        '''

    def callPopupMain(self):
        Factory.PopupMain().open()

    def callPopupRegister(self):
        Factory.PopupRegister().open()

    def callPopupSuccessful(self):
        Factory.PopupSuccessful().open()

    def knownFlag(self, flag, name=None):
        print(name)
        self.obj.change_known_flag(flag, name)

    def on_action(self):
        self.status = 1
        try:
            self.obj.change_status("off.txt", "on.txt")
        except:
            pass
        print("switched on")

    def off_action(self):
        self.status = 0
        try:
            self.obj.change_status("on.txt", "off.txt")
        except:
            pass
        print("switched off")

    def buttonclick(self):
        print("Button clicked")


if __name__ == "__main__":
    LabelBase.register(name="MPoppins", fn_regular=os.getcwd()+"\MPoppins.ttf")
    LabelBase.register(name="BPoppins", fn_regular=os.getcwd()+"\BPoppins.ttf")
    Watchdog().run()