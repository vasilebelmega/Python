import boto3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
from datetime import datetime, timedelta

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # Replace with your region
table_name = "meetings_table"
table = dynamodb.Table(table_name)

# Function to get the current day of the week
def get_current_day():
    return datetime.now().strftime("%A")  # Returns the full name of the current day (e.g., "Monday")

# Function to get the days of the current week starting from today
def get_week_days():
    current_day = datetime.now().weekday()  # Monday is 0, Sunday is 6
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return week_days[current_day:] + week_days[:current_day]  # Rotate the list to start from today

# Function to delete old entries from DynamoDB
def clean_old_entries():
    try:
        # Fetch all items from the table
        response = table.scan()
        items = response.get('Items', [])

        # Get the valid days for the current week
        valid_days = get_week_days()

        # Delete items that are not in the valid days
        for item in items:
            if item['day_of_week'] not in valid_days:
                table.delete_item(Key={'id': item['id']})
                print(f"Deleted old entry: {item}")
    except Exception as e:
        print(f"Error cleaning old entries: {e}")

# Function to add sample data to DynamoDB
def setup_database():
    try:
        # Clean old entries first
        clean_old_entries()

        # Add sample meetings for the current week
        valid_days = get_week_days()
        meetings = [
            {"id": str(uuid.uuid4()), "day_of_week": day, "meeting": f"Meeting on {day}", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            for day in valid_days
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
                html_response += f"<li>{item['day_of_week']} ({item['timestamp']}): {item['meeting']}</li>"
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
    server_address = ('0.0.0.0', 8081)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port 8081...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
