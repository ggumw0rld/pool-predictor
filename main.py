from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Line, Ellipse
from kivy.core.window import Window
from PIL import Image as PILImage, ImageDraw
import math
import os

SCREENSHOT_PATH = "/sdcard/pool_shot.png"

class OverlayLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img_widget = Image(size_hint=(1, 0.85), pos_hint={'x':0,'y':0.15})
        self.add_widget(self.img_widget)
        self.label = Label(text='Press PREDICT', size_hint=(1,0.1), pos_hint={'x':0,'y':0.05}, font_size='16sp')
        self.add_widget(self.label)
        btn = Button(text='PREDICT', size_hint=(0.4,0.08), pos_hint={'x':0.3,'y':0.005}, font_size='18sp')
        btn.bind(on_press=self.run_prediction)
        self.add_widget(btn)

    def detect_table(self, img):
        w, h = img.size
        pixels = img.load()
        min_x, min_y, max_x, max_y = w, h, 0, 0
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                r, g, b = pixels[x, y][:3]
                # teal/green felt detection
                if g > 100 and b > 80 and r < 120 and (g > r) and (b > r * 0.7):
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
        if max_x <= min_x or max_y <= min_y:
            return (50, 50, w-50, h-50)
        return (min_x, min_y, max_x, max_y)

    def detect_balls(self, img, bounds):
        x1, y1, x2, y2 = bounds
        w, h = img.size
        pixels = img.load()
        balls = []
        step = 12
        for y in range(y1, y2, step):
            for x in range(x1, x2, step):
                r, g, b = pixels[x, y][:3]
                # check color variance in small patch
                patch_colors = []
                for dy in range(-8, 9, 4):
                    for dx in range(-8, 9, 4):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < w and 0 <= ny < h:
                            patch_colors.append(pixels[nx, ny][:3])
                if len(patch_colors) < 4:
                    continue
                # calc variance manually
                avg_r = sum(c[0] for c in patch_colors) / len(patch_colors)
                avg_g = sum(c[1] for c in patch_colors) / len(patch_colors)
                avg_b = sum(c[2] for c in patch_colors) / len(patch_colors)
                var = sum((c[0]-avg_r)**2 + (c[1]-avg_g)**2 + (c[2]-avg_b)**2 for c in patch_colors) / len(patch_colors)
                if var < 800:  # uniform color = ball
                    # not felt color
                    if not (g > 100 and b > 80 and r < 120):
                        balls.append((x, y, avg_r, avg_g, avg_b))
        # remove duplicates
        filtered = []
        for ball in balls:
            too_close = False
            for fb in filtered:
                if abs(ball[0]-fb[0]) < 18 and abs(ball[1]-fb[1]) < 18:
                    too_close = True
                    break
            if not too_close:
                filtered.append(ball)
        return filtered

    def find_cue_ball(self, balls):
        if not balls:
            return None
        # find whitest ball
        best = None
        best_score = -1
        for b in balls:
            score = b[2] + b[3] + b[4]  # sum RGB = brightness
            if score > best_score:
                best_score = score
                best = b
        return best

    def predict_path(self, sx, sy, angle, bounds, step=5, max_b=3):
        x1, y1, x2, y2 = bounds
        path = [(sx, sy)]
        dx = math.cos(angle) * step
        dy = math.sin(angle) * step
        cx, cy = float(sx), float(sy)
        bounces = 0
        for _ in range(300):
            cx += dx
            cy += dy
            if cx <= x1 or cx >= x2:
                dx = -dx
                bounces += 1
            if cy <= y1 or cy >= y2:
                dy = -dy
                bounces += 1
            path.append((int(cx), int(cy)))
            if bounces >= max_b:
                break
        return path

    def draw_result(self, img, cue, target, path, angle, power):
        draw = ImageDraw.Draw(img)
        if path:
            draw.line(path, fill=(0, 255, 255), width=3)
        r = 10
        if cue:
            draw.ellipse([cue[0]-r, cue[1]-r, cue[0]+r, cue[1]+r], outline=(255,255,255), width=3)
        if target:
            draw.ellipse([target[0]-r, target[1]-r, target[0]+r, target[1]+r], outline=(0,100,255), width=3)
        return img

    def run_prediction(self, instance):
        if not os.path.exists(SCREENSHOT_PATH):
            self.label.text = f'No file: {SCREENSHOT_PATH}'
            return
        try:
            img = PILImage.open(SCREENSHOT_PATH).convert('RGB')
            bounds = self.detect_table(img)
            balls = self.detect_balls(img, bounds)
            cue = self.find_cue_ball(balls)
            if not cue or len(balls) < 2:
                self.label.text = f'Detected {len(balls)} balls - need 2+'
                return
            # find nearest other ball
            target = None
            min_dist = float('inf')
            for b in balls:
                if b is cue:
                    continue
                d = math.sqrt((b[0]-cue[0])**2 + (b[1]-cue[1])**2)
                if d < min_dist:
                    min_dist = d
                    target = b
            angle = math.atan2(target[1]-cue[1], target[0]-cue[0])
            power = min(100, int(min_dist / 8))
            path = self.predict_path(cue[0], cue[1], angle, bounds)
            result_img = self.draw_result(img.copy(), cue, target, path, angle, power)
            out_path = '/sdcard/pool_result.png'
            result_img.save(out_path)
            self.img_widget.source = out_path
            self.img_widget.reload()
            self.label.text = f'Angle:{math.degrees(angle):.1f}° Power:{power} Balls:{len(balls)}'
        except Exception as e:
            self.label.text = f'Error: {str(e)}'

class PoolApp(App):
    def build(self):
        return OverlayLayout()

if __name__ == '__main__':
    PoolApp().run()
