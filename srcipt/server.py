#pip install --upgrade huggingface_hub
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from huggingface_hub import InferenceClient

file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources'), 'key.txt')

# Check if the file exists
if os.path.exists(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the first line
        first_line = file.readline().strip()
else:
    print(f"The file {file_path} does not exist.")


default_context = "This is the default message you can ignore it : \"Hello, speak in fluent englis, also help in any way you can:\" "


def get_msg_w_msg(user_message):
    # Integrate AI interaction
    messages = [
        {"role": "user", "content": default_context+user_message}
    ]
    try:
        client = InferenceClient(
            provider="nebius",
            api_key=first_line # your own key
        )
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
            top_p=0.5,
            stream=True
        )
        full_response = ""
        for chunk in response:
            full_response += chunk.choices[0].delta.content
        return full_response
    except Exception as e:
        print(e)
        return f"Error: {e}"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Check if the query contains the message parameter
        messages = ""
        query = self.path.split('?')
        if len(query) > 1:
            params = query[1].split('&')
            for param in params:
                key, value = param.split('=')
                if key == 'message':
                    user_input = value
                    print(user_input)
                    messages = get_msg_w_msg(user_input)
                    print(messages)
                    break

        html = f"""
        <html>
        <head>
            <title>AI Message Interface</title>
        </head>
        <body>
            <h1>AI Message Interface</h1>
            <form action="/send_message" method="get">
                <label for="message">Enter your message:</label><br><br>
                <input type="text" id="message" name="message" style="width: 300px;"><br><br>
                <input type="submit" value="Send">
            </form>
            """+messages+"""
        </body>
        </html>
        """

        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = post_data.decode('utf-8').split('&')
        user_input = ""
        for param in params:
            key, value = param.split('=')
            if key == 'message':
                user_input = value
                break

        messages = get_msg_w_msg(user_input)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <html>
        <head>
            <title>AI Message Interface</title>
        </head>
        <body>
            <h1>AI Message Interface</h1>
            <p>{messages}</p>
            <form action="/send_message" method="get">
                <label for="message">Enter your message:</label><br><br>
                <input type="text" id="message" name="message" style="width: 300px;"><br><br>
                <input type="submit" value="Send">
            </form>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=1234):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
