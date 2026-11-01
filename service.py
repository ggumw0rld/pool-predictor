# service.py
from jnius import PythonJavaClass, java_method, autoclass
from kivy.logger import Logger

# Import các thư viện Java của Android
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
WindowManager = autoclass('android.view.WindowManager')
WindowManagerLayoutParams = autoclass('android.view.WindowManager$LayoutParams')
Gravity = autoclass('android.view.Gravity')
PixelFormat = autoclass('android.graphics.PixelFormat')
Button = autoclass('android.widget.Button')
Color = autoclass('android.graphics.Color')
Toast = autoclass('android.widget.Toast')
MotionEvent = autoclass('android.view.MotionEvent')
Looper = autoclass('android.os.Looper')
Handler = autoclass('android.os.Handler')
Build = autoclass('android.os.Build$VERSION')

mService = PythonService.mService
context = mService.getApplicationContext()

# Tạo Handler để đẩy code lên Main Thread (Luồng giao diện)
main_handler = Handler(Looper.getMainLooper())

# ==========================================
# CLASS RUNNABLE: Ép code chạy trên Main Thread
# ==========================================
class PyRunnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __javacontext__ = 'app'
    
    def __init__(self, func):
        super().__init__()
        self.func = func
        
    @java_method('()V')
    def run(self):
        try:
            self.func()
        except Exception as e:
            Logger.error(f"Runnable Error: {e}")
            # Nếu có lỗi, hiện Toast báo lỗi
            Toast.makeText(context, f"Lỗi: {str(e)}", Toast.LENGTH_LONG).show()

# ==========================================
# SỰ KIỆN BẤM VÀ KÉO THẢ
# ==========================================
class OnClickListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnClickListener']
    __javacontext__ = 'app'

    @java_method('(Landroid/view/View;)V')
    def onClick(self, view):
        Toast.makeText(context, "Đang phân tích...", Toast.LENGTH_SHORT).show()

class OnTouchListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnTouchListener']
    __javacontext__ = 'app'

    def __init__(self, params, window_manager):
        super().__init__()
        self.params = params
        self.window_manager = window_manager
        self.initialX = 0
        self.initialY = 0
        self.initialTouchX = 0
        self.initialTouchY = 0

    @java_method('(Landroid/view/View;Landroid/view/MotionEvent;)Z')
    def onTouch(self, view, event):
        action = event.getAction()
        if action == MotionEvent.ACTION_DOWN:
            self.initialX = self.params.x
            self.initialY = self.params.y
            self.initialTouchX = event.getRawX()
            self.initialTouchY = event.getRawY()
            return False 
        elif action == MotionEvent.ACTION_MOVE:
            dx = event.getRawX() - self.initialTouchX
            dy = event.getRawY() - self.initialTouchY
            if abs(dx) > 10 or abs(dy) > 10:
                self.params.x = int(self.initialX + dx)
                self.params.y = int(self.initialY + dy)
                self.window_manager.updateViewLayout(view, self.params)
            return True
        return False

# ==========================================
# HÀM TẠO NÚT (Sẽ được gọi trên Main Thread)
# ==========================================
def create_button():
    try:
        window_manager = context.getSystemService(Context.WINDOW_SERVICE)
        button = Button(context)
        button.setText("PREDICT")
        button.setTextColor(Color.WHITE)
        button.setBackgroundColor(Color.RED)

        # Xử lý loại Overlay tùy theo phiên bản Android
        if Build.SDK_INT >= 26: # Android 8.0 trở lên
            type_overlay = WindowManagerLayoutParams.TYPE_APPLICATION_OVERLAY
        else:
            type_overlay = WindowManagerLayoutParams.TYPE_PHONE

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

        button.setOnClickListener(OnClickListener())
        button.setOnTouchListener(OnTouchListener(params, window_manager))

        window_manager.addView(button, params)
        Toast.makeText(context, "Đã hiện Nút PREDICT!", Toast.LENGTH_SHORT).show()
        
    except Exception as e:
        # Hiện lỗi lên màn hình nếu bị chặn quyền
        Toast.makeText(context, f"Lỗi tạo nút: {str(e)}", Toast.LENGTH_LONG).show()

# Đẩy hàm tạo nút vào Main Thread để thực thi
main_handler.post(PyRunnable(create_button))
