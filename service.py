# service.py
from jnius import PythonJavaClass, java_method, autoclass
from kivy.logger import Logger

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

mService = PythonService.mService
context = mService.getApplicationContext()

# --- BÁO HIỆU SERVICE ĐÃ CHẠY ---
# Nếu bấm nút mà không thấy dòng chữ này hiện lên => Service chưa hề chạy (Lỗi ở main.py hoặc do máy chặn)
Toast.makeText(context, "Service đã khởi động!", Toast.LENGTH_SHORT).show()

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

try:
    window_manager = context.getSystemService(Context.WINDOW_SERVICE)
    button = Button(context)
    button.setText("PREDICT")
    button.setTextColor(Color.WHITE)
    button.setBackgroundColor(Color.RED)

    # Sửa TYPE_APPLICATION_OVERLAY thành TYPE_PHONE nếu máy bạn chạy Android cũ (dưới Android 8)
    type_overlay = WindowManagerLayoutParams.TYPE_APPLICATION_OVERLAY 
    
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
except Exception as e:
    # Nếu có lỗi khi vẽ nút, nó sẽ hiện lên màn hình cho bạn biết
    Toast.makeText(context, f"Lỗi tạo nút: {str(e)}", Toast.LENGTH_LONG).show()
    Logger.error(f"Service Error: {e}")
