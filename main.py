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
import shutil
import pyttsx3


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
        '''
        changes status of owner's presence in home from on to off or vice versa
        '''
        self.ftpMain.cwd("/../htdocs")
        self.ftpMain.rename(fromStatus, toStatus)

    def change_known_flag(self, toFlag, name=None):
        '''
        00 -> intruder is not friendly so keep gate closed.
        10 -> intruder is friendly but do not register face. Open gate.
        11 -> intruder is friendly and register face. Open gate.
        '''
        self.ftpMain.cwd("/../htdocs")
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
        for file in flags:
            if file in files:
                self.ftpMain.rename(file, toFlag)
                print("File has been renamed from", file, "to", toFlag)
                break

        try:
            self.ftpMain.rename("incomplete.txt", "complete.txt")
        except:
            print("Could not be renamed")

    def run(self):
        '''
        checks for new intruders and downloads their photos if any
        '''
        self.ftpMain.cwd('/htdocs/photos')
        ftp = self.ftpMain
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

                    print(r)
                else:
                    pass
                    #print("File already downloaded")
        #ftp.quit()
        print(path)

        if new:
            self.getLatestPhoto()
            print("latest photo copied!")

        return new

    def getLatestPhoto(self):
        '''
        copies latest photo of intruder in 'Intruders' directory
        '''
        if "intruder.jpg" in os.listdir():
            os.remove("intruder.jpg")

        latestFolder = os.listdir()[-1]
        latestFile = os.listdir(latestFolder)[-1]  # latest intruder
        shutil.copy(latestFolder + "/" + latestFile, "intruder.jpg")


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

        username = "epiz_33843178"
        password = "QOMgsUul412mh"

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
        new = self.obj.run()
        if new:
            self.send_notification()
        else:
            print("No new intruders")

    def send_notification(self):
        plyer.notification.notify(title='INTRUDER ALERT!', message='Watchdog has detected a new intruder! Tap to view!')
        speech = pyttsx3.init()
        text = "Warning! Intruder alert! Warning! Intruder Alert!"
        speech.say(text)
        speech.runAndWait()

        if self.status:  # if owner is home
            self.callPopupMain()

    def callPopupMain(self):
        Factory.PopupMain().open()

    def callPopupRegister(self):
        Factory.PopupRegister().open()

    def callPopupSuccessful(self):
        print("I dont know Walt. You've been acting sauce lately. It seems like we have an impostor among us")
        Factory.PopupSuccessful().open()
        speech = pyttsx3.init()
        text = "I dont know Walt. You've been acting sauce lately. It seems like we have an impostor among us"
        speech.say(text)
        speech.runAndWait()

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


if __name__ == "__main__":
    LabelBase.register(name="MPoppins", fn_regular=os.getcwd()+"\MPoppins.ttf")
    LabelBase.register(name="BPoppins", fn_regular=os.getcwd()+"\BPoppins.ttf")
    Watchdog().run()