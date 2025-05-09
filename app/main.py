# app/main.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/stream', methods=['POST'])
def start_stream():
    data = request.json
    manifest_url = data.get('manifest_url')

    if not manifest_url:
        return jsonify({'error': 'manifest_url is required'}), 400

    # output_url = "rtmp://rtmp-server/stream/processed"
    # output_url = "rtmp://localhost:1935/stream/processed"
    output_url = "rtmp://nginx-rtmp:1935/stream/processed"
    # output_url = "rtmp://nginx-rtmp.my-app.local:1935/stream/processed" 
    # output_url = "rtmp://65.1.133.222:1935/stream/processed"

    #a



    try:
        subprocess.Popen(['python', 'test.py', manifest_url, '--output', output_url])
        return jsonify({'message': 'Streaming started', 'rtmp_url': output_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
