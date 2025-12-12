"""FFmpeg kontrol ve yardımcı fonksiyonlar"""
import subprocess
import shutil
import json
import re
import platform
import os
import sys
from typing import Optional, Dict, List, Tuple


def _get_app_dir() -> str:
    """Uygulama klasörünü al"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_ffprobe_path() -> str:
    """FFprobe yolunu al"""
    # Önce PATH'de ara
    system_path = shutil.which("ffprobe")
    if system_path:
        return system_path

    # Yerel kurulumu kontrol et
    app_dir = _get_app_dir()
    system = platform.system().lower()

    if system == "windows":
        local_path = os.path.join(app_dir, "ffmpeg", "bin", "ffprobe.exe")
    else:
        local_path = os.path.join(app_dir, "ffmpeg", "ffprobe")

    if os.path.exists(local_path):
        return local_path

    return "ffprobe"


class FFmpegUtils:
    """FFmpeg varlık kontrolü ve bilgi alma"""

    @staticmethod
    def check_ffmpeg() -> Tuple[bool, str]:
        """FFmpeg kurulu mu kontrol et"""
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_line = result.stdout.split('\n')[0]
                return True, version_line
            except Exception as e:
                return False, f"FFmpeg calistirilamadi: {e}"
        return False, "FFmpeg bulunamadi"

    @staticmethod
    def check_ffprobe() -> Tuple[bool, str]:
        """FFprobe kurulu mu kontrol et"""
        ffprobe_path = shutil.which("ffprobe")
        if ffprobe_path:
            return True, ffprobe_path
        return False, "FFprobe bulunamadi"

    @staticmethod
    def check_nvenc() -> Tuple[bool, List[str]]:
        """NVIDIA NVENC desteği kontrol et"""
        available_encoders = []
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout

            nvenc_encoders = ["h264_nvenc", "hevc_nvenc", "av1_nvenc"]
            for encoder in nvenc_encoders:
                if encoder in output:
                    # Gerçekten çalışıyor mu test et
                    test = subprocess.run(
                        ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i",
                         "nullsrc=s=256x256:d=1", "-c:v", encoder,
                         "-f", "null", "-"],
                        capture_output=True,
                        timeout=10
                    )
                    if test.returncode == 0:
                        available_encoders.append(encoder)

            if available_encoders:
                return True, available_encoders
            return False, []
        except Exception:
            return False, []

    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Sistem bilgisini al"""
        system = platform.system().lower()
        info = {
            "system": system,
            "release": platform.release(),
            "machine": platform.machine()
        }

        # Linux dağıtımını tespit et
        if system == "linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            info["distro"] = line.strip().split("=")[1].strip('"')
                        elif line.startswith("ID_LIKE="):
                            info["distro_like"] = line.strip().split("=")[1].strip('"')
            except:
                info["distro"] = "unknown"

        return info

    @staticmethod
    def install_ffmpeg(progress_callback=None) -> Tuple[bool, str]:
        """
        FFmpeg'i otomatik kur

        Returns:
            (success, message)
        """
        system_info = FFmpegUtils.get_system_info()
        system = system_info["system"]

        if progress_callback:
            progress_callback("Sistem tespit ediliyor...")

        try:
            if system == "linux":
                return FFmpegUtils._install_linux(system_info, progress_callback)
            elif system == "windows":
                return FFmpegUtils._install_windows(progress_callback)
            elif system == "darwin":
                return FFmpegUtils._install_macos(progress_callback)
            else:
                return False, f"Desteklenmeyen sistem: {system}"
        except Exception as e:
            return False, f"Kurulum hatasi: {e}"

    @staticmethod
    def _install_linux(system_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """Linux'ta FFmpeg kur"""
        distro = system_info.get("distro", "")
        distro_like = system_info.get("distro_like", "")

        # Paket yöneticisini belirle
        if distro in ["ubuntu", "debian", "linuxmint", "pop"] or "debian" in distro_like or "ubuntu" in distro_like:
            pkg_manager = "apt"
            update_cmd = ["sudo", "apt", "update"]
            install_cmd = ["sudo", "apt", "install", "-y", "ffmpeg"]
        elif distro in ["fedora", "rhel", "centos"] or "fedora" in distro_like:
            pkg_manager = "dnf"
            update_cmd = None
            install_cmd = ["sudo", "dnf", "install", "-y", "ffmpeg"]
        elif distro in ["arch", "manjaro"] or "arch" in distro_like:
            pkg_manager = "pacman"
            update_cmd = ["sudo", "pacman", "-Sy"]
            install_cmd = ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]
        elif distro in ["opensuse", "suse"]:
            pkg_manager = "zypper"
            update_cmd = None
            install_cmd = ["sudo", "zypper", "install", "-y", "ffmpeg"]
        else:
            return False, f"Bilinmeyen Linux dagitimi: {distro}\nManuel kurulum yapiniz."

        if progress_callback:
            progress_callback(f"Paket yoneticisi: {pkg_manager}")

        # pkexec veya gksudo kullan (GUI için)
        # Önce pkexec'i dene, yoksa sudo kullan
        auth_cmd = None
        if shutil.which("pkexec"):
            auth_cmd = "pkexec"
        elif shutil.which("gksudo"):
            auth_cmd = "gksudo"
        elif shutil.which("kdesudo"):
            auth_cmd = "kdesudo"

        def run_with_auth(cmd):
            if auth_cmd and auth_cmd != "sudo":
                # sudo'yu auth_cmd ile değiştir
                new_cmd = [auth_cmd] + cmd[1:]  # sudo'yu çıkar, auth_cmd ekle
                return subprocess.run(new_cmd, capture_output=True, text=True, timeout=300)
            else:
                # Terminal'de sudo kullan
                return subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Güncelleme
        if update_cmd:
            if progress_callback:
                progress_callback("Paket listesi guncelleniyor...")
            result = run_with_auth(update_cmd)
            if result.returncode != 0:
                # Güncelleme başarısız olsa bile devam et
                pass

        # Kurulum
        if progress_callback:
            progress_callback("FFmpeg kuruluyor...")

        result = run_with_auth(install_cmd)

        if result.returncode == 0:
            # Kurulumu doğrula
            if shutil.which("ffmpeg"):
                return True, "FFmpeg basariyla kuruldu!"
            else:
                return False, "Kurulum tamamlandi ancak FFmpeg bulunamadi."
        else:
            error_msg = result.stderr if result.stderr else "Bilinmeyen hata"
            return False, f"Kurulum basarisiz:\n{error_msg}"

    @staticmethod
    def _install_windows(progress_callback=None) -> Tuple[bool, str]:
        """Windows'ta FFmpeg kur"""
        # winget ile dene
        if shutil.which("winget"):
            if progress_callback:
                progress_callback("winget ile FFmpeg kuruluyor...")

            result = subprocess.run(
                ["winget", "install", "FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, "FFmpeg winget ile kuruldu!\nBilgisayari yeniden baslatin veya yeni terminal acin."

        # chocolatey ile dene
        if shutil.which("choco"):
            if progress_callback:
                progress_callback("Chocolatey ile FFmpeg kuruluyor...")

            result = subprocess.run(
                ["choco", "install", "ffmpeg", "-y"],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, "FFmpeg Chocolatey ile kuruldu!\nBilgisayari yeniden baslatin veya yeni terminal acin."

        # Manuel indirme talimatı
        return False, (
            "Otomatik kurulum yapilamadi.\n\n"
            "Manuel kurulum:\n"
            "1. https://ffmpeg.org/download.html adresine gidin\n"
            "2. Windows builds > gyan.dev linkine tiklayin\n"
            "3. ffmpeg-release-essentials.zip indirin\n"
            "4. Zip'i C:\\ffmpeg klasorune cikarin\n"
            "5. C:\\ffmpeg\\bin klasorunu PATH'e ekleyin\n"
            "6. Bilgisayari yeniden baslatin"
        )

    @staticmethod
    def _install_macos(progress_callback=None) -> Tuple[bool, str]:
        """macOS'ta FFmpeg kur"""
        # Homebrew ile dene
        if shutil.which("brew"):
            if progress_callback:
                progress_callback("Homebrew ile FFmpeg kuruluyor...")

            result = subprocess.run(
                ["brew", "install", "ffmpeg"],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, "FFmpeg Homebrew ile kuruldu!"

        return False, (
            "Homebrew bulunamadi.\n\n"
            "Homebrew kurmak icin terminalde calistirin:\n"
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"\n\n'
            "Sonra:\nbrew install ffmpeg"
        )

    @staticmethod
    def get_video_info(file_path: str) -> Optional[Dict]:
        """Video dosyası hakkında bilgi al"""
        try:
            ffprobe_path = _get_ffprobe_path()
            cmd = [
                ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)

                info = {
                    "duration": 0,
                    "width": 0,
                    "height": 0,
                    "fps": 0,
                    "video_codec": "",
                    "audio_codec": "",
                    "bitrate": 0,
                    "size": 0
                }

                # Format bilgisi
                if "format" in data:
                    fmt = data["format"]
                    info["duration"] = float(fmt.get("duration", 0))
                    info["bitrate"] = int(fmt.get("bit_rate", 0))
                    info["size"] = int(fmt.get("size", 0))

                # Stream bilgileri
                for stream in data.get("streams", []):
                    if stream["codec_type"] == "video":
                        info["width"] = stream.get("width", 0)
                        info["height"] = stream.get("height", 0)
                        info["video_codec"] = stream.get("codec_name", "")
                        # FPS hesapla
                        fps_str = stream.get("r_frame_rate", "0/1")
                        if "/" in fps_str:
                            num, den = fps_str.split("/")
                            if int(den) > 0:
                                info["fps"] = round(int(num) / int(den), 2)
                    elif stream["codec_type"] == "audio":
                        info["audio_codec"] = stream.get("codec_name", "")

                return info
            return None
        except Exception as e:
            print(f"Video bilgisi alinamadi: {e}")
            return None

    @staticmethod
    def get_available_encoders() -> Dict[str, List[str]]:
        """Kullanılabilir encoder'ları listele"""
        encoders = {
            "video": [],
            "audio": []
        }

        # Öncelikli video encoder'lar
        video_encoders = [
            ("h264_nvenc", "H.264 (NVIDIA GPU)"),
            ("hevc_nvenc", "H.265/HEVC (NVIDIA GPU)"),
            ("libx264", "H.264 (CPU)"),
            ("libx265", "H.265/HEVC (CPU)"),
            ("libvpx-vp9", "VP9 (WebM)"),
            ("libaom-av1", "AV1 (CPU)")
        ]

        audio_encoders = [
            ("aac", "AAC"),
            ("libmp3lame", "MP3"),
            ("flac", "FLAC (Kayipsiz)"),
            ("pcm_s16le", "WAV (PCM)"),
            ("libopus", "Opus"),
            ("libvorbis", "Vorbis (OGG)")
        ]

        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout

            for codec, name in video_encoders:
                if codec in output:
                    encoders["video"].append((codec, name))

            for codec, name in audio_encoders:
                if codec in output:
                    encoders["audio"].append((codec, name))

        except Exception:
            # Varsayılan encoder'lar
            encoders["video"] = [("libx264", "H.264 (CPU)")]
            encoders["audio"] = [("aac", "AAC")]

        return encoders

    @staticmethod
    def get_installation_instructions() -> str:
        """FFmpeg kurulum talimatları"""
        system = platform.system().lower()

        if system == "linux":
            return """
FFmpeg Kurulum (Linux):

Ubuntu/Debian:
    sudo apt update
    sudo apt install ffmpeg

Fedora:
    sudo dnf install ffmpeg

Arch Linux:
    sudo pacman -S ffmpeg

openSUSE:
    sudo zypper install ffmpeg
"""
        elif system == "windows":
            return """
FFmpeg Kurulum (Windows):

Yontem 1 - winget (Windows 10/11):
    winget install FFmpeg

Yontem 2 - Chocolatey:
    choco install ffmpeg

Yontem 3 - Manuel:
    1. https://ffmpeg.org/download.html
    2. Windows builds > gyan.dev
    3. ffmpeg-release-essentials.zip indir
    4. C:\\ffmpeg klasorune cikar
    5. C:\\ffmpeg\\bin'i PATH'e ekle
"""
        elif system == "darwin":
            return """
FFmpeg Kurulum (macOS):

Homebrew ile:
    brew install ffmpeg

Homebrew yoksa once onu kurun:
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
"""
        else:
            return "FFmpeg'i sisteminize uygun sekilde kurun: https://ffmpeg.org/download.html"

    @staticmethod
    def parse_progress(line: str, duration: float) -> Optional[Dict]:
        """FFmpeg çıktısından ilerleme bilgisi parse et"""
        progress = {}

        # frame= 1234 fps= 60 ... time=00:01:23.45 ...
        frame_match = re.search(r'frame=\s*(\d+)', line)
        fps_match = re.search(r'fps=\s*([\d.]+)', line)
        time_match = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
        speed_match = re.search(r'speed=\s*([\d.]+)x', line)
        size_match = re.search(r'size=\s*(\d+)(\w+)', line)

        if frame_match:
            progress["frame"] = int(frame_match.group(1))

        if fps_match:
            progress["fps"] = float(fps_match.group(1))

        if time_match:
            h, m, s = time_match.groups()
            current_time = int(h) * 3600 + int(m) * 60 + float(s)
            progress["current_time"] = current_time
            if duration > 0:
                progress["percent"] = min(100, (current_time / duration) * 100)

        if speed_match:
            progress["speed"] = float(speed_match.group(1))

        if size_match:
            size = int(size_match.group(1))
            unit = size_match.group(2).lower()
            multipliers = {"kb": 1024, "mb": 1024**2, "gb": 1024**3, "b": 1}
            progress["size"] = size * multipliers.get(unit, 1)

        return progress if progress else None
