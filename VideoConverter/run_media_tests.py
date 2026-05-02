import os
import time

from core.converter import BatchConverter, VideoConverter
from core.ffmpeg_utils import FFmpegUtils


DESKTOP = r"C:\Users\taham\OneDrive\Desktop"
OUT_DIR = os.path.join(DESKTOP, "TMVC_Test_Output")


def ensure_output_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def run_sync_tests():
    tests = [
        (
            "mp4_to_mp3",
            os.path.join(DESKTOP, "Download.mp4"),
            os.path.join(OUT_DIR, "Download_audio_test.mp3"),
            {"vcodec": None, "acodec": "libmp3lame", "audio_bitrate": "192k", "audio_only": True},
        ),
        (
            "mp4_to_webm",
            os.path.join(DESKTOP, "Download.mp4"),
            os.path.join(OUT_DIR, "Download_video_test.webm"),
            {"vcodec": "libvpx-vp9", "acodec": "libopus", "bitrate": "1000k", "audio_bitrate": "96k", "preset": None},
        ),
        (
            "mp3_to_wav",
            os.path.join(DESKTOP, "Download.mp3"),
            os.path.join(OUT_DIR, "Download_audio_test.wav"),
            {"vcodec": None, "acodec": "pcm_s16le", "audio_only": True},
        ),
        (
            "mp3_to_flac",
            os.path.join(DESKTOP, "Download.mp3"),
            os.path.join(OUT_DIR, "Download_audio_test.flac"),
            {"vcodec": None, "acodec": "flac", "audio_only": True},
        ),
    ]

    converter = VideoConverter()
    results = []
    for name, src, dst, settings in tests:
        if os.path.exists(dst):
            os.remove(dst)
        started = time.time()
        ok, msg = converter.convert_sync(src, dst, settings)
        elapsed = time.time() - started
        size = os.path.getsize(dst) if os.path.exists(dst) else 0
        info = FFmpegUtils.get_video_info(dst) if ok and size else None
        results.append((name, ok, size, elapsed, dst, msg, info))
        print(f"{name}: ok={ok} size={size} elapsed={elapsed:.1f}s dst={dst}")
        if info:
            print(f"  info={info}")
        if not ok:
            print(f"  error={msg[:1200]}")
    return results


def run_batch_audio_test():
    batch = BatchConverter()
    sources = [
        os.path.join(DESKTOP, "Download.mp4"),
        os.path.join(DESKTOP, "Download.mp3"),
    ]
    settings = {"vcodec": None, "acodec": "libmp3lame", "audio_bitrate": "128k", "audio_only": True}

    for index, src in enumerate(sources, start=1):
        dst = os.path.join(OUT_DIR, f"batch_audio_{index}.mp3")
        if os.path.exists(dst):
            os.remove(dst)
        batch.add_to_queue(src, dst, settings.copy())

    done = False

    def on_batch_progress(completed, total, queue):
        print(f"batch_progress: {completed}/{total}")

    def on_item_progress(index, item, progress):
        percent = progress.get("percent", 0)
        print(f"item_progress: index={index} percent={percent:.1f} file={os.path.basename(item['input'])}")

    def on_complete(queue):
        nonlocal done
        done = True
        print("batch_complete:")
        for item in queue:
            size = os.path.getsize(item["output"]) if os.path.exists(item["output"]) else 0
            print(f"  {os.path.basename(item['input'])}: status={item.get('status')} size={size} error={item.get('error')}")

    batch.set_callbacks(on_batch_progress, on_item_progress, on_complete)
    batch.start(max_workers=1)

    while not done:
        time.sleep(0.2)


if __name__ == "__main__":
    ensure_output_dir()
    run_sync_tests()
    run_batch_audio_test()
