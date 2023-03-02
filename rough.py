import kivy.app
import plyer

class PushNotificationApp(kivy.app.App):
    def show_notification(self):
        plyer.notification.notify(title='test', message="Notification using plyer")

app = PushNotificationApp()
app.run()