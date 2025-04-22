from flask import Flask, render_template_string, Response, request, session, redirect, url_for
import cv2
from config import STREAM_CREDENTIALS

app = Flask(__name__)
app.secret_key = 'CHANGE_THIS_TO_RANDOM_SECRET'

# Shared frame buffer
frame_buffer = None

LOGIN_PAGE = """
<html><body>
  <h2>Login to Stream</h2>
  {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
  <form method="post">
    Stream ID: <input name="stream_id"><br>
    Password: <input name="password" type="password"><br>
    <input type="submit" value="Login">
  </form>
</body></html>
"""

STREAM_PAGE = """
<html><body>
  <h2>Live Stream</h2>
  <img src="{{ url_for('video_feed') }}" />
</body></html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sid = request.form.get('stream_id')
        pwd = request.form.get('password')
        if STREAM_CREDENTIALS.get(sid) == pwd:
            session['authenticated'] = True
            session['stream_id'] = sid
            return redirect(url_for('stream_page'))
        else:
            return render_template_string(LOGIN_PAGE, error='Invalid credentials')
    return render_template_string(LOGIN_PAGE)

@app.route('/')
@app.route('/stream')
def stream_page():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template_string(STREAM_PAGE)


def gen_frames():
    global frame_buffer
    while True:
        if frame_buffer is None:
            continue
        _, jpeg = cv2.imencode('.jpg', frame_buffer)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Utility to update frame from server loop
def set_frame(frame):
    global frame_buffer
    frame_buffer = frame

# Run the web server
def run(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, threaded=True)