# service.py
import os
from jnius import PythonJavaClass, java_method, autoclass
from kivy.logger import Logger
import traceback

PythonService = autoclass('org.kivy.android.PythonService')
mService = PythonService.mService
context = mService.getApplicationContext()

# Đường dẫn file log (nằm trong thư mục bộ nhớ riêng của app)
log_path = os.path.join(context.getFilesDir().getAbsolutePath(), "debug_log.txt")

def write_log(msg):
    try:
        with open(log_path, "a") as f:
            f.write(msg + "\n")
    except:
        pass

# Xóa log cũ mỗi khi bật service để dễ đọc
try:
    if os.path.exists(log_path):
        os.remove(log_path)
except:
    pass

write_log("--- KHỞI ĐỘNG SERVICE ---")

try:
    Context = autoclass('android.content.Context')
    WindowManager = autoclass('android.view.WindowManager')
    WindowManagerLayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    Gravity = autoclass('android.view.Gravity')
    PixelFormat = autoclass('android.graphics.PixelFormat')
    Button = autoclass('android.widget.Button')
    Color = autoclass('android.graphics.Color')
    Build = autoclass('android.os.Build$VERSION')
    
    write_log("1. Import các thư viện Java thành công.")

    def create_overlay():
        try:
            write_log("2. Bắt đầu hàm vẽ nút...")
            window_manager = context.getSystemService(Context.WINDOW_SERVICE)
            
            button = Button(context)
            button.setText("PREDICT")
            button.setTextColor(Color.WHITE)
            button.setBackgroundColor(Color.RED)

            if Build.SDK_INT >= 26:
                type_overlay = WindowManagerLayoutParams.TYPE_APPLICATION_OVERLAY
            else:
                type_overlay = WindowManagerLayoutParams.TYPE_PHONE

            write_log(f"3. Đang cấu hình Layout (Type: {type_overlay})...")
            
            params = WindowManagerLayoutParams(
                WindowManagerLayoutParams.WRAP_CONTENT,
                WindowManagerLayoutParams.WRAP_CONTENT,
                type_overlay,
                WindowManagerLayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
            )
            params.gravity = Gravity.TOP | Gravity.START
            params.x = 100 
            params.y = 300 

            write_log("4. Đang gọi addView...")
            window_manager.addView(button, params)
            write_log("5. THÀNH CÔNG! Nút đã được vẽ.")
            
        except Exception as e:
            write_log(f"LỖI KHI VẼ NÚT: {str(e)}")
            write_log(traceback.format_exc())

    # Gọi vẽ nút
    from android.runnable import run_on_ui_thread
    draw_func = run_on_ui_thread(create_overlay)
    draw_func()

except Exception as e:
    write_log(f"LỖI KHỞI TẠO SERVICE: {str(e)}")
    write_log(traceback.format_exc())
