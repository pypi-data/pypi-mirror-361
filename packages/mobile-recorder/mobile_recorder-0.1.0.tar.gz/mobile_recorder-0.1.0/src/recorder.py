import uiautomator2 as u2
from types import FunctionType

class AndroidRecorder:
    """
    A class to record the screen of an Android device and perform UI operations using uiautomator2.
    """
    def __init__(self, on_new_frame: list[FunctionType], device: str = None) -> None:
        self.on_new_frame = on_new_frame
        self.device = device

    def start_recording(self):
        """
        Start recording by taking screenshots as fast as possible and calling callbacks.
        """
        self._recording = True
        import threading

        def record_loop():
            d = u2.connect(self.device)
            while self._recording:
                img = d.screenshot()
                for cb in self.on_new_frame:
                    cb(img)
        self._thread = threading.Thread(target=record_loop, daemon=True)
        self._thread.start()

    def stop_recording(self):
        """
        Stop the recording loop.
        """
        self._recording = False
        if hasattr(self, '_thread'):
            self._thread.join()
    
    def get_frame_actions(self):
        return self.on_new_frame
    
    def set_frame_actions(self):
        return self.on_new_frame
    
if __name__ == "__main__":
    import time
    recorder = AndroidRecorder([])
    recorder.start_recording()
    time.sleep(2)
    recorder.stop_recording()