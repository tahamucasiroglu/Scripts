# -*- coding: utf-8 -*-
"""
Taha Mucasiroglu TIF Donusturucu
================================
TIF/TIFF dosyalarini PNG, JPEG ve PDF bicimlerine donusturen, cift tiklayinca
acilan bagimsiz bir masaustu uygulamasi.

Ozellikler
----------
* Bir veya birden cok .tif/.tiff dosyasi secimi
* Cikti bicimi: PNG / JPEG / PDF
* Bicime ozel kalite ayarlari:
    - PNG : sikistirma seviyesi (0-9, kayipsiz) + optimize
    - JPEG: kalite (1-100) + optimize
    - PDF : icerik modu (otomatik/gri/renkli) + JPEG kalite + tek PDF'te birlestirme
* Ortak: cozunurluk (DPI), cikti klasoru, ayni isim varsa numara ekleme
* Cok sayfali TIF destegi (her sayfa ayri PNG/JPEG; PDF'te cok sayfa korunur)
* Donusturme islemi arka planda calisir, arayuz donmaz

Bu dosya hem masaustu uygulamasi (argumansiz calistirma) hem de dahili dogrulama
(`--selftest`) icin kullanilabilir.

Gereksinim: Pillow  (pip install pillow)
"""

import os
import sys
import threading
import queue
import traceback

from PIL import Image, ImageSequence


# ---------------------------------------------------------------------------
# Yardimci: yol / dosya islemleri
# ---------------------------------------------------------------------------

def uygulama_klasoru():
    """Calistirilan exe'nin (veya .py dosyasinin) bulundugu klasor."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _kaynak_yolu(ad):
    """Pakete gomulu bir kaynak dosyanin (ikon vb.) calisma zamani yolu.

    PyInstaller --onefile modunda veriler gecici bir klasore (_MEIPASS) acilir;
    gelistirme sirasinda ise dosya .py ile ayni klasordedir.
    """
    taban = getattr(sys, "_MEIPASS", None) or uygulama_klasoru()
    return os.path.join(taban, ad)


def benzersiz_yol(yol, numara_ekle):
    """
    `numara_ekle` True ise ve dosya zaten varsa, uzerine yazmamak icin
    sonuna _1, _2 ... ekleyerek bos bir yol dondurur.
    """
    if not numara_ekle or not os.path.exists(yol):
        return yol
    kok, uzanti = os.path.splitext(yol)
    i = 1
    while os.path.exists("{}_{}{}".format(kok, i, uzanti)):
        i += 1
    return "{}_{}{}".format(kok, i, uzanti)


def sayfa_yolu(temel, sayfa_no, uzanti, numara_ekle):
    """
    Bir sayfa icin cikti yolu uretir. `sayfa_no` None ise tek sayfalik dosya
    demektir (ekstra ek yok), aksi halde '_sayfa{n}' eklenir.
    """
    if sayfa_no is None:
        aday = "{}{}".format(temel, uzanti)
    else:
        aday = "{}_sayfa{}{}".format(temel, sayfa_no, uzanti)
    return benzersiz_yol(aday, numara_ekle)


# ---------------------------------------------------------------------------
# Goruntu hazirlama (mod donusumleri)
# ---------------------------------------------------------------------------

def _rgb_duzlestir(im):
    """Saydamligi beyaz zemine yedirerek goruntuyu RGB'ye cevirir."""
    if im.mode == "RGB":
        return im
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        zemin = Image.new("RGB", im.size, (255, 255, 255))
        zemin.paste(rgba, mask=rgba.split()[-1])
        return zemin
    return im.convert("RGB")


def _jpeg_icin_hazirla(im):
    """JPEG, 1-bit/saydam/paletli modlari desteklemez; uygun moda cevirir."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return _rgb_duzlestir(im)
    if im.mode == "1":           # siyah-beyaz tarama -> gri tonlama (temiz)
        return im.convert("L")
    if im.mode in ("L", "RGB"):
        return im
    return im.convert("RGB")


def _pdf_icin_hazirla(im, icerik_modu):
    """
    PDF sayfasi icin goruntuyu hazirlar.
    icerik_modu:
        'auto'  -> 1-bit ise kayipsiz G4 olarak korunur (kucuk, net)
        'gray'  -> gri tonlama (JPEG, kalite ayari etkili)
        'color' -> renkli      (JPEG, kalite ayari etkili)
    """
    if icerik_modu == "gray":
        return im if im.mode == "L" else im.convert("L")
    if icerik_modu == "color":
        return _rgb_duzlestir(im)
    # auto
    if im.mode in ("1", "L", "RGB"):
        return im
    return _rgb_duzlestir(im)


# ---------------------------------------------------------------------------
# TIF okuma
# ---------------------------------------------------------------------------

def tif_sayfalarini_ac(yol):
    """TIF dosyasindaki tum sayfalari bagimsiz (kopyalanmis) PIL goruntuleri olarak dondurur."""
    im = Image.open(yol)
    sayfalar = []
    for kare in ImageSequence.Iterator(im):
        sayfalar.append(kare.copy())
    if not sayfalar:
        raise ValueError("Dosyada okunabilir sayfa bulunamadi.")
    return sayfalar


# ---------------------------------------------------------------------------
# Kaydetme (PNG / JPEG / PDF)
# ---------------------------------------------------------------------------

def png_kaydet(sayfalar, temel, dpi, sikistirma, optimize, numara_ekle):
    """Sayfalari PNG olarak kaydeder (kayipsiz). Cok sayfali ise ayri dosyalar."""
    ciktilar = []
    coklu = len(sayfalar) > 1
    for i, sayfa in enumerate(sayfalar, start=1):
        yol = sayfa_yolu(temel, i if coklu else None, ".png", numara_ekle)
        try:
            sayfa.save(yol, "PNG", compress_level=sikistirma,
                       optimize=optimize, dpi=(dpi, dpi))
        except Exception:
            # Nadir modlar icin guvenli geri donus
            _rgb_duzlestir(sayfa).save(yol, "PNG", compress_level=sikistirma,
                                       optimize=optimize, dpi=(dpi, dpi))
        ciktilar.append(yol)
    return ciktilar


def jpeg_kaydet(sayfalar, temel, dpi, kalite, optimize, numara_ekle):
    """Sayfalari JPEG olarak kaydeder. Cok sayfali ise ayri dosyalar."""
    ciktilar = []
    coklu = len(sayfalar) > 1
    for i, sayfa in enumerate(sayfalar, start=1):
        yol = sayfa_yolu(temel, i if coklu else None, ".jpg", numara_ekle)
        img = _jpeg_icin_hazirla(sayfa)
        img.save(yol, "JPEG", quality=kalite, optimize=optimize,
                 progressive=True, dpi=(dpi, dpi))
        ciktilar.append(yol)
    return ciktilar


def _pdf_yaz(hazir_sayfalar, yol, dpi, kalite):
    """
    Hazirlanmis sayfa listesini tek bir PDF olarak yazar.
    Onemli: Sayfalardan herhangi biri 1-bit (mode '1') ise quality parametresi
    Pillow'un dahili TIFF/G4 kodlayicisina sizip hata verir; bu yuzden bilevel
    sayfa varsa quality HIC gonderilmez (G4 zaten kayipsizdir).
    """
    ilk = hazir_sayfalar[0]
    kalan = hazir_sayfalar[1:]
    kw = dict(format="PDF", save_all=True, resolution=float(dpi))
    if kalan:
        kw["append_images"] = kalan
    if not any(p.mode == "1" for p in hazir_sayfalar):
        kw["quality"] = kalite
    ilk.save(yol, **kw)


def pdf_kaydet_tekli(sayfalar, yol, dpi, kalite, icerik_modu, numara_ekle):
    """Bir TIF'in tum sayfalarini tek (cok sayfali) PDF olarak kaydeder."""
    yol = benzersiz_yol(yol, numara_ekle)
    hazir = [_pdf_icin_hazirla(s, icerik_modu) for s in sayfalar]
    _pdf_yaz(hazir, yol, dpi, kalite)
    return [yol]


# ---------------------------------------------------------------------------
# Toplu donusturme cekirdegi (GUI'den bagimsiz)
# ---------------------------------------------------------------------------

