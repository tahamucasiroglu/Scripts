from moviepy import VideoFileClip

def convert_ts_to_mp4(input_ts, output_mp4):
    video_clip = VideoFileClip(input_ts)
    video_clip = video_clip.subclipped(0,-6720)
    video_clip.write_videofile(output_mp4, codec='libx264', audio_codec='aac', bitrate='5000k', preset='slow', threads=4)

if __name__ == "__main__":
    input_ts = r""
    output_mp4 = r""

    convert_ts_to_mp4(input_ts, output_mp4)
