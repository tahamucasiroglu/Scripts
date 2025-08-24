# winget install ffmpeg
# pip install yt_dlp
import yt_dlp
import os
from pathlib import Path
import re

class YouTubeMP3Downloader:
    def __init__(self, output_path="downloads"):
        """
        YouTube MP3 İndirici
        
        Args:
            output_path (str): İndirilen dosyaların kaydedileceği klasör
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
    
    def clean_youtube_url(self, url):
        """
        YouTube URL'sinden playlist parametrelerini temizler
        
        Args:
            url (str): YouTube URL'i
            
        Returns:
            str: Temizlenmiş URL
        """
        # Video ID'sini çıkar
        video_id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
        
    def download_as_mp3(self, url, audio_quality='192'):
        """
        YouTube videosunu MP3 olarak indirir
        
        Args:
            url (str): YouTube video URL'i
            audio_quality (str): Ses kalitesi (128, 192, 256, 320 kbps)
        
        Returns:
            bool: İndirme başarılı ise True, değilse False
        """
        # yt-dlp ayarları
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'noplaylist': True,  # SADECE TEK VİDEO İNDİR!
            'concurrent_fragment_downloads': 5,  # Daha hızlı indirme için
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"🎵 Video bilgisi alınıyor: {url}")
                
                # Video bilgilerini al
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                print(f"📹 Video: {video_title}")
                print(f"⏱️  Süre: {self._format_duration(duration)}")
                print(f"🎧 Ses kalitesi: {audio_quality} kbps")
                print(f"📂 Kayıt yeri: {self.output_path}")
                print("-" * 50)
                
                # İndirme işlemini başlat
                print("⬇️  İndiriliyor...")
                ydl.download([url])
                
                print(f"✅ İndirme tamamlandı: {video_title}.mp3")
                return True
                
        except yt_dlp.utils.DownloadError as e:
            print(f"❌ İndirme hatası: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {str(e)}")
            return False
    
    def download_playlist(self, playlist_url, audio_quality='192'):
        """
        YouTube playlist'ini MP3 olarak indirir
        
        Args:
            playlist_url (str): YouTube playlist URL'i
            audio_quality (str): Ses kalitesi
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
            'outtmpl': str(self.output_path / '%(playlist)s/%(title)s.%(ext)s'),
            'quiet': False,
            'extract_flat': 'in_playlist',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"📋 Playlist bilgisi alınıyor...")
                
                # Playlist bilgilerini al
                info = ydl.extract_info(playlist_url, download=False)
                playlist_title = info.get('title', 'Unknown Playlist')
                video_count = len(info.get('entries', []))
                
                print(f"📋 Playlist: {playlist_title}")
                print(f"🎵 Video sayısı: {video_count}")
                print("-" * 50)
                
                # Playlist'i indir
                ydl_opts['extract_flat'] = False
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([playlist_url])
                
                print(f"✅ Playlist indirme tamamlandı!")
                return True
                
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return False
    
    def _format_duration(self, seconds):
        """Süreyi okunabilir formata çevirir"""
        if seconds:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes}:{secs:02d}"
        return "Bilinmiyor"


def main():
    """Ana program"""
    print("=" * 50)
    print("🎵 YouTube MP3 İndirici 🎵")
    print("=" * 50)
    
    # İndirici nesnesini oluştur
    downloader = YouTubeMP3Downloader()
    
    while True:
        print("\n📌 Seçenekler:")
        print("1. Tek video indir")
        print("2. Playlist indir")
        print("3. Çıkış")
        
        choice = input("\nSeçiminiz (1-3): ").strip()
        
        if choice == '1':
            url = input("\n🔗 YouTube video URL'sini girin: ").strip()
            
            # URL'de playlist varsa uyar
            if 'list=' in url or '&start_radio=' in url:
                print("\n⚠️  URL'de playlist parametresi tespit edildi!")
                print("1. Sadece bu videoyu indir (önerilen)")
                print("2. URL'yi olduğu gibi kullan")
                
                clean_choice = input("Seçiminiz (1-2): ").strip()
                if clean_choice == '1':
                    url = downloader.clean_youtube_url(url)
                    print(f"✅ Temiz URL: {url}")
            
            print("\n🎧 Ses kalitesi seçin:")
            print("1. Normal (128 kbps)")
            print("2. İyi (192 kbps) - Önerilen")
            print("3. Yüksek (256 kbps)")
            print("4. En yüksek (320 kbps)")
            
            quality_choice = input("Seçiminiz (1-4): ").strip()
            quality_map = {'1': '128', '2': '192', '3': '256', '4': '320'}
            quality = quality_map.get(quality_choice, '192')
            
            print("\n" + "=" * 50)
            downloader.download_as_mp3(url, quality)
            
        elif choice == '2':
            url = input("\n🔗 YouTube playlist URL'sini girin: ").strip()
            
            print("\n🎧 Ses kalitesi seçin:")
            print("1. Normal (128 kbps)")
            print("2. İyi (192 kbps) - Önerilen")
            print("3. Yüksek (256 kbps)")
            print("4. En yüksek (320 kbps)")
            
            quality_choice = input("Seçiminiz (1-4): ").strip()
            quality_map = {'1': '128', '2': '192', '3': '256', '4': '320'}
            quality = quality_map.get(quality_choice, '192')
            
            print("\n" + "=" * 50)
            downloader.download_playlist(url, quality)
            
        elif choice == '3':
            print("\n👋 Güle güle!")
            break
        else:
            print("\n❌ Geçersiz seçim!")


if __name__ == "__main__":
    print("""
    ⚠️  UYARI: Bu program sadece eğitim amaçlıdır.
    Telif hakkı olan içerikleri indirmek yasaktır.
    Sadece kendi içeriğinizi veya telif hakkı olmayan içerikleri indirin.
    """)
    
    input("Devam etmek için Enter'a basın...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")