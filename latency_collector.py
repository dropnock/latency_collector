import rrdtool
import time
import subprocess
import os
import smtplib
from ping3 import ping
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sys
import signal

# Define constants for configuration
RRD_FILE = "latency.rrd"
GRAPH_FILE = "latency_graph.png"
PING_HOST = "8.8.8.8"  # Replace with the target host for latency checks
PING_COUNT = 4  # Number of pings to send
PING_TIMEOUT = 2  # Timeout for each ping in seconds
LATENCY_STEP = 10  # Data collection interval in seconds
GRAPH_WIDTH = 600  # Width of the graph image
GRAPH_HEIGHT = 200  # Height of the graph image
LATENCY_THRESHOLD = 60  # Threshold in ms for latency alert
EMAIL_SENDER = "your-email@example.com"  # Replace with the sender's email
EMAIL_PASSWORD = "your-email-password"  # Replace with the sender's email password (use app password if 2FA is enabled)
EMAIL_SMTP_SERVER = "smtp.example.com"  # Replace with SMTP server
EMAIL_SMTP_PORT = 587  # Replace with the SMTP port (usually 587 for TLS)


def create_rrd():
    """
    Creates an RRD file to store latency data.
    """
    try:
        # Create RRD file with one data source (latency) and a 24-hour archive.
        rrdtool.create(RRD_FILE,
                       "--start", "N",
                       "--step", str(LATENCY_STEP),
                       "DS:latency:GAUGE:600:0:U",  # Data Source: latency (GAUGE type)
                       "RRA:AVERAGE:0.5:1:1440",    # Archive: average over 1 minute, store 1440 points
                       "RRA:AVERAGE:0.5:5:288",     # Archive: average over 5 minutes, store 288 points
                       "RRA:AVERAGE:0.5:30:672")    # Archive: average over 30 minutes, store 672 points
        print("RRD file created successfully.")
    except rrdtool.OperationalError as e:
        print(f"Error creating RRD file: {e}")

def record_latency():
    """
    Records the latency information by pinging the target host and storing it in the RRD file.
    Sends an email if latency surpasses the defined threshold.
    """
    try:
        # Send a ping request to the target host and measure the latency (in milliseconds)
        latency = ping(PING_HOST, timeout=PING_TIMEOUT) * 1000  # Convert to ms

        if latency is None:
            print(f"Ping to {PING_HOST} failed. Latency not recorded.")
            return

        print(f"Latency to {PING_HOST}: {latency:.2f} ms")

        # Store latency data in the RRD file
        rrdtool.update(RRD_FILE, f"N:{latency:.2f}")

        # Check if latency exceeds the threshold and send an email if so
        if latency > LATENCY_THRESHOLD:
            send_alert_email(latency)

    except Exception as e:
        print(f"Error recording latency: {e}")

def send_alert_email(latency):
    """
    Sends an email alert with the latency details and RRD graph if latency exceeds the threshold.
    """
    try:
        # Generate graph for the past 24 hours
        rrdtool.graph(GRAPH_FILE,
                      "--start", "-21600",  # Last 6 hours
                      "--end", "N",         # Until now
                      "--width", str(GRAPH_WIDTH),
                      "--height", str(GRAPH_HEIGHT),
                      "--title", "Latency Over the Last 6 Hours",
                      "--vertical-label", "Latency (ms)",
                      "DEF:latency=" + RRD_FILE + ":latency:AVERAGE",
                      "LINE1:latency#FF0000:Latency")

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"Latency Alert: {latency:.2f} ms Exceeded Threshold"

        # Attach a text message to the email body
        body = f"Alert: The latency to {PING_HOST} has exceeded the threshold of {LATENCY_THRESHOLD} ms.\n\nCurrent Latency: {latency:.2f} ms"
        msg.attach(MIMEText(body, 'plain'))

        # Attach the generated graph image
        with open(GRAPH_FILE, 'rb') as graph_file:
            img = MIMEImage(graph_file.read())
            img.add_header('Content-ID', '<graph>')
            msg.attach(img)

        # Set up the SMTP server and send the email
        with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print(f"Alert email sent to {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"Error sending email: {e}")

def send_exit_email():
    """
    Sends an email notification when the program exits, advising to restart it.
    """
    print(f"Got to exit_email")
    try:
        # Define email server settings for Gmail
        # SMTP_SERVER = "smtp.gmail.com"
        # SMTP_PORT = 465  # Use SSL on port 465 for Gmail SMTP

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = "Script Stopped - Action Required"

        body = "The latency monitoring script has stopped unexpectedly. Please restart the script to ensure continuous monitoring."
        msg.attach(MIMEText(body, 'plain'))

        # Using SSL to securely connect to Gmail's SMTP server
        with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Use app password if 2FA is enabled
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print(f"Exit email sent to {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"Error sending exit email: {e}")

def signal_handler(signal, frame):
    """
    Handles termination signals (Ctrl+C or script exit) to send an exit email.
    """
    send_exit_email()
    sys.exit(0)

def main():
    """
    Main function to create the RRD file, record latency, and generate a graph.
    """
    # Set up signal handler for graceful exit (e.g., Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Check if RRD file exists, if not create it
    if not os.path.exists(RRD_FILE):
        create_rrd()

    # Record latency at regular intervals
    while True:
        record_latency()
        time.sleep(LATENCY_STEP)  # Wait for the next data collection

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        send_exit_email()
    except Exception as e:
        print(f"Unexpected error: {e}")
        send_exit_email()

