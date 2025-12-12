"""Otomatik FFmpeg ve GPU kurulum modülü"""
import subprocess
import shutil
import platform
import os
import sys
import urllib.request
import zipfile
import tempfile
from typing import Tuple, Callable, Optional


class Installer:
    """Otomatik kurulum yöneticisi"""

    # FFmpeg indirme URL'leri
    FFMPEG_URLS = {
        "windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        "linux": None,  # Paket yöneticisi ile
        "darwin": None  # Homebrew ile
    }

    @staticmethod
    def get_app_dir() -> str:
        """Uygulama klasörünü al"""
        if getattr(sys, 'frozen', False):
            # PyInstaller ile paketlenmiş
            return os.path.dirname(sys.executable)
        else:
            # Normal Python
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def get_ffmpeg_local_path() -> str:
        """Yerel FFmpeg yolunu al"""
        app_dir = Installer.get_app_dir()
        system = platform.system().lower()

        if system == "windows":
            return os.path.join(app_dir, "ffmpeg", "bin", "ffmpeg.exe")
        else:
            return os.path.join(app_dir, "ffmpeg", "ffmpeg")

    @staticmethod
    def check_ffmpeg() -> Tuple[bool, str]:
        """FFmpeg kurulu mu kontrol et"""
        # Önce sistem PATH'inde ara
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.split('\n')[0] if result.stdout else "Bilinmiyor"
                return True, version
            except:
                pass

        # Yerel kurulumu kontrol et
        local_path = Installer.get_ffmpeg_local_path()
        if os.path.exists(local_path):
            try:
                result = subprocess.run(
                    [local_path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.split('\n')[0] if result.stdout else "Yerel kurulum"
                return True, version
            except:
                pass

        return False, "FFmpeg bulunamadi"

    @staticmethod
    def install_ffmpeg(progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """
        FFmpeg'i otomatik kur

        Args:
            progress_callback: İlerleme bildirimi için callback(message, percent)
        """
        system = platform.system().lower()

        def notify(msg, pct=None):
            if progress_callback:
                progress_callback(msg, pct)

        try:
            if system == "windows":
                return Installer._install_ffmpeg_windows(notify)
            elif system == "linux":
                return Installer._install_ffmpeg_linux(notify)
            elif system == "darwin":
                return Installer._install_ffmpeg_macos(notify)
            else:
                return False, f"Desteklenmeyen sistem: {system}"
        except Exception as e:
            return False, f"Kurulum hatasi: {str(e)}"

    @staticmethod
    def _install_ffmpeg_windows(notify: Callable) -> Tuple[bool, str]:
        """Windows'ta FFmpeg kur - Direkt indirip uygulama klasörüne koy"""
        notify("FFmpeg indiriliyor...", 10)

        app_dir = Installer.get_app_dir()
        ffmpeg_dir = os.path.join(app_dir, "ffmpeg")

        # Eski kurulumu temizle
        if os.path.exists(ffmpeg_dir):
            shutil.rmtree(ffmpeg_dir, ignore_errors=True)

        try:
            # Temp klasöre indir
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")

            notify("FFmpeg indiriliyor (bu biraz zaman alabilir)...", 20)

            # İndirme işlemi
            url = Installer.FFMPEG_URLS["windows"]
            urllib.request.urlretrieve(url, zip_path, reporthook=lambda b, bs, ts: None)

            notify("Arsiv cikartiliyor...", 60)

            # Zip'i çıkart
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Çıkartılan klasörü bul
            extracted_folders = [f for f in os.listdir(temp_dir) if f.startswith("ffmpeg") and os.path.isdir(os.path.join(temp_dir, f))]

            if not extracted_folders:
                return False, "Arsiv icinde ffmpeg klasoru bulunamadi"

            extracted_path = os.path.join(temp_dir, extracted_folders[0])

            notify("Dosyalar kopyalaniyor...", 80)

            # Uygulama klasörüne taşı
            shutil.move(extracted_path, ffmpeg_dir)

            # Temizlik
            shutil.rmtree(temp_dir, ignore_errors=True)

            # PATH'e ekle (bu oturum için)
            bin_path = os.path.join(ffmpeg_dir, "bin")
            if bin_path not in os.environ.get("PATH", ""):
                os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")

            notify("Kurulum tamamlandi!", 100)

            # Doğrula
            ffmpeg_exe = os.path.join(bin_path, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                return True, "FFmpeg basariyla kuruldu!"
            else:
                return False, "Kurulum tamamlandi ancak ffmpeg.exe bulunamadi"

        except urllib.error.URLError as e:
            return False, f"Indirme hatasi: {e}\nInternet baglantinizi kontrol edin."
        except zipfile.BadZipFile:
            return False, "Indirilen dosya bozuk. Tekrar deneyin."
        except PermissionError:
            return False, "Dosya yazma izni yok. Programi yonetici olarak calistirin."
        except Exception as e:
            return False, f"Beklenmeyen hata: {str(e)}"

    @staticmethod
    def _install_ffmpeg_linux(notify: Callable) -> Tuple[bool, str]:
        """Linux'ta FFmpeg kur"""
        notify("Paket yoneticisi tespit ediliyor...", 10)

        # Dağıtımı tespit et
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"').lower()
                        break
        except:
            pass

        # Paket yöneticisine göre komut belirle
        if distro in ["ubuntu", "debian", "linuxmint", "pop"]:
            cmds = [
                (["sudo", "apt", "update"], "Paket listesi guncelleniyor..."),
                (["sudo", "apt", "install", "-y", "ffmpeg"], "FFmpeg kuruluyor...")
            ]
        elif distro in ["fedora", "rhel", "centos"]:
            cmds = [
                (["sudo", "dnf", "install", "-y", "ffmpeg"], "FFmpeg kuruluyor...")
            ]
        elif distro in ["arch", "manjaro"]:
            cmds = [
                (["sudo", "pacman", "-Sy", "--noconfirm", "ffmpeg"], "FFmpeg kuruluyor...")
            ]
        else:
            # Genel deneme
            if shutil.which("apt"):
                cmds = [(["sudo", "apt", "install", "-y", "ffmpeg"], "FFmpeg kuruluyor...")]
            elif shutil.which("dnf"):
                cmds = [(["sudo", "dnf", "install", "-y", "ffmpeg"], "FFmpeg kuruluyor...")]
            elif shutil.which("pacman"):
                cmds = [(["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"], "FFmpeg kuruluyor...")]
            else:
                return False, "Paket yoneticisi bulunamadi"

        # pkexec varsa GUI'de şifre sor
        use_pkexec = shutil.which("pkexec") is not None

        for i, (cmd, msg) in enumerate(cmds):
            notify(msg, 30 + (i * 30))

            if use_pkexec:
                # sudo yerine pkexec kullan
                cmd = ["pkexec"] + cmd[1:]  # sudo'yu çıkar

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0 and "ffmpeg" in cmd:
                    return False, f"Kurulum hatasi:\n{result.stderr}"
            except subprocess.TimeoutExpired:
                return False, "Kurulum zaman asimina ugradi"
            except Exception as e:
                return False, f"Hata: {str(e)}"

        notify("Kurulum tamamlandi!", 100)

        # Doğrula
        if shutil.which("ffmpeg"):
            return True, "FFmpeg basariyla kuruldu!"
        else:
            return False, "Kurulum tamamlandi ancak ffmpeg PATH'de bulunamadi"

    @staticmethod
    def _install_ffmpeg_macos(notify: Callable) -> Tuple[bool, str]:
        """macOS'ta FFmpeg kur"""
        if not shutil.which("brew"):
            notify("Homebrew kuruluyor...", 10)
            try:
                subprocess.run(
                    ['/bin/bash', '-c',
                     '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'],
                    timeout=600
                )
            except:
                return False, "Homebrew kurulamadi"

        notify("FFmpeg kuruluyor...", 50)
        try:
            result = subprocess.run(
                ["brew", "install", "ffmpeg"],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                notify("Kurulum tamamlandi!", 100)
                return True, "FFmpeg basariyla kuruldu!"
            else:
                return False, f"Kurulum hatasi:\n{result.stderr}"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    @staticmethod
    def check_nvidia_gpu() -> Tuple[bool, str]:
        """NVIDIA GPU var mı kontrol et"""
        system = platform.system().lower()

        try:
            if system == "windows":
                # nvidia-smi kontrol
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return True, result.stdout.strip().split('\n')[0]
            else:
                # Linux
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return True, result.stdout.strip().split('\n')[0]
        except FileNotFoundError:
            pass
        except Exception:
            pass

        return False, "NVIDIA GPU bulunamadi veya surucu kurulu degil"

    @staticmethod
    def check_nvenc() -> Tuple[bool, list]:
        """NVENC encoder desteği kontrol et"""
        ffmpeg_path = shutil.which("ffmpeg")

        # Yerel kurulumu da kontrol et
        if not ffmpeg_path:
            local_path = Installer.get_ffmpeg_local_path()
            if os.path.exists(local_path):
                ffmpeg_path = local_path

        if not ffmpeg_path:
            return False, []

        available_encoders = []
        nvenc_encoders = ["h264_nvenc", "hevc_nvenc"]

        try:
            # Encoder listesini al
            result = subprocess.run(
                [ffmpeg_path, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )

            for encoder in nvenc_encoders:
                if encoder in result.stdout:
                    # Test et
                    test = subprocess.run(
                        [ffmpeg_path, "-hide_banner", "-f", "lavfi", "-i",
                         "nullsrc=s=256x256:d=1", "-c:v", encoder,
                         "-f", "null", "-"],
                        capture_output=True,
                        timeout=10
                    )
                    if test.returncode == 0:
                        available_encoders.append(encoder)

            return len(available_encoders) > 0, available_encoders
        except:
            return False, []

    @staticmethod
    def get_ffmpeg_path() -> str:
        """Kullanılacak FFmpeg yolunu al"""
        # Önce sistem PATH'inde ara
        system_path = shutil.which("ffmpeg")
        if system_path:
            return system_path

        # Yerel kurulumu kontrol et
        local_path = Installer.get_ffmpeg_local_path()
        if os.path.exists(local_path):
            # PATH'e ekle (bu oturum için)
            bin_dir = os.path.dirname(local_path)
            if bin_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            return local_path

        return "ffmpeg"  # Varsayılan

    @staticmethod
    def get_ffprobe_path() -> str:
        """Kullanılacak FFprobe yolunu al"""
        # Önce sistem PATH'inde ara
        system_path = shutil.which("ffprobe")
        if system_path:
            return system_path

        # Yerel kurulumu kontrol et
        app_dir = Installer.get_app_dir()
        system = platform.system().lower()

        if system == "windows":
            local_path = os.path.join(app_dir, "ffmpeg", "bin", "ffprobe.exe")
        else:
            local_path = os.path.join(app_dir, "ffmpeg", "ffprobe")

        if os.path.exists(local_path):
            return local_path

        return "ffprobe"  # Varsayılan

    @staticmethod
    def install_nvidia_driver(progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """
        NVIDIA sürücülerini kur

        Args:
            progress_callback: İlerleme bildirimi için callback(message, percent)
        """
        system = platform.system().lower()

        def notify(msg, pct=None):
            if progress_callback:
                progress_callback(msg, pct)

        try:
            if system == "windows":
                return Installer._install_nvidia_windows(notify)
            elif system == "linux":
                return Installer._install_nvidia_linux(notify)
            else:
                return False, "Bu sistemde otomatik NVIDIA kurulumu desteklenmiyor"
        except Exception as e:
            return False, f"Kurulum hatasi: {str(e)}"

    @staticmethod
    def _install_nvidia_windows(notify: Callable) -> Tuple[bool, str]:
        """Windows'ta NVIDIA sürücü kur"""
        notify("NVIDIA sürücü kontrol ediliyor...", 10)

        # winget ile NVIDIA sürücü kur
        if shutil.which("winget"):
            notify("NVIDIA sürücü indiriliyor (winget)...", 30)
            try:
                result = subprocess.run(
                    ["winget", "install", "Nvidia.GeForceExperience", "-e",
                     "--accept-package-agreements", "--accept-source-agreements"],
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                if result.returncode == 0:
                    notify("GeForce Experience kuruldu!", 100)
                    return True, (
                        "GeForce Experience kuruldu!\n\n"
                        "Simdi GeForce Experience'i acin ve\n"
                        "'Drivers' sekmesinden surucu guncellemesi yapin.\n\n"
                        "Sonra bilgisayari yeniden baslatin."
                    )
            except:
                pass

        # Manuel indirme linki
        return False, (
            "Otomatik kurulum yapilamadi.\n\n"
            "NVIDIA surucu indirmek icin:\n"
            "https://www.nvidia.com/Download/index.aspx\n\n"
            "1. Ekran kartinizi secin\n"
            "2. Surucuyu indirin ve kurun\n"
            "3. Bilgisayari yeniden baslatin"
        )

    @staticmethod
    def _install_nvidia_linux(notify: Callable) -> Tuple[bool, str]:
        """Linux'ta NVIDIA sürücü kur"""
        notify("Sistem tespit ediliyor...", 10)

        # Dağıtımı tespit et
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"').lower()
                        break
        except:
            pass

        # pkexec varsa GUI'de şifre sor
        use_pkexec = shutil.which("pkexec") is not None

        def run_cmd(cmd):
            if use_pkexec:
                cmd = ["pkexec"] + cmd[1:]  # sudo'yu çıkar
            return subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        notify("NVIDIA sürücü kuruluyor...", 30)

        try:
            if distro in ["ubuntu", "debian", "linuxmint", "pop"]:
                # Ubuntu/Debian - ubuntu-drivers kullan
                # Önce ubuntu-drivers-common kur
                run_cmd(["sudo", "apt", "update"])
                run_cmd(["sudo", "apt", "install", "-y", "ubuntu-drivers-common"])

                notify("En iyi sürücü tespit ediliyor...", 50)

                # Otomatik en iyi sürücüyü kur
                result = run_cmd(["sudo", "ubuntu-drivers", "autoinstall"])

                if result.returncode == 0:
                    notify("NVIDIA sürücü kuruldu!", 100)
                    return True, (
                        "NVIDIA surucusu kuruldu!\n\n"
                        "Degisikliklerin aktif olmasi icin\n"
                        "bilgisayari yeniden baslatin."
                    )
                else:
                    # Alternatif: nvidia-driver-xxx paketini dene
                    notify("Alternatif yontem deneniyor...", 60)
                    result = run_cmd(["sudo", "apt", "install", "-y", "nvidia-driver-535"])
                    if result.returncode == 0:
                        return True, "NVIDIA surucusu kuruldu! Bilgisayari yeniden baslatin."

            elif distro in ["fedora"]:
                # Fedora - RPM Fusion kullan
                notify("RPM Fusion ekleniyor...", 40)
                run_cmd(["sudo", "dnf", "install", "-y",
                        f"https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm",
                        f"https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm"])

                notify("NVIDIA sürücü kuruluyor...", 60)
                result = run_cmd(["sudo", "dnf", "install", "-y", "akmod-nvidia"])

                if result.returncode == 0:
                    return True, "NVIDIA surucusu kuruldu! Bilgisayari yeniden baslatin."

            elif distro in ["arch", "manjaro"]:
                # Arch - nvidia paketi
                notify("NVIDIA sürücü kuruluyor...", 50)
                result = run_cmd(["sudo", "pacman", "-S", "--noconfirm", "nvidia", "nvidia-utils"])

                if result.returncode == 0:
                    return True, "NVIDIA surucusu kuruldu! Bilgisayari yeniden baslatin."

        except subprocess.TimeoutExpired:
            return False, "Kurulum zaman asimina ugradi"
        except Exception as e:
            return False, f"Hata: {str(e)}"

        return False, (
            "Otomatik kurulum yapilamadi.\n\n"
            "Manuel kurulum:\n"
            f"Dagitim: {distro}\n\n"
            "Ubuntu/Debian:\n"
            "  sudo ubuntu-drivers autoinstall\n\n"
            "Fedora:\n"
            "  sudo dnf install akmod-nvidia\n\n"
            "Arch:\n"
            "  sudo pacman -S nvidia nvidia-utils"
        )
