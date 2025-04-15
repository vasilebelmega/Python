import boto3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # Replace with your region
table_name = "meetings_table"
table = dynamodb.Table(table_name)

# Function to add sample data to DynamoDB
def setup_database():
    try:
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

# HTTP request handler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Fetch all meetings from DynamoDB
            response = table.scan()
            items = response.get('Items', [])

            # Build the HTML response
            html_response = "<html><body><h1>Meetings Schedule</h1><ul>"
            for item in items:
                html_response += f"<li>{item['day_of_week']}: {item['meeting']}</li>"
            html_response += "</ul></body></html>"

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_response.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

# Run the HTTP server
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    setup_database()  # Set up the database before starting the server
    server_address = ('0.0.0.0', 8080)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port 8080...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