class DonusumAyarlari:
    """Donusturme islemi icin tum kullanici ayarlarini tasiyan basit kap."""

    def __init__(self):
        self.bicim = "pdf"          # 'png' | 'jpeg' | 'pdf'
        self.dpi = 200
        # PNG
        self.png_sikistirma = 6
        self.png_optimize = False
        # JPEG
        self.jpeg_kalite = 90
        self.jpeg_optimize = True
        # PDF
        self.pdf_icerik = "auto"    # 'auto' | 'gray' | 'color'
        self.pdf_kalite = 90
        self.pdf_birlestir = False
        # Cikti
        self.kaynak_klasore = True
        self.cikti_klasoru = ""
        self.numara_ekle = True     # ayni isim varsa numara ekle (uzerine yazma)


def _cikti_temeli(dosya, ayar):
    """Bir kaynak dosya icin (uzantisiz) cikti yol temelini hesaplar."""
    klasor = os.path.dirname(dosya) if ayar.kaynak_klasore else ayar.cikti_klasoru
    govde = os.path.splitext(os.path.basename(dosya))[0]
    return os.path.join(klasor, govde)


def donustur(dosyalar, ayar, bildir=None, iptal=None):
    """
    Verilen dosyalari ayarlara gore donusturur.

    bildir(tur, deger): ilerleme bildirimi geri cagrimi
        tur 'log'      -> deger: metin satiri
        tur 'progress' -> deger: tamamlanan dosya sayisi (int)
    iptal(): True donerse islem nazikce durdurulur.

    Donus: (basari_sayisi, hata_sayisi, uretilen_dosyalar)
    """
    def _log(msg):
        if bildir:
            bildir("log", msg)

    def _ilerle(n):
        if bildir:
            bildir("progress", n)

    uretilen = []
    basari = 0
    hata = 0

    # ---- PDF + birlestirme: tum sayfalari tek PDF'te topla ----
    if ayar.bicim == "pdf" and ayar.pdf_birlestir and len(dosyalar) > 1:
        tum_hazir = []
        for idx, dosya in enumerate(dosyalar, start=1):
            if iptal and iptal():
                _log("Islem kullanici tarafindan durduruldu.")
                break
            try:
                sayfalar = tif_sayfalarini_ac(dosya)
                tum_hazir.extend(_pdf_icin_hazirla(s, ayar.pdf_icerik) for s in sayfalar)
                _log("Okundu: {}  ({} sayfa)".format(os.path.basename(dosya), len(sayfalar)))
                basari += 1
            except Exception as e:
                hata += 1
                _log("HATA ({}): {}".format(os.path.basename(dosya), e))
            _ilerle(idx)
        if tum_hazir:
            klasor = (os.path.dirname(dosyalar[0]) if ayar.kaynak_klasore
                      else ayar.cikti_klasoru)
            hedef = benzersiz_yol(os.path.join(klasor, "birlesik.pdf"), ayar.numara_ekle)
            _pdf_yaz(tum_hazir, hedef, ayar.dpi, ayar.pdf_kalite)
            uretilen.append(hedef)
            _log("PDF olusturuldu (birlesik, {} sayfa): {}".format(len(tum_hazir), hedef))
        return basari, hata, uretilen

    # ---- Her dosya bagimsiz ----
    for idx, dosya in enumerate(dosyalar, start=1):
        if iptal and iptal():
            _log("Islem kullanici tarafindan durduruldu.")
            break
        ad = os.path.basename(dosya)
        try:
            sayfalar = tif_sayfalarini_ac(dosya)
            temel = _cikti_temeli(dosya, ayar)

            if ayar.bicim == "png":
                yeni = png_kaydet(sayfalar, temel, ayar.dpi,
                                  ayar.png_sikistirma, ayar.png_optimize, ayar.numara_ekle)
            elif ayar.bicim == "jpeg":
                yeni = jpeg_kaydet(sayfalar, temel, ayar.dpi,
                                   ayar.jpeg_kalite, ayar.jpeg_optimize, ayar.numara_ekle)
            else:  # pdf
                yeni = pdf_kaydet_tekli(sayfalar, temel + ".pdf", ayar.dpi,
                                        ayar.pdf_kalite, ayar.pdf_icerik, ayar.numara_ekle)

            uretilen.extend(yeni)
            basari += 1
            _log("{}  ({} sayfa)  ->  {} dosya".format(ad, len(sayfalar), len(yeni)))
            for y in yeni:
                _log("    {}  ({:,} B)".format(os.path.basename(y), os.path.getsize(y)))
        except Exception as e:
            hata += 1
            _log("HATA ({}): {}".format(ad, e))
        _ilerle(idx)

    return basari, hata, uretilen


