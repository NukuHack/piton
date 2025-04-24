import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, parse_qs
from huggingface_hub import InferenceClient
from typing import Optional, Dict, List

# Configuration Constants
CONFIG = {
    "PORT": 1234,
    "API_KEY_FILE": os.path.join(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'resources'
        ), 
        'key.txt'
    ),
    "DEFAULT_CONTEXT": "You are a helpful AI assistant. Respond in fluent English and provide useful, concise answers.",
    "MODEL_NAME": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    "MODEL_PARAMS": {
        "temperature": 0.1,
        "max_tokens": 4096,
        "top_p": 0.5,
        "stream": True
    }
}

class AIClient:
    """Wrapper for AI client operations"""
    def __init__(self):
        self.api_key = self._load_api_key()
        self.client = None
        
    def _load_api_key(self) -> str:
        """Load API key from file"""
        if os.path.exists(CONFIG["API_KEY_FILE"]):
            with open(CONFIG["API_KEY_FILE"], 'r') as file:
                return file.readline().strip()
        raise FileNotFoundError(f"API key file not found at {CONFIG['API_KEY_FILE']}")
    
    def initialize_client(self):
        """Initialize the inference client"""
        if not self.client:
            self.client = InferenceClient(
                provider="nebius",
                api_key=self.api_key
            )
    
    def get_response(self, user_message: str) -> str:
        """Get AI response for user message"""
        messages = [{"role": "user", "content": f"{CONFIG['DEFAULT_CONTEXT']} {user_message}"}]
        
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
            print(f"AI Error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with AI integration"""
    
    def __init__(self, *args, ai_client: Optional[AIClient] = None, **kwargs):
        self.ai_client = ai_client or AIClient()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/' or '?' in self.path:
                self._handle_root_request()
            else:
                self._handle_static_file()
        except Exception as e:
            self._handle_error(500, f"Server error: {str(e)}")
    
    def _handle_root_request(self):
        """Handle requests to the root path"""
        user_input = self._extract_user_input()
        ai_response = self._get_ai_response(user_input) if user_input else ""
        
        try:
            content = self._load_html_template()
            content = content.replace('<!-- RESPONSE_PLACEHOLDER -->', ai_response)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self._handle_error(404, "File not found")
    
    def _handle_static_file(self):
        """Handle requests for static files"""
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
    
    def _extract_user_input(self) -> str:
        """Extract user input from query parameters"""
        if '?' not in self.path:
            return ""
            
        query = self.path.split('?')[1]
        params = parse_qs(query)
        return unquote(params.get('message', [''])[0]).strip()
    
    def _get_ai_response(self, user_input: str) -> str:
        """Get AI response for user input"""
        print(f"Processing user input: {user_input}")
        response = self.ai_client.get_response(user_input)
        print(f"Generated response: {response}")
        return response
    
    def _load_html_template(self) -> str:
        """Load HTML template file"""
        html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        with open(html_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_content_type(self, file_path: str) -> str:
        """Determine content type based on file extension"""
        if file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        return 'text/plain'
    
    def _handle_error(self, code: int, message: str):
        """Handle HTTP errors"""
        self.send_error(code, message)

def run_server(port: int = CONFIG["PORT"]):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, lambda *args: HTTPRequestHandler(*args, ai_client=AIClient()))
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()