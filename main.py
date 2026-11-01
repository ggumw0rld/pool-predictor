# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from jnius import autoclass
from android.permissions import request_permissions, Permission

class PoolPredictorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 40
        self.spacing = 20

        # Tự động xin các quyền cần thiết khi mở app
        # (Bao gồm quyền hiển thị đè lên app khác và quyền đọc bộ nhớ)
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
            background_color=(0.1, 0.7, 0.1, 1), # Màu xanh lá
            size_hint=(1, 0.3)
        )
        btn_start.bind(on_press=self.start_service)
        self.add_widget(btn_start)

        # Nút Tắt Nút Nổi
        btn_stop = Button(
            text="TẮT NÚT NỔI", 
            font_size='22sp', 
            background_color=(0.8, 0.1, 0.1, 1), # Màu đỏ
            size_hint=(1, 0.3)
        )
        btn_stop.bind(on_press=self.stop_service)
        self.add_widget(btn_stop)

        # Hướng dẫn
        hdsd = Label(
            text="Hướng dẫn:\n1. Bấm Bật nút nổi\n2. Thoát ra ngoài, mở game Bida\n3. Nút PREDICT sẽ nổi trên màn hình", 
            font_size='14sp', 
            size_hint=(1, 0.2)
        )
        self.add_widget(hdsd)

    def start_service(self, instance):
        try:
            # Tên class Service được sinh ra dựa trên package.domain và package.name trong buildozer.spec
            # Cấu trúc: [package.domain].[package.name].Service[ServiceName]
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Khởi chạy Service chạy ngầm
            service.start(mActivity, '')
            print("Đã gửi lệnh bật Service!")
        except Exception as e:
            print("Lỗi bật service:", e)

    def stop_service(self, instance):
        try:
            service = autoclass('org.poolpredictor.poolpredictor.ServicePoolPredictor')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Tắt Service
            service.stop(mActivity)
            print("Đã gửi lệnh tắt Service!")
        except Exception as e:
            print("Lỗi tắt service:", e)

class PoolPredictorApp(App):
    def build(self):
        return PoolPredictorUI()

if __name__ == '__main__':
    PoolPredictorApp().run()
