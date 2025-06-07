import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, parse_qs
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Disable compiler requirements
os.environ['TORCHDYNAMO_DISABLE'] = '1'

PORT = 1234
MODEL_NAME = "microsoft/bitnet-b1.58-2B-4T"
MODEL_PARAMS = {
    "temperature": 0.7,
    "max_new_tokens": 512,
    "top_p": 0.9,
}

class AIClient:
    def __init__(self):
        print(f"Loading model {MODEL_NAME}...")
        try:
            # Disable torch compile which requires a compiler
            torch._dynamo.config.suppress_errors = True
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float32,  # Use float32 for CPU
                low_cpu_mem_usage=True
            )
            print("Model loaded successfully")
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            raise
        
    def get_response(self, user_message: str) -> str:
        if not user_message.strip():
            return "Please provide a valid question or prompt."
        
        try:
            inputs = self.tokenizer(user_message, return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                **MODEL_PARAMS
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(user_message):].strip()
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return f"Error: {str(e)}"

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, ai_client=None, **kwargs):
        self.ai_client = ai_client or AIClient()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        try:
            if self.path in ('/', '/index.html'):
                self.serve_file('index.html', 'text/html')
            else:
                self.serve_file(self.path[1:])
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
            print(f"GET error: {e}")
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            
            if self.path == '/api/chat':
                post_data = self.rfile.read(content_length)
                
                if 'application/json' in content_type:
                    data = json.loads(post_data.decode('utf-8'))
                    user_message = data.get('message', '').strip()
                else:
                    data = parse_qs(post_data.decode('utf-8'))
                    user_message = unquote(data.get('message', [''])[0]).strip()
                
                if not user_message:
                    self.send_json(400, {"error": "Message is required"})
                    return
                
                response = self.ai_client.get_response(user_message)
                self.send_json(200, {"response": response})
            else:
                self.send_json(404, {"error": "Endpoint not found"})
        except Exception as e:
            self.send_json(500, {"error": f"Server error: {str(e)}"})
            print(f"POST error: {e}")
    
    def serve_file(self, filename, content_type=None):
        if '..' in filename or filename.startswith('/'):
            self.send_error(403, "Forbidden")
            return
            
        filepath = os.path.join('static', filename)
        
        if not os.path.isfile(filepath):
            self.send_error(404, "File not found")
            return
            
        with open(filepath, 'rb') as f:
            content = f.read()
        
        if not content_type:
            content_type = self.guess_content_type(filepath)
        
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)
    
    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def guess_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }.get(ext, 'application/octet-stream')

def run_server(port=PORT):    
    server_address = ('', port)
    httpd = HTTPServer(server_address, lambda *args: HTTPRequestHandler(*args))
    print(f'Server running on port {port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    run_server()