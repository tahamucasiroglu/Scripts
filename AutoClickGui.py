"""
GELİŞMİŞ OTOMATİK TIKLAYICI
Versiyon: 3.0
"""

import pyautogui
import mouse
import keyboard
import time
import json
from tkinter import (
    Tk, Label, Button, StringVar, Entry, OptionMenu,
    Listbox, messagebox, END, Toplevel, Frame, filedialog
)

# ---------------------------- AYARLAR ----------------------------
JUMP = "JUMP"
SMOOTH = "SMOOTH"
CONFIG_FILE = "autoclicker_config.acfg"

# ---------------------------- TIKLAMA AYAR SINIFI ----------------------------
class ClickAction:
    def __init__(self, x, y, mode, click_delay=100, click_count=1,
                 move_duration=0, wait_before=0, drag_duration=0, drag_to=None):
        self.x = x
        self.y = y
        self.mode = mode
        self.click_delay = click_delay
        self.click_count = click_count
        self.move_duration = move_duration
        self.wait_before = wait_before
        self.drag_duration = drag_duration
        self.drag_to = drag_to

    def to_json(self):
        return json.dumps({
            "x": self.x,
            "y": self.y,
            "mode": self.mode,
            "click_delay": self.click_delay,
            "click_count": self.click_count,
            "move_duration": self.move_duration,
            "wait_before": self.wait_before,
            "drag_duration": self.drag_duration,
            "drag_to": self.drag_to
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(
            x=data["x"],
            y=data["y"],
            mode=data["mode"],
            click_delay=data.get("click_delay", 100),
            click_count=data.get("click_count", 1),
            move_duration=data.get("move_duration", 0),
            wait_before=data.get("wait_before", 0),
            drag_duration=data.get("drag_duration", 0),
            drag_to=data.get("drag_to", None)
        )

    def execute(self):
        try:
            if self.wait_before > 0:
                time.sleep(self.wait_before / 1000)

            self.move_mouse()
            self.perform_action()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def move_mouse(self):
        duration = 0 if self.mode == JUMP else self.move_duration
        pyautogui.moveTo(self.x, self.y, duration=duration)

    def perform_action(self):
        if self.drag_to:
            self.drag_action()
        else:
            self.click_action()

    def drag_action(self):
        pyautogui.dragTo(
            self.drag_to[0],
            self.drag_to[1],
            duration=self.drag_duration,
            button='left'
        )

    def click_action(self):
        pyautogui.click(
            clicks=self.click_count,
            interval=self.click_delay/1000,
            button='left'
        )

# ---------------------------- ANA UYGULAMA ----------------------------
class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.root.title("AutoClicker Pro 3.0")
        self.root.geometry("800x600")

        # Liste Kutusu
        self.action_list = Listbox(self.root, bg="#F0F0F0", selectmode="single")
        self.action_list.pack(pady=10, padx=20, fill="both", expand=True)

        # Kontrol Paneli
        control_frame = Frame(self.root)
        control_frame.pack(pady=10)

        buttons = [
            ("Ekle", self.add_action, "left"),
            ("Sil", self.delete_action, "left"),
            ("Yükle", self.load_config_dialog, "left"),
            ("Kaydet", self.save_config, "left"),
            ("Başlat", self.start_sequence, "right", "green", "white"),
            ("Çıkış", self.exit_app, "right", "red", "white")
        ]

        for btn in buttons:
            Button(control_frame, text=btn[0], command=btn[1],
                   bg=btn[3] if len(btn)>3 else None,
                   fg=btn[4] if len(btn)>4 else None).pack(side=btn[2], padx=5)

    # ---------------------------- DOSYA İŞLEMLERİ ----------------------------
    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                self.action_list.delete(0, END)
                for line in f:
                    self.action_list.insert(END, line.strip())
        except FileNotFoundError:
            pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                for i in range(self.action_list.size()):
                    f.write(self.action_list.get(i) + "\n")
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def load_config_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("AutoClicker Config", "*.acfg")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.action_list.delete(0, END)
                    for line in f:
                        self.action_list.insert(END, line.strip())
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    # ---------------------------- İŞLEMLER ----------------------------
    def add_action(self):
        try:
            # Koordinat Seçimi
            messagebox.showinfo("Bilgi", "Koordinat seçmek için tıklayın veya SPACE'e basın")
            x, y = self.get_coordinates()

            # Ayarları Al
            settings = self.get_action_settings(x, y)
            if settings:
                self.action_list.insert(END, settings.to_json())
                messagebox.showinfo("Başarılı", "Eylem başarıyla eklendi")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def get_coordinates(self):
        while True:
            time.sleep(0.05)
            if keyboard.is_pressed("space") or mouse.is_pressed():
                return mouse.get_position()

    def get_action_settings(self, x, y):
        mode = self.select_mode()
        move_duration = self.get_input("Hareket Süresi (saniye)", "0", True)
        wait_before = self.get_input("Bekleme Süresi (ms)", "0")
        click_delay = self.get_input("Tıklama Aralığı (ms)", "100")
        click_count = self.get_input("Tıklama Sayısı", "1")

        drag_settings = {}
        if messagebox.askyesno("Sürükleme", "Sürükleme yapılacak mı?"):
            messagebox.showinfo("Bilgi", "Sürükleme bitiş noktasını seçin")
            end_x, end_y = self.get_coordinates()
            drag_duration = self.get_input("Sürükleme Süresi (saniye)", "0.5", True)
            drag_settings = {
                "drag_duration": drag_duration,
                "drag_to": (end_x, end_y)
            }

        return ClickAction(
            x=x,
            y=y,
            mode=mode,
            move_duration=move_duration,
            wait_before=wait_before,
            click_delay=click_delay,
            click_count=click_count,
            **drag_settings
        )

    def select_mode(self):
        mode_var = StringVar(value=JUMP)
        popup = Toplevel(self.root)
        popup.title("Mod Seçimi")
        popup.grab_set()

        Label(popup, text="Hareket Modu:").pack(pady=5)
        OptionMenu(popup, mode_var, JUMP, SMOOTH).pack()
        Button(popup, text="Tamam", command=popup.destroy).pack(pady=5)

        self.root.wait_window(popup)
        return mode_var.get()

    def get_input(self, title, default, is_float=False):
        value = None
        popup = Toplevel(self.root)
        popup.title(title)
        popup.grab_set()

        Label(popup, text=f"{title}:").pack(pady=5)
        entry_var = StringVar(value=default)
        Entry(popup, textvariable=entry_var).pack(pady=5)
        Button(popup, text="Tamam", command=popup.destroy).pack(pady=5)

        self.root.wait_window(popup)
        input_val = entry_var.get()
        
        try:
            return float(input_val) if is_float else int(input_val)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz değer!")
            return self.get_input(title, default, is_float)

    def delete_action(self):
        try:
            self.action_list.delete(self.action_list.curselection()[0])
        except:
            messagebox.showerror("Hata", "Lütfen bir öğe seçin!")

    def start_sequence(self):
        if self.action_list.size() == 0:
            messagebox.showwarning("Uyarı", "Lütfen önce eylem ekleyin!")
            return

        if messagebox.askokcancel("Başlat", "İşlemi başlatmak istiyor musunuz?"):
            try:
                for i in range(self.action_list.size()):
                    if keyboard.is_pressed("s"):
                        messagebox.showinfo("Bilgi", "İşlem durduruldu")
                        break
                    ClickAction.from_json(self.action_list.get(i)).execute()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def exit_app(self):
        if messagebox.askokcancel("Çıkış", "Programı kapatmak istiyor musunuz?"):
            self.root.destroy()

# ---------------------------- UYGULAMAYI BAŞLAT ----------------------------
if __name__ == "__main__":
    root = Tk()
    app = AutoClickerApp(root)
    root.mainloop()