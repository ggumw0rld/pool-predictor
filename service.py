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

# Lấy context của service đang chạy
mService = PythonService.mService
context = mService.getApplicationContext()

# ==========================================
# HÀM XỬ LÝ KHI BẤM NÚT (GẮN AI VÀO ĐÂY)
# ==========================================
class OnClickListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnClickListener']
    __javacontext__ = 'app'

    @java_method('(Landroid/view/View;)V')
    def onClick(self, view):
        # Hiển thị thông báo trên màn hình game
        Toast.makeText(context, "Đang phân tích bàn bida...", Toast.LENGTH_SHORT).show()
        Logger.info("Service: Đã bấm nút Predict!")
        
        # TODO: VIẾT CODE CHỤP MÀN HÌNH VÀ GỌI AI CỦA BẠN Ở ĐÂY
        # Ví dụ: 
        # 1. Chụp màn hình game
        # 2. Đưa ảnh qua model AI của bạn
        # 3. Hiển thị kết quả bằng Toast.makeText(...)

# ==========================================
# HÀM XỬ LÝ KÉO THẢ NÚT
# ==========================================
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
            # Lưu lại tọa độ lúc bắt đầu chạm
            self.initialX = self.params.x
            self.initialY = self.params.y
            self.initialTouchX = event.getRawX()
            self.initialTouchY = event.getRawY()
            return False # Trả về False để sự kiện Click (bấm) vẫn hoạt động
            
        elif action == MotionEvent.ACTION_MOVE:
            # Tính toán khoảng cách di chuyển ngón tay
            dx = event.getRawX() - self.initialTouchX
            dy = event.getRawY() - self.initialTouchY
            
            # Nếu di chuyển quá 10 pixel thì mới coi là kéo thả (tránh bị nhầm với click)
            if abs(dx) > 10 or abs(dy) > 10:
                self.params.x = int(self.initialX + dx)
                self.params.y = int(self.initialY + dy)
                self.window_manager.updateViewLayout(view, self.params)
            return True
            
        return False

# ==========================================
# TIẾN HÀNH VẼ NÚT LÊN MÀN HÌNH
# ==========================================
try:
    # Khởi tạo WindowManager để quản lý cửa sổ nổi
    window_manager = mService.getSystemService(Context.WINDOW_SERVICE)
    
    # Tạo nút bấm Native của Android
    button = Button(context)
    button.setText("PREDICT")
    button.setTextColor(Color.WHITE)
    button.setBackgroundColor(Color.RED)

    # Cấu hình thông số cửa sổ nổi
    params = WindowManagerLayoutParams(
        WindowManagerLayoutParams.WRAP_CONTENT,
        WindowManagerLayoutParams.WRAP_CONTENT,
        WindowManagerLayoutParams.TYPE_APPLICATION_OVERLAY, # Quyền hiển thị đè lên app khác (Android 8+)
        WindowManagerLayoutParams.FLAG_NOT_FOCUSABLE,       # Không cướp bàn phím/cảm ứng của game
        PixelFormat.TRANSLUCENT
    )
    params.gravity = Gravity.TOP | Gravity.START
    params.x = 100 # Vị trí ban đầu X
    params.y = 300 # Vị trí ban đầu Y

    # Gắn sự kiện Bấm và Kéo thả vào nút
    button.setOnClickListener(OnClickListener())
    button.setOnTouchListener(OnTouchListener(params, window_manager))

    # Thêm nút vào màn hình
    window_manager.addView(button, params)
    Logger.info("Service: Nút nổi PREDICT đã xuất hiện thành công!")
except Exception as e:
    Logger.error(f"Service: Lỗi tạo nút nổi (Có thể do chưa cấp quyền) - {e}")
