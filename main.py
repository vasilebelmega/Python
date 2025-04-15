import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import os

# Database connection details
DB_HOST = os.getenv("DB_HOST")  
DB_PORT = 3306
DB_USER = "admin"  # Replace with your RDS username
DB_PASSWORD = "Fizyfangs97."  # Replace with your RDS password
DB_NAME = "meetings_db"  # Database name

print(f"Connecting to database at {DB_HOST}...")
# Create a connection to the database
def setup_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # Create the table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day_of_week VARCHAR(20),
                meeting VARCHAR(255)
            )
        """)

        # Insert random meetings for working days
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        meetings = ["Team Sync", "Project Update", "Client Call", "Code Review", "Planning Session"]

        for day in days_of_week:
            meeting = random.choice(meetings)
            cursor.execute("INSERT INTO meetings (day_of_week, meeting) VALUES (%s, %s)", (day, meeting))

        connection.commit()
        print("Database setup complete and data inserted.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Connect to the database
            connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            # Fetch all meetings
            cursor.execute("SELECT day_of_week, meeting FROM meetings")
            rows = cursor.fetchall()

            # Build the HTML response
            response = "<html><body><h1>Meetings Schedule</h1><ul>"
            for row in rows:
                response += f"<li>{row[0]}: {row[1]}</li>"
            response += "</ul></body></html>"

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.encode())
        except mysql.connector.Error as err:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {err}".encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    setup_database()  # Set up the database before starting the server
    server_address = ('0.0.0.0', 5000)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port 5000...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()