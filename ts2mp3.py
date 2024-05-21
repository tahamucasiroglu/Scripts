from moviepy.editor import VideoFileClip

def extract_audio_from_ts(ts_file, output_audio_file):
    clip = VideoFileClip(ts_file)
    audio = clip.audio
    audio.write_audiofile(output_audio_file, codec='aac')

if __name__ == "__main__":
    ts_file = "input"
    output_audio_file = "output"

    extract_audio_from_ts(ts_file, output_audio_file)
