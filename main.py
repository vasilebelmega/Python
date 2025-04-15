import boto3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
from datetime import datetime

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # Replace with your region
table_name = "meetings_table"
table = dynamodb.Table(table_name)

# Function to delete all entries from DynamoDB
def delete_all_entries():
    try:
        # Scan the table to get all items
        response = table.scan()
        items = response.get('Items', [])

        # Delete each item
        for item in items:
            table.delete_item(Key={'id': item['id']})
            print(f"Deleted entry: {item}")
    except Exception as e:
        print(f"Error deleting entries: {e}")

# Function to add sample data to DynamoDB
def setup_database():
    try:
        # Delete all existing entries first
        delete_all_entries()

        # Add sample meetings to the DynamoDB table
        meetings = [
            {"id": str(uuid.uuid4()), "day_of_week": "Monday", "meeting": "Team Sync"},
            {"id": str(uuid.uuid4()), "day_of_week": "Tuesday", "meeting": "Project Update"},
            {"id": str(uuid.uuid4()), "day_of_week": "Wednesday", "meeting": "Client Call"},
            {"id": str(uuid.uuid4()), "day_of_week": "Thursday", "meeting": "Code Review"},
            {"id": str(uuid.uuid4()), "day_of_week": "Friday", "meeting": "Planning Session"}
        ]

        for meeting in meetings:
            table.put_item(Item=meeting)

        print("Sample data added to DynamoDB.")
    except Exception as e:
        print(f"Error setting up database: {e}")

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
    setup_database()  # Set up the database before starting the server
    server_address = ('0.0.0.0', 8081)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port 8081...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
