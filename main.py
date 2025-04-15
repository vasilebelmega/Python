import boto3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
from datetime import datetime, timedelta

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # Replace with your region
table_name = "meetings_table"
table = dynamodb.Table(table_name)

# Function to clean old entries from DynamoDB
def clean_old_entries():
    try:
        # Fetch all items from the table
        response = table.scan()
        items = response.get('Items', [])

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Delete items older than today
        for item in items:
            if 'timestamp' in item:
                item_date = datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                if item_date < today:
                    table.delete_item(Key={'id': item['id']})
                    print(f"Deleted old entry: {item}")
    except Exception as e:
        print(f"Error cleaning old entries: {e}")

# Function to add a new meeting to DynamoDB
def add_meeting(day_of_week, meeting_name):
    try:
        new_meeting = {
            "id": str(uuid.uuid4()),
            "day_of_week": day_of_week,
            "meeting": meeting_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        table.put_item(Item=new_meeting)
        print(f"Added new meeting: {new_meeting}")
    except Exception as e:
        print(f"Error adding new meeting: {e}")

# HTTP request handler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Clean old entries before displaying
            clean_old_entries()

            # Fetch all meetings from DynamoDB
            response = table.scan()
            items = response.get('Items', [])

            # Build the HTML response
            html_response = """
            <html>
            <body>
                <h1>Meetings Schedule</h1>
                <ul>
            """
            for item in items:
                timestamp = item.get('timestamp', 'No timestamp available')
                html_response += f"<li>{item['day_of_week']} ({timestamp}): {item['meeting']}</li>"
            html_response += """
                </ul>
                <h2>Add a New Meeting</h2>
                <form method="POST">
                    <label for="day_of_week">Day of Week:</label>
                    <input type="text" id="day_of_week" name="day_of_week" required><br>
                    <label for="meeting">Meeting Name:</label>
                    <input type="text" id="meeting" name="meeting" required><br>
                    <button type="submit">Add Meeting</button>
                </form>
            </body>
            </html>
            """

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_response.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

    def do_POST(self):
        try:
            # Parse the form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = dict(x.split('=') for x in post_data.split('&'))

            # Add the new meeting
            day_of_week = form_data.get('day_of_week', '').replace('+', ' ')
            meeting_name = form_data.get('meeting', '').replace('+', ' ')
            add_meeting(day_of_week, meeting_name)

            # Redirect back to the main page
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

# Run the HTTP server
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('0.0.0.0', 8081)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port 8081...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
