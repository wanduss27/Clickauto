import os
import logging
from flask import Flask, request

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Đường dẫn để lưu log
LOG_DIR = 'logs'

# Middleware để log các request
@app.before_request
def log_request_info():
    logging.info('Headers: %s', request.headers)
    logging.info('Body: %s', request.get_data())

# Middleware để log các response
@app.after_request
def log_response_info(response):
    logging.info('Response status: %s', response.status)
    logging.info('Response body: %s', response.get_data())
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    # Lưu file log vào thư mục 'logs'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    file.save(os.path.join(LOG_DIR, file.filename))
    return 'File uploaded successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Bạn có thể thay đổi cổng nếu cần
