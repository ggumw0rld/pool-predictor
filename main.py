# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from jnius import autoclass
from android.permissions import request_permissions, Permission
from android import mActivity

# Lấy class Toast của Android để hiện thông báo lỗi
Toast = autoclass('android.widget.Toast')

class PoolPredictorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 40
        self.spacing = 20

        # Tự động xin các quyền cần thiết khi mở app
        request_permissions([
            Permission.SYSTEM_ALERT_WINDOW,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Tiêu đề
        title = Label(
            text="POOL PREDICTOR", 
            font_size='30sp', 
            bold=True, 
            size_hint=(1, 0.2)
        )
        self.add_widget(title)

        # Nút Bật Nút Nổi
        btn_start = Button(
            text="BẬT NÚT NỔI PREDICT", 
            font_size='22sp', 
            background_color=(0.1, 0.7, 0.1, 1), 
            size_hint=(1, 0.3)
        )
        btn_start.bind(on_press=self.start_service)
        self.add_widget(btn_start)

        # Nút Tắt Nút Nổi
        btn_stop = Button(
            text="TẮT NÚT NỔI", 
            font_size='22sp', 
            background_color=(0.8, 0.1, 0.1, 1), 
            size_hint=(1, 0.3)
        )
        btn_stop.bind(on_press=self.stop_service)
        self.add_widget(btn_stop)

        # Hướng dẫn
        hdsd = Label(
            text="Hướng dẫn:\n1. Bật nút nổi\n2. Thoát ra ngoài mở game\n3. Nút PREDICT sẽ nổi lên", 
            font_size='14sp', 
            size_hint=(1, 0.2)
        )
        self.add_widget(hdsd)

    def start_service(self, instance):
        try:
            # Tên class Service khớp với package.domain và package.name
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            mActivity_obj = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Khởi chạy Service chạy ngầm
            service.start(mActivity_obj, '')
            
            # Hiện thông báo thành công
            Toast.makeText(mActivity.getApplicationContext(), "Đã gửi lệnh bật Nút Nổi!", Toast.LENGTH_SHORT).show()
            
        except Exception as e:
            # Nếu có lỗi, hiện lỗi lên màn hình
            error_msg = f"Lỗi bật Service: {str(e)}"
            Toast.makeText(mActivity.getApplicationContext(), error_msg, Toast.LENGTH_LONG).show()
            print(error_msg)

    def stop_service(self, instance):
        try:
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            mActivity_obj = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Tắt Service
            service.stop(mActivity_obj)
            Toast.makeText(mActivity.getApplicationContext(), "Đã tắt Service", Toast.LENGTH_SHORT).show()
            
        except Exception as e:
            error_msg = f"Lỗi tắt Service: {str(e)}"
            Toast.makeText(mActivity.getApplicationContext(), error_msg, Toast.LENGTH_LONG).show()
            print(error_msg)

class PoolPredictorApp(App):
    def build(self):
        return PoolPredictorUI()

if __name__ == '__main__':
    PoolPredictorApp().run()
