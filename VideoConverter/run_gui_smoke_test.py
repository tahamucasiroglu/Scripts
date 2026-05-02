import os
from tkinter import messagebox

from gui.main_window import MainWindow


DESKTOP = r"C:\Users\taham\OneDrive\Desktop"
OUT_DIR = os.path.join(DESKTOP, "TMVC_Test_Output")


def patch_messageboxes():
    messagebox.askyesno = lambda *args, **kwargs: True
    messagebox.showinfo = lambda title, msg, *args, **kwargs: print(f"showinfo: {title}: {msg}")
    messagebox.showerror = lambda title, msg, *args, **kwargs: print(f"showerror: {title}: {msg}")


class GuiSmokeTest:
    def __init__(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        patch_messageboxes()
        self.app = MainWindow(nvenc_available=False, nvenc_encoders=[])
        self.steps = [
            self.single_audio_extract,
            self.single_mp3_to_wav_after_previous,
            self.batch_audio_sequential,
        ]
        self.current_step = -1
        self.failures = []
        self._wrap_callbacks()

    def _wrap_callbacks(self):
        original_complete = self.app._on_convert_complete
        original_error = self.app._on_convert_error
        original_batch_complete = self.app._on_batch_complete

        def complete(output_path):
            original_complete(output_path)
            if hasattr(self.app, "progress_dialog") and self.app.progress_dialog.winfo_exists():
                self.app.progress_dialog.destroy()
            print(f"gui_step_complete: {self.steps[self.current_step].__name__} -> {output_path}")
            self.app.root.after(200, self.next_step)

        def error(error_message):
            self.failures.append((self.steps[self.current_step].__name__, error_message))
            original_error(error_message)
            if hasattr(self.app, "progress_dialog") and self.app.progress_dialog.winfo_exists():
                self.app.progress_dialog.destroy()
            print(f"gui_step_error: {self.steps[self.current_step].__name__} -> {error_message}")
            self.app.root.after(200, self.next_step)

        def batch_complete(queue):
            original_batch_complete(queue)
            if hasattr(self.app, "batch_dialog") and self.app.batch_dialog.winfo_exists():
                self.app.batch_dialog.destroy()
            failed = [item for item in queue if item.get("status") != "completed"]
            if failed:
                self.failures.append(("batch_audio_sequential", str(failed)))
            print("gui_step_complete: batch_audio_sequential")
            self.app.root.after(200, self.next_step)

        self.app._on_convert_complete = complete
        self.app._on_convert_error = error
        self.app._on_batch_complete = batch_complete

    def prepare_source(self, source):
        self.app.source_files = [source]
        self.app.source_var.set(source)
        self.app.output_dir_var.set(OUT_DIR)
        self.app._load_video_info(source)

    def single_audio_extract(self):
        self.prepare_source(os.path.join(DESKTOP, "Download.mp4"))
        self.app.preset_var.set("Ses Cikar -> MP3 (192kbps)")
        self.app._on_preset_change()
        self.app._start_convert()

    def single_mp3_to_wav_after_previous(self):
        self.prepare_source(os.path.join(DESKTOP, "Download.mp3"))
        self.app.preset_var.set("Ses Cikar -> WAV (Kayipsiz)")
        self.app._on_preset_change()
        self.app._start_convert()

    def batch_audio_sequential(self):
        sources = [
            os.path.join(DESKTOP, "Download.mp4"),
            os.path.join(DESKTOP, "Download.mp3"),
        ]
        self.app.source_files = sources
        self.app.source_var.set("2 dosya secildi")
        self.app.output_dir_var.set(OUT_DIR)
        self.app._load_video_info(sources[0])
        self.app.preset_var.set("Ses Cikar -> MP3 (192kbps)")
        self.app._on_preset_change()
        self.app.parallel_var.set(1)
        self.app._start_convert()

    def next_step(self):
        self.current_step += 1
        if self.current_step >= len(self.steps):
            if self.failures:
                print(f"gui_smoke_failures: {self.failures}")
            else:
                print("gui_smoke_passed")
            self.app.root.destroy()
            return

        print(f"gui_step_start: {self.steps[self.current_step].__name__}")
        self.steps[self.current_step]()

    def run(self):
        self.app.root.after(200, self.next_step)
        self.app.root.mainloop()


if __name__ == "__main__":
    GuiSmokeTest().run()