# ---------------------------------------------------------------------------
# Grafik arayuz (tkinter)
# ---------------------------------------------------------------------------

def arayuzu_baslat(test_modu=False):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    # Windows'ta net (keskin) arayuz icin DPI farkindaligi
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # Gorev cubugunun python yerine bizim ikonu gostermesi icin uygulama kimligi
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "TahaMucasiroglu.TifDonusturucu")
    except Exception:
        pass

    class Uygulama:
        def __init__(self, kok):
            self.kok = kok
            self.dosyalar = []
            self.kuyruk = queue.Queue()
            self.calisiyor = False
            self.son_klasor = uygulama_klasoru()

            kok.title("Taha Mücasiroğlu Tif dönüştürücü")
            kok.geometry("780x760")
            kok.minsize(700, 680)

            # Pencere ikonu: baslik cubugu (.ico) + gorev cubugu/program ici (.png)
            self._ikon_ref = None
            try:
                ico = _kaynak_yolu("ikon.ico")
                if os.path.exists(ico):
                    kok.iconbitmap(ico)
            except Exception as e:
                sys.stderr.write("iconbitmap: {}\n".format(e))
            try:
                logo = _kaynak_yolu("ikon_logo.png")
                if os.path.exists(logo):
                    self._ikon_ref = tk.PhotoImage(file=logo)
                    kok.iconphoto(True, self._ikon_ref)
            except Exception as e:
                sys.stderr.write("iconphoto: {}\n".format(e))

            try:
                ttk.Style().theme_use("vista")
            except Exception:
                pass

            self._arayuzu_kur()
            self._bicim_degisti()
            self.kok.after(100, self._kuyrugu_isle)

        # ---- arayuz kurulumu ----
        def _arayuzu_kur(self):
            dis = ttk.Frame(self.kok, padding=12)
            dis.pack(fill="both", expand=True)

            ust = ttk.Frame(dis)
            ust.pack(fill="x", pady=(0, 8))
            if self._ikon_ref is not None:
                ttk.Label(ust, image=self._ikon_ref).pack(side="left", padx=(0, 12))
            yazi = ttk.Frame(ust)
            yazi.pack(side="left", anchor="w")
            ttk.Label(yazi, text="Taha Mücasiroğlu Tif dönüştürücü",
                      font=("Segoe UI", 16, "bold")).pack(anchor="w")
            ttk.Label(yazi, text="TIF/TIFF dosyalarını PNG, JPEG veya PDF'e çevirin.",
                      foreground="#555").pack(anchor="w")

            # 1) Dosyalar
            f1 = ttk.LabelFrame(dis, text="1) Dosyalar", padding=8)
            f1.pack(fill="both", expand=True)

            dugmeler = ttk.Frame(f1)
            dugmeler.pack(fill="x", pady=(0, 6))
            ttk.Button(dugmeler, text="Dosya Ekle...",
                       command=self._dosya_ekle).pack(side="left")
            ttk.Button(dugmeler, text="Secileni Kaldir",
                       command=self._secileni_kaldir).pack(side="left", padx=6)
            ttk.Button(dugmeler, text="Listeyi Temizle",
                       command=self._listeyi_temizle).pack(side="left")
            self.sayac_etiket = ttk.Label(dugmeler, text="0 dosya", foreground="#555")
            self.sayac_etiket.pack(side="right")

            liste_cer = ttk.Frame(f1)
            liste_cer.pack(fill="both", expand=True)
            kaydir = ttk.Scrollbar(liste_cer, orient="vertical")
            self.liste = tk.Listbox(liste_cer, selectmode="extended", height=7,
                                    yscrollcommand=kaydir.set, activestyle="none")
            kaydir.config(command=self.liste.yview)
            self.liste.pack(side="left", fill="both", expand=True)
            kaydir.pack(side="right", fill="y")

            # 2) Cikti bicimi
            f2 = ttk.LabelFrame(dis, text="2) Cikti Bicimi", padding=8)
            f2.pack(fill="x", pady=(8, 0))
            self.bicim_var = tk.StringVar(value="pdf")
            for metin, deger in (("PDF", "pdf"), ("PNG", "png"), ("JPEG", "jpeg")):
                ttk.Radiobutton(f2, text=metin, value=deger, variable=self.bicim_var,
                                command=self._bicim_degisti).pack(side="left", padx=(0, 18))

            # 3) Ayarlar
            f3 = ttk.LabelFrame(dis, text="3) Ayarlar", padding=8)
            f3.pack(fill="x", pady=(8, 0))

            # Ortak: DPI
            ortak = ttk.Frame(f3)
            ortak.pack(fill="x", pady=(0, 6))
            ttk.Label(ortak, text="Cozunurluk (DPI):").pack(side="left")
            self.dpi_var = tk.IntVar(value=200)
            ttk.Spinbox(ortak, from_=50, to=1200, increment=50, width=7,
                        textvariable=self.dpi_var).pack(side="left", padx=(6, 0))
            ttk.Label(ortak, text="PDF'te fiziksel sayfa boyutunu; PNG/JPEG'de "
                      "yalnizca etiketi belirler.", foreground="#777").pack(side="left", padx=10)

            # Bicime ozel paneller (ust uste, secime gore gosterilir)
            self.panel_kap = ttk.Frame(f3)
            self.panel_kap.pack(fill="x")

            self._png_panelini_kur()
            self._jpeg_panelini_kur()
            self._pdf_panelini_kur()

            # 4) Cikti yeri
            f4 = ttk.LabelFrame(dis, text="4) Cikti", padding=8)
            f4.pack(fill="x", pady=(8, 0))
            self.kaynak_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(f4, text="Ciktiyi kaynak dosyanin klasorune kaydet",
                            variable=self.kaynak_var,
                            command=self._klasor_durumu).pack(anchor="w")
            satir = ttk.Frame(f4)
            satir.pack(fill="x", pady=(4, 0))
            self.klasor_var = tk.StringVar(value="")
            self.klasor_giris = ttk.Entry(satir, textvariable=self.klasor_var)
            self.klasor_giris.pack(side="left", fill="x", expand=True)
            self.gozat_dugme = ttk.Button(satir, text="Gozat...",
                                          command=self._klasor_sec)
            self.gozat_dugme.pack(side="left", padx=(6, 0))
            self.numara_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(f4, text="Ayni isimde dosya varsa numara ekle (uzerine yazma)",
                            variable=self.numara_var).pack(anchor="w", pady=(4, 0))

            # 5) Calistir + ilerleme + gunluk
            alt = ttk.Frame(dis)
            alt.pack(fill="x", pady=(10, 0))
            self.donustur_dugme = ttk.Button(alt, text="DONUSTUR",
                                             command=self._donustur_basla)
            self.donustur_dugme.pack(side="left")
            self.ac_dugme = ttk.Button(alt, text="Cikti Klasorunu Ac",
                                       command=self._cikti_klasorunu_ac, state="disabled")
            self.ac_dugme.pack(side="left", padx=6)
            self.durum_var = tk.StringVar(value="Hazir.")
            ttk.Label(alt, textvariable=self.durum_var,
                      foreground="#555").pack(side="right")

            self.ilerleme = ttk.Progressbar(dis, mode="determinate")
            self.ilerleme.pack(fill="x", pady=(6, 0))

            g = ttk.LabelFrame(dis, text="Gunluk", padding=4)
            g.pack(fill="both", expand=True, pady=(8, 0))
            gk = ttk.Scrollbar(g, orient="vertical")
            self.gunluk = tk.Text(g, height=8, wrap="word", yscrollcommand=gk.set,
                                  state="disabled", font=("Consolas", 9))
            gk.config(command=self.gunluk.yview)
            self.gunluk.pack(side="left", fill="both", expand=True)
            gk.pack(side="right", fill="y")

            self._klasor_durumu()

        def _png_panelini_kur(self):
            p = ttk.Frame(self.panel_kap)
            self.png_panel = p
            ttk.Label(p, text="PNG kayipsizdir; goruntu kalitesi her zaman tamdir. "
                      "Sikistirma yalnizca dosya boyutunu/hizini etkiler.",
                      foreground="#777").grid(row=0, column=0, columnspan=3,
                                              sticky="w", pady=(0, 6))
            ttk.Label(p, text="Sikistirma (0-9):").grid(row=1, column=0, sticky="w")
            self.png_sik_var = tk.IntVar(value=6)
            self.png_sik_etk = ttk.Label(p, text="6", width=3)
            tk.Scale(p, from_=0, to=9, orient="horizontal", showvalue=False,
                     variable=self.png_sik_var, length=240,
                     command=lambda v: self.png_sik_etk.config(
                         text=str(self.png_sik_var.get()))).grid(row=1, column=1, padx=6)
            self.png_sik_etk.grid(row=1, column=2, sticky="w")
            self.png_opt_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(p, text="Optimize et (en kucuk boyut; sikistirma seviyesini yok sayar)",
                            variable=self.png_opt_var).grid(row=2, column=0, columnspan=3,
                                                            sticky="w", pady=(4, 0))

        def _jpeg_panelini_kur(self):
            p = ttk.Frame(self.panel_kap)
            self.jpeg_panel = p
            ttk.Label(p, text="JPEG kayiplidir. Yuksek kalite = daha buyuk dosya. "
                      "Siyah-beyaz TIF gri tonlamaya cevrilir.",
                      foreground="#777").grid(row=0, column=0, columnspan=3,
                                              sticky="w", pady=(0, 6))
            ttk.Label(p, text="Kalite (1-100):").grid(row=1, column=0, sticky="w")
            self.jpeg_kal_var = tk.IntVar(value=90)
            self.jpeg_kal_etk = ttk.Label(p, text="90", width=3)
            tk.Scale(p, from_=1, to=100, orient="horizontal", showvalue=False,
                     variable=self.jpeg_kal_var, length=240,
                     command=lambda v: self.jpeg_kal_etk.config(
                         text=str(self.jpeg_kal_var.get()))).grid(row=1, column=1, padx=6)
            self.jpeg_kal_etk.grid(row=1, column=2, sticky="w")
            self.jpeg_opt_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(p, text="Optimize et (onerilir)",
                            variable=self.jpeg_opt_var).grid(row=2, column=0, columnspan=3,
                                                             sticky="w", pady=(4, 0))

        def _pdf_panelini_kur(self):
            p = ttk.Frame(self.panel_kap)
            self.pdf_panel = p
            ttk.Label(p, text="Icerik modu:").grid(row=0, column=0, sticky="w")
            self.pdf_icerik_var = tk.StringVar(value="auto")
            secenekler = [
                ("Otomatik (orijinali koru; siyah-beyaz = kayipsiz, en kucuk)", "auto"),
                ("Gri tonlama (JPEG, kalite ayari etkili)", "gray"),
                ("Renkli (JPEG, kalite ayari etkili)", "color"),
            ]
            kutu = ttk.Frame(p)
            kutu.grid(row=0, column=1, columnspan=2, sticky="w", padx=6)
            for metin, deger in secenekler:
                ttk.Radiobutton(kutu, text=metin, value=deger,
                                variable=self.pdf_icerik_var).pack(anchor="w")

            ttk.Label(p, text="Kalite (1-100):").grid(row=1, column=0, sticky="w", pady=(6, 0))
            self.pdf_kal_var = tk.IntVar(value=90)
            self.pdf_kal_etk = ttk.Label(p, text="90", width=3)
            tk.Scale(p, from_=1, to=100, orient="horizontal", showvalue=False,
                     variable=self.pdf_kal_var, length=240,
                     command=lambda v: self.pdf_kal_etk.config(
                         text=str(self.pdf_kal_var.get()))).grid(row=1, column=1, padx=6, pady=(6, 0))
            self.pdf_kal_etk.grid(row=1, column=2, sticky="w", pady=(6, 0))
            ttk.Label(p, text="(Kalite yalnizca gri/renkli modda etkilidir.)",
                      foreground="#777").grid(row=2, column=0, columnspan=3, sticky="w")
            self.pdf_birlestir_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(p, text="Tum dosyalari tek PDF'te birlestir",
                            variable=self.pdf_birlestir_var).grid(row=3, column=0, columnspan=3,
                                                                  sticky="w", pady=(4, 0))

        # ---- olay isleyicileri ----
        def _bicim_degisti(self):
            for panel in (self.png_panel, self.jpeg_panel, self.pdf_panel):
                panel.pack_forget()
            {"png": self.png_panel, "jpeg": self.jpeg_panel,
             "pdf": self.pdf_panel}[self.bicim_var.get()].pack(fill="x")

        def _klasor_durumu(self):
            kaynak = self.kaynak_var.get()
            durum = "disabled" if kaynak else "normal"
            self.klasor_giris.config(state=durum)
            self.gozat_dugme.config(state=durum)

        def _dosya_ekle(self):
            yollar = filedialog.askopenfilenames(
                title="TIF dosyalarini secin",
                initialdir=self.son_klasor,
                filetypes=[("TIFF goruntuleri", "*.tif *.tiff"), ("Tum dosyalar", "*.*")])
            eklendi = 0
            for y in yollar:
                if y not in self.dosyalar:
                    self.dosyalar.append(y)
                    self.liste.insert("end", os.path.basename(y))
                    eklendi += 1
            if yollar:
                self.son_klasor = os.path.dirname(yollar[0])
            self._sayaci_guncelle()

        def _secileni_kaldir(self):
            for i in reversed(self.liste.curselection()):
                self.liste.delete(i)
                del self.dosyalar[i]
            self._sayaci_guncelle()

        def _listeyi_temizle(self):
            self.liste.delete(0, "end")
            self.dosyalar.clear()
            self._sayaci_guncelle()

        def _sayaci_guncelle(self):
            self.sayac_etiket.config(text="{} dosya".format(len(self.dosyalar)))

        def _klasor_sec(self):
            klasor = filedialog.askdirectory(title="Cikti klasorunu secin",
                                             initialdir=self.son_klasor)
            if klasor:
                self.klasor_var.set(klasor)

        def _gunluge_yaz(self, metin):
            self.gunluk.config(state="normal")
            self.gunluk.insert("end", metin + "\n")
            self.gunluk.see("end")
            self.gunluk.config(state="disabled")

        # ---- donusturme ----
        def _ayarlari_topla(self):
            a = DonusumAyarlari()
            a.bicim = self.bicim_var.get()
            a.dpi = max(1, int(self.dpi_var.get()))
            a.png_sikistirma = int(self.png_sik_var.get())
            a.png_optimize = bool(self.png_opt_var.get())
            a.jpeg_kalite = int(self.jpeg_kal_var.get())
            a.jpeg_optimize = bool(self.jpeg_opt_var.get())
            a.pdf_icerik = self.pdf_icerik_var.get()
            a.pdf_kalite = int(self.pdf_kal_var.get())
            a.pdf_birlestir = bool(self.pdf_birlestir_var.get())
            a.kaynak_klasore = bool(self.kaynak_var.get())
            a.cikti_klasoru = self.klasor_var.get().strip()
            a.numara_ekle = bool(self.numara_var.get())
            return a

        def _donustur_basla(self):
            if self.calisiyor:
                return
            if not self.dosyalar:
                messagebox.showinfo("TIF Donusturucu", "Once en az bir TIF dosyasi ekleyin.")
                return
            ayar = self._ayarlari_topla()
            if not ayar.kaynak_klasore:
                if not ayar.cikti_klasoru or not os.path.isdir(ayar.cikti_klasoru):
                    messagebox.showwarning("TIF Donusturucu",
                                           "Gecerli bir cikti klasoru secin veya "
                                           "'kaynak klasore kaydet' secenegini isaretleyin.")
                    return

            self.calisiyor = True
            self.donustur_dugme.config(state="disabled")
            self.ac_dugme.config(state="disabled")
            self.ilerleme.config(maximum=len(self.dosyalar), value=0)
            self.durum_var.set("Donusturuluyor...")
            self._son_cikti_klasoru = (None if ayar.kaynak_klasore else ayar.cikti_klasoru)

            kopya = list(self.dosyalar)

            def is_parcacigi():
                def bildir(tur, deger):
                    self.kuyruk.put((tur, deger))
                try:
                    basari, hata, uretilen = donustur(kopya, ayar, bildir=bildir)
                    if uretilen and self._son_cikti_klasoru is None:
                        self._son_cikti_klasoru = os.path.dirname(uretilen[0])
                    self.kuyruk.put(("done", (basari, hata, len(uretilen))))
                except Exception as e:
                    self.kuyruk.put(("log", "BEKLENMEYEN HATA: {}".format(e)))
                    self.kuyruk.put(("log", traceback.format_exc()))
                    self.kuyruk.put(("done", (0, len(kopya), 0)))

            threading.Thread(target=is_parcacigi, daemon=True).start()

        def _kuyrugu_isle(self):
            try:
                while True:
                    tur, deger = self.kuyruk.get_nowait()
                    if tur == "log":
                        self._gunluge_yaz(deger)
                    elif tur == "progress":
                        self.ilerleme.config(value=deger)
                    elif tur == "done":
                        basari, hata, adet = deger
                        self.calisiyor = False
                        self.donustur_dugme.config(state="normal")
                        self.durum_var.set("Bitti: {} basarili, {} hata, {} dosya uretildi."
                                           .format(basari, hata, adet))
                        self._gunluge_yaz("---- Tamamlandi: {} basarili, {} hata, {} cikti ----"
                                          .format(basari, hata, adet))
                        if adet > 0 and self._son_cikti_klasoru:
                            self.ac_dugme.config(state="normal")
            except queue.Empty:
                pass
            self.kok.after(100, self._kuyrugu_isle)

        def _cikti_klasorunu_ac(self):
            klasor = getattr(self, "_son_cikti_klasoru", None)
            if klasor and os.path.isdir(klasor):
                try:
                    os.startfile(klasor)
                except Exception:
                    pass

    kok = tk.Tk()
    Uygulama(kok)
    if test_modu:
        # Dahili dogrulama: pencereyi acip kisa surede kapatir (cikis kodu 0)
        kok.after(800, kok.destroy)
    kok.mainloop()


