# main.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from jnius import autoclass
from android.permissions import request_permissions, Permission
from android import mActivity
from android.runnable import run_on_ui_thread

@run_on_ui_thread
def show_toast(message):
    try:
        Toast = autoclass('android.widget.Toast')
        Toast.makeText(mActivity, message, Toast.LENGTH_SHORT).show()
    except Exception as e:
        print("Lỗi Toast:", e)

class PoolPredictorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        self.add_widget(Label(text="POOL PREDICTOR", font_size='30sp', bold=True, size_hint=(1, 0.15)))

        btn_start = Button(text="BẬT NÚT NỔI PREDICT", font_size='20sp', background_color=(0.1, 0.7, 0.1, 1), size_hint=(1, 0.2))
        btn_start.bind(on_press=self.start_service)
        self.add_widget(btn_start)

        btn_stop = Button(text="TẮT NÚT NỔI", font_size='20sp', background_color=(0.8, 0.1, 0.1, 1), size_hint=(1, 0.2))
        btn_stop.bind(on_press=self.stop_service)
        self.add_widget(btn_stop)

        # NÚT DEBUG XEM LOG
        btn_debug = Button(text="XEM LOG LỖI", font_size='18sp', background_color=(0.2, 0.5, 0.8, 1), size_hint=(1, 0.2))
        btn_debug.bind(on_press=self.show_log)
        self.add_widget(btn_debug)

    def start_service(self, instance):
        try:
            # Thử cả 2 tên class phòng trường hợp có chữ Foreground
            try:
                service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
                service.start(mActivity, '')
            except:
                service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictorForeground')
                service.start(mActivity, '')
            show_toast("Đã gửi lệnh bật Nút Nổi!")
        except Exception as e:
            show_toast(f"Lỗi gọi Service: {str(e)}")

    def stop_service(self, instance):
        try:
            try:
                service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
                service.stop(mActivity)
            except:
                service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictorForeground')
                service.stop(mActivity)
            show_toast("Đã tắt Service")
        except Exception as e:
            show_toast(f"Lỗi tắt: {str(e)}")

    def show_log(self, instance):
        # Đọc nội dung file log
        log_path = os.path.join(self.app.user_data_dir, "debug_log.txt")
        log_content = "Chưa có log nào. Hãy bấm BẬT NÚT NỔI trước."
        
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                log_content = f.read()

        # Tạo giao diện Popup hiển thị log
        content = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()
        lbl = Label(text=log_content, size_hint_y=None, halign='left', valign='top')
        lbl.bind(width=lambda *x: lbl.setter('text_size')(lbl, (lbl.width, None)))
        lbl.bind(texture_size=lambda *x: lbl.setter('size')(lbl, lbl.texture_size))
        scroll.add_widget(lbl)
        content.add_widget(scroll)

        # Nút Copy
        btn_copy = Button(text="COPY LOG", size_hint=(1, 0.2), background_color=(0, 1, 0, 1))
        content.add_widget(btn_copy)

        popup = Popup(title="Log Lỗi Service", content=content, size_hint=(0.9, 0.9))
        
        def copy_to_clipboard(instance):
            Clipboard.copy(log_content)
            show_toast("Đã Copy Log! Hãy dán vào chat.")
            popup.dismiss()

        btn_copy.bind(on_press=copy_to_clipboard)
        popup.open()

class PoolPredictorApp(App):
    def build(self):
        ui = PoolPredictorUI()
        ui.app = self # Truyền app vào để lấy user_data_dir
        return ui

if __name__ == '__main__':
    PoolPredictorApp().run()
