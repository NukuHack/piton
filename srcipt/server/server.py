import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, parse_qs
from huggingface_hub import InferenceClient
from typing import Optional, Dict, List, Tuple
import json
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configuration Constants
CONFIG = {
    "PORT": 1234,
    "API_KEY_FILE": os.path.join(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'resources'),
            'key.txt'
        ),
    "DEFAULT_CONTEXT": """

-_-
    """,
    "DEFAULT_CONTEXT_TWO": """

-_-

    """,
    "MODEL_NAME": "deepseek-ai/DeepSeek-V3-0324",
    "MODEL_PARAMS": {
        "temperature": 0.1,
        "max_tokens": 4096,
        "top_p": 0.5,
        "stream": True
    },
    "RATE_LIMIT": {
        "REQUESTS_PER_MINUTE": 30,  # Max requests per IP per minute
        "BAN_TIME": 30  # 30 sec ban for exceeding rate limit
    },
    "ALLOWED_ORIGINS": ["http://localhost", "http://127.0.0.1"],
    "MAX_REQUEST_SIZE": 1024 * 10  # 10KB max request size
}

class RateLimiter:
    """Simple rate limiting implementation"""
    def __init__(self):
        self.requests = defaultdict(list)
        self.banned_ips = {}
    
    def check_rate_limit(self, ip: str) -> Tuple[bool, Optional[str]]:
        """Check if IP is rate limited"""
        current_time = time.time()
        
        # Check if IP is banned
        if ip in self.banned_ips:
            if current_time < self.banned_ips[ip]:
                return False, f"Too many requests. Try again after {int(self.banned_ips[ip] - current_time)} seconds"
            del self.banned_ips[ip]
        
        # Clean up old requests
        self.requests[ip] = [t for t in self.requests[ip] if current_time - t < 60]
        
        # Check current rate
        if len(self.requests[ip]) >= CONFIG["RATE_LIMIT"]["REQUESTS_PER_MINUTE"]:
            # Ban the IP
            self.banned_ips[ip] = current_time + CONFIG["RATE_LIMIT"]["BAN_TIME"]
            return False, "Too many requests. You have been temporarily banned."
        
        # Record this request
        self.requests[ip].append(current_time)
        return True, None

class AIClient:
    """Wrapper for AI client operations"""
    def __init__(self):
        self.api_key = self._load_api_key()
        self.client = None
        
    def _load_api_key(self) -> str:
        """Load API key from file"""
        try:
            if os.path.exists(CONFIG["API_KEY_FILE"]):
                with open(CONFIG["API_KEY_FILE"], 'r') as file:
                    key = file.readline().strip()
                    if not key:
                        raise ValueError("API key file is empty")
                    return key
            raise FileNotFoundError(f"API key file not found at {CONFIG['API_KEY_FILE']}")
        except Exception as e:
            logging.error(f"Failed to load API key: {str(e)}")
            raise
        
    def initialize_client(self):
        """Initialize the inference client"""
        if not self.client:
            self.client = InferenceClient(
                provider="nebius",
                api_key=self.api_key
            )
            logging.info("AI client initialized")
    
    def get_response(self, user_message: str) -> str:
        """Get AI response for user message"""
        if not user_message.strip():
            return "Please provide a valid question or prompt."
                
        messages = [{"role": "user", "content": f"{CONFIG['DEFAULT_CONTEXT']}"},{"role": "assistant", "content": f"{CONFIG['DEFAULT_CONTEXT_TWO']}"},{"role": "user", "content": f"{user_message}"}]
        
        try:
            self.initialize_client()
            response = self.client.chat.completions.create(
                model=CONFIG["MODEL_NAME"],
                messages=messages,
                **CONFIG["MODEL_PARAMS"]
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            return full_response
            
        except Exception as e:
            logging.error(f"AI Error: {str(e)}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with AI integration"""
    
    def __init__(self, *args, ai_client: Optional[AIClient] = None, rate_limiter: Optional[RateLimiter] = None, **kwargs):
        self.ai_client = ai_client or AIClient()
        self.rate_limiter = rate_limiter or RateLimiter()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self._serve_homepage()
            else:
                self._handle_static_file()
        except Exception as e:
            self._handle_error(500, f"Server error: {str(e)}")
            logging.error(f"GET request error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests for API calls"""
        client_ip = self.client_address[0]
        
        # Check rate limit
        allowed, message = self.rate_limiter.check_rate_limit(client_ip)
        if not allowed:
            self._send_json_response(429, {"error": message})
            return
            
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > CONFIG["MAX_REQUEST_SIZE"]:
                raise ValueError("Request too large")
                
            content_type = self.headers.get('Content-Type', '')
            
            if self.path == '/api/chat':
                if 'application/json' in content_type:
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    user_message = data.get('message', '').strip()
                else:
                    post_data = self.rfile.read(content_length)
                    data = parse_qs(post_data.decode('utf-8'))
                    user_message = unquote(data.get('message', [''])[0]).strip()
                
                if not user_message:
                    self._send_json_response(400, {"error": "Message is required"})
                    return
                
                ai_response = self.ai_client.get_response(user_message)
                self._send_json_response(200, {"response": ai_response})
            else:
                self._send_json_response(404, {"error": "Endpoint not found"})
                
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
        except ValueError as e:
            self._send_json_response(400, {"error": str(e)})
        except Exception as e:
            self._send_json_response(500, {"error": f"Server error: {str(e)}"})
            logging.error(f"POST request error: {str(e)}")
    
    def _serve_homepage(self):
        """Serve the HTML homepage"""
        try:
            content = self._load_html_template()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self._handle_error(404, "File not found")
    
    def _handle_static_file(self):
        """Handle requests for static files"""
        # Security: Prevent directory traversal
        if '..' in self.path or self.path.startswith('/'):
            self._handle_error(403, "Forbidden")
            return
            
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.path[1:])
        
        if not os.path.isfile(file_path):
            self._handle_error(404, "File not found")
            return
            
        content_type = self._get_content_type(file_path)
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self._handle_error(500, f"Error reading file: {str(e)}")
    
    def _send_json_response(self, status_code: int, data: Dict):
        """Send a JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        
        # Handle CORS
        origin = self.headers.get('Origin')
        if origin and any(origin.startswith(allowed) for allowed in CONFIG["ALLOWED_ORIGINS"]):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _load_html_template(self) -> str:
        """Load HTML template file"""
        html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        with open(html_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_content_type(self, file_path: str) -> str:
        """Determine content type based on file extension"""
        extension = os.path.splitext(file_path)[1].lower()
        content_types = {
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
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def _handle_error(self, code: int, message: str):
        """Handle HTTP errors"""
        self.send_error(code, message)
        logging.error(f"HTTP {code}: {message}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port: int = CONFIG["PORT"]):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(
        server_address, 
        lambda *args: HTTPRequestHandler(
            *args, 
            ai_client=AIClient(),
            rate_limiter=RateLimiter()
        )
    )
    logging.info(f'Starting server on port {port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server shutting down")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()