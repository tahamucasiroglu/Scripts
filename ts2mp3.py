from moviepy import VideoFileClip

def extract_audio_from_ts(ts_file, output_mp3_file):
    with VideoFileClip(ts_file) as clip:
        if clip.audio is None:
            raise RuntimeError("Bu .ts dosyasında audio stream yok gibi görünüyor.")
        clip.audio.write_audiofile(
            output_mp3_file,
            codec="libmp3lame",   # MP3 codec
            bitrate="192k"        # istersen 128k/256k yap
        )

if __name__ == "__main__":
    ts_file = r""
    output_mp3_file = r""
    extract_audio_from_ts(ts_file, output_mp3_file)
