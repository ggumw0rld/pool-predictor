# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from jnius import autoclass
from android.permissions import request_permissions, Permission
from android import mActivity
from android.runnable import run_on_ui_thread

# Hàm hiển thị thông báo an toàn trên luồng giao diện
@run_on_ui_thread
def show_toast(message):
    try:
        Toast = autoclass('android.widget.Toast')
        Toast.makeText(mActivity, message, Toast.LENGTH_SHORT).show()
    except Exception as e:
        print("Lỗi hiển thị Toast:", e)

class PoolPredictorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 40
        self.spacing = 20

        # CHỈ XIN QUYỀN BỘ NHỚ (Không xin SYSTEM_ALERT_WINDOW ở đây)
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        title = Label(text="POOL PREDICTOR", font_size='30sp', bold=True, size_hint=(1, 0.2))
        self.add_widget(title)

        btn_start = Button(text="BẬT NÚT NỔI PREDICT", font_size='22sp', background_color=(0.1, 0.7, 0.1, 1), size_hint=(1, 0.3))
        btn_start.bind(on_press=self.start_service)
        self.add_widget(btn_start)

        btn_stop = Button(text="TẮT NÚT NỔI", font_size='22sp', background_color=(0.8, 0.1, 0.1, 1), size_hint=(1, 0.3))
        btn_stop.bind(on_press=self.stop_service)
        self.add_widget(btn_stop)

        hdsd = Label(text="Hướng dẫn:\n1. Bật nút nổi\n2. Thoát ra ngoài mở game\n3. Nút PREDICT sẽ nổi lên", font_size='14sp', size_hint=(1, 0.2))
        self.add_widget(hdsd)

    def start_service(self, instance):
        try:
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            service.start(mActivity, '')
            show_toast("Đã gửi lệnh bật Nút Nổi!")
        except Exception as e:
            show_toast(f"Lỗi: {str(e)}")
            print("Lỗi bật service:", e)

    def stop_service(self, instance):
        try:
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            service.stop(mActivity)
            show_toast("Đã tắt Service")
        except Exception as e:
            show_toast(f"Lỗi: {str(e)}")
            print("Lỗi tắt service:", e)

class PoolPredictorApp(App):
    def build(self):
        return PoolPredictorUI()

if __name__ == '__main__':
    PoolPredictorApp().run()
