import cv2
import pytesseract
import threading
import time

class FrameThread(threading.Thread):
    def __init__(self, cap, frame_container, frame_lock, running):
        threading.Thread.__init__(self)
        self.cap = cap
        self.frame_container = frame_container
        self.frame_lock = frame_lock
        self.running = running

    def run(self):
        while self.running.is_set():
            ret, frame = self.cap.read()

            # フレームを保存
            with self.frame_lock:
                self.frame_container[0] = frame

            # カメラ映像の表示
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running.clear()
                break

            time.sleep(1/30)  # fps制御

class OCRThread(threading.Thread):
    def __init__(self, frame_container, frame_lock, running):
        threading.Thread.__init__(self)
        self.frame_container = frame_container
        self.frame_lock = frame_lock
        self.running = running

    def run(self):
        while self.running.is_set():
            frame = None

            # 最新のフレームを取得
            with self.frame_lock:
                frame = self.frame_container[0]

            if frame is not None:
                text = pytesseract.image_to_string(frame, lang='jpn')
                print(text)

            time.sleep(1/30)  # fps制御

cap = cv2.VideoCapture(0)

# フレームを保存するコンテナ（1要素のリスト）とロック
frame_container = [None]
frame_lock = threading.Lock()

# スレッドが動作中であることを示すフラグ
running = threading.Event()
running.set()

frame_thread = FrameThread(cap, frame_container, frame_lock, running)
ocr_thread = OCRThread(frame_container, frame_lock, running)
frame_thread.start()
ocr_thread.start()

frame_thread.join()
ocr_thread.join()

cap.release()
cv2.destroyAllWindows()
