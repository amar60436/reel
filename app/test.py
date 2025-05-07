# app/test.py
import argparse
import subprocess
import collections
import cv2
import time
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Input stream URL (HLS or RTMP)")
parser.add_argument("--output", help="RTMP output stream URL", required=True)
args = parser.parse_args()

input_url = args.input
output_url = args.output

width, height = 640, 480
fps = 25
buffer_seconds = 10
buffer_size = buffer_seconds * fps
frame_buffer = collections.deque(maxlen=buffer_size)

ffmpeg_input_cmd = [
    'ffmpeg',
    '-i', input_url,
    '-loglevel', 'quiet',
    '-f', 'rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', f'{width}x{height}',
    '-r', str(fps),
    '-'
]

cap = subprocess.Popen(ffmpeg_input_cmd, stdout=subprocess.PIPE)

ffmpeg_output_cmd = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', f'{width}x{height}',
    '-r', str(fps),
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'superfast',
    '-tune', 'zerolatency',
    '-f', 'flv',
    output_url
]

process = subprocess.Popen(ffmpeg_output_cmd, stdin=subprocess.PIPE)

frame_size = width * height * 3

while len(frame_buffer) < buffer_size:
    raw_frame = cap.stdout.read(frame_size)
    if not raw_frame:
        print("Error: Failed to read frame.")
        break
    frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
    frame_buffer.append(frame)

try:
    while True:
        raw_frame = cap.stdout.read(frame_size)
        if not raw_frame:
            print("End of stream or error.")
            break
        frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
        frame_buffer.append(frame)
        buffered_frame = frame_buffer.popleft()
        process.stdin.write(buffered_frame.tobytes())
except KeyboardInterrupt:
    pass
finally:
    cap.terminate()
    process.stdin.close()
    process.wait()
