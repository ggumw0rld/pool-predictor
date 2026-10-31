import numpy as np
import subprocess
import os
from PIL import Image, ImageDraw
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.clock import Clock

SCREENSHOT_PATH = "/sdcard/pool_shot.png"

class OverlayLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img_widget = KivyImage(size_hint=(1, 0.85), pos_hint={"top": 1})
        self.add_widget(self.img_widget)
        self.label = Label(text="Chup screenshot -> /sdcard/pool_shot.png -> PREDICT",
            size_hint=(1, 0.08), pos_hint={"y": 0.08},
            color=(1, 1, 0, 1), font_size="14sp")
        self.add_widget(self.label)
        btn = Button(text="PREDICT", size_hint=(1, 0.08),
            pos_hint={"y": 0}, background_color=(0.1, 0.6, 1, 1))
        btn.bind(on_press=self.run_predict)
        self.add_widget(btn)

    def run_predict(self, *args):
        self.label.text = "Dang xu ly..."
        Clock.schedule_once(self._do_predict, 0.1)

    def _do_predict(self, dt):
        try:
            img = Image.open(SCREENSHOT_PATH).convert("RGB")
        except:
            self.label.text = "Luu screenshot vao /sdcard/pool_shot.png truoc!"
            return
        arr = np.array(img)
        bounds = self.detect_table(arr)
        if not bounds:
            self.label.text = "Khong tim thay ban billiard"
            return
        balls = self.detect_balls(arr, bounds)
        cue = self.find_cue(balls)
        if not cue or len(balls) < 2:
            self.label.text = f"Chi thay {len(balls)} bong"
            return
        others = [b for b in balls if b != cue]
        target = min(others, key=lambda b: np.hypot(b[0]-cue[0], b[1]-cue[1]))
        angle = np.arctan2(target[1]-cue[1], target[0]-cue[0])
        power = min(np.hypot(target[0]-cue[0], target[1]-cue[1]) / 8, 100)
        path = self.predict_path(cue[0], cue[1], angle, bounds)
        out_img = self.draw_result(img, cue, target, path, angle, power)
        self.show_image(out_img)
        self.label.text = f"Angle: {np.degrees(angle):.1f}  Power: {power:.0f}  Balls: {len(balls)}"

    def detect_table(self, arr):
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        mask = (b > 120) & (g > 120) & (r < 120) & (b > r) & (g > r)
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not rows.any(): return None
        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]
        return (int(x1), int(y1), int(x2), int(y2))

    def detect_balls(self, arr, bounds):
        x1, y1, x2, y2 = bounds
        region = arr[y1:y2, x1:x2]
        h, w = region.shape[:2]
        balls = []
        for cy in range(0, h, 12):
            for cx in range(0, w, 12):
                r_s = min(12, h-cy-1, w-cx-1)
                if r_s < 4: continue
                patch = region[cy:cy+r_s*2, cx:cx+r_s*2]
                if patch.size == 0: continue
                flat = patch.reshape(-1, 3).astype(float)
                diff = np.abs(flat - flat[len(flat)//2]).mean()
                if diff < 60:
                    rx, ry = x1+cx+r_s, y1+cy+r_s
                    balls.append((rx, ry, r_s, tuple(arr[ry, rx].tolist())))
        unique = []
        for b in balls:
            if not any(np.hypot(b[0]-u[0], b[1]-u[1]) < 20 for u in unique):
                unique.append(b)
        return unique

    def find_cue(self, balls):
        for b in balls:
            r, g, bl = b[3]
            if r > 200 and g > 200 and bl > 200: return b
        return max(balls, key=lambda b: sum(b[3])) if balls else None

    def predict_path(self, sx, sy, angle, bounds, step=5, max_b=3):
        x1, y1, x2, y2 = bounds
        path = [(sx, sy)]
        dx, dy = np.cos(angle)*step, np.sin(angle)*step
        cx, cy, bounces = float(sx), float(sy), 0
        for _ in range(600):
            nx, ny = cx+dx, cy+dy
            if nx < x1 or nx > x2: dx=-dx; nx=cx+dx; bounces+=1
            if ny < y1 or ny > y2: dy=-dy; ny=cy+dy; bounces+=1
            cx, cy = nx, ny
            path.append((int(cx), int(cy)))
            if bounces >= max_b: break
        return path

    def draw_result(self, img, cue, target, path, angle, power):
        out = img.copy()
        draw = ImageDraw.Draw(out)
        for i in range(len(path)-1):
            draw.line([path[i], path[i+1]], fill=(0,255,255), width=2)
        cx, cy, cr = cue[0], cue[1], cue[2]
        draw.ellipse([cx-cr-4, cy-cr-4, cx+cr+4, cy+cr+4], outline=(255,255,255), width=3)
        tx, ty, tr = target[0], target[1], target[2]
        draw.ellipse([tx-tr-4, ty-tr-4, tx+tr+4, ty+tr+4], outline=(0,128,255), width=3)
        draw.line([(cx,cy),(tx,ty)], fill=(255,80,80), width=1)
        return out

    def show_image(self, img):
        arr = np.flipud(np.array(img))
        buf = arr.tobytes()
        tex = Texture.create(size=(arr.shape[1], arr.shape[0]), colorfmt='rgb')
        tex.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.img_widget.texture = tex

class PoolApp(App):
    def build(self):
        return OverlayLayout()

if __name__ == "__main__":
    PoolApp().run()