# ---------------------------------------------------------------------------
# Dahili dogrulama (--selftest): GUI olmadan donusumu test eder
# ---------------------------------------------------------------------------

def _selftest(args):
    import tempfile

    if len(args) >= 1:
        tif = args[0]
    else:
        tif = os.path.join(uygulama_klasoru(), "evrak_7147314872.tif")
    cikti = args[1] if len(args) >= 2 else tempfile.mkdtemp(prefix="tif_selftest_")
    sonuc_dosyasi = os.path.join(cikti, "selftest_result.txt")

    satirlar = []
    basarili = True
    try:
        from PIL import features
        satirlar.append("libtiff (G4) destegi: {}".format(features.check("libtiff")))
        # Gomulu ikon dosyalari (frozen exe'de _MEIPASS'tan gelmeli)
        for _ad in ("ikon.ico", "ikon_logo.png"):
            _y = _kaynak_yolu(_ad)
            satirlar.append("gomulu ikon {:14s}: {}".format(
                _ad, "VAR" if os.path.exists(_y) else "YOK"))
        sayfalar = tif_sayfalarini_ac(tif)
        satirlar.append("Acildi: {}  ({} sayfa, mod={}, boyut={})".format(
            tif, len(sayfalar), sayfalar[0].mode, sayfalar[0].size))
        temel = os.path.join(cikti, os.path.splitext(os.path.basename(tif))[0])

        png = png_kaydet(sayfalar, temel, 200, 6, True, True)
        jpg = jpeg_kaydet(sayfalar, temel, 200, 90, True, True)
        pdf_a = pdf_kaydet_tekli(sayfalar, temel + "_auto.pdf", 200, 90, "auto", True)
        pdf_g = pdf_kaydet_tekli(sayfalar, temel + "_gri.pdf", 200, 50, "gray", True)

        for grup, etiket in ((png, "PNG"), (jpg, "JPEG"),
                             (pdf_a, "PDF/auto"), (pdf_g, "PDF/gri")):
            for y in grup:
                satirlar.append("{:9s} -> {}  ({:,} B)".format(etiket, y, os.path.getsize(y)))

        # PDF baslik dogrulamasi
        for y in pdf_a + pdf_g:
            with open(y, "rb") as f:
                bas = f.read(5)
            if bas != b"%PDF-":
                basarili = False
                satirlar.append("PDF basligi HATALI: {} -> {}".format(y, bas))
    except Exception as e:
        basarili = False
        satirlar.append("HATA: " + repr(e))
        satirlar.append(traceback.format_exc())

    satirlar.append("SELFTEST: " + ("OK" if basarili else "FAIL"))
    metin = "\n".join(satirlar)
    try:
        with open(sonuc_dosyasi, "w", encoding="utf-8") as f:
            f.write(metin)
    except Exception:
        pass
    print(metin)
    print("Sonuc dosyasi:", sonuc_dosyasi)
    return 0 if basarili else 1


# ---------------------------------------------------------------------------
# Giris noktasi
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(_selftest(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "--guitest":
        arayuzu_baslat(test_modu=True)
        sys.exit(0)
    arayuzu_baslat()
