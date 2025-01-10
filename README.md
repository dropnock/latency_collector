---

# Latency Monitoring Script

## Description

This script is designed to monitor the network latency to a target host (e.g., Google's public DNS server `8.8.8.8`) at regular intervals, store the data in an RRD (Round Robin Database) file, and generate graphs to visualize the latency over time. 

If latency exceeds a predefined threshold, the script sends an email alert, and if the script is stopped or interrupted, it will send an exit email to notify the responsible team that the monitoring has been interrupted and to restart the script.

### Key Features:
- Regularly ping a specified target host.
- Store latency data in an RRD file.
- Generate graphs showing the latency over time.
- Send email alerts when latency exceeds a threshold.
- Send an email when the script exits, advising the user to restart it for continuous monitoring.

## Prerequisites

Before running the script, you need to install a few prerequisite applications and Python libraries:

### Applications
1. **Python**: Ensure that Python 3.x is installed on your system.
   - Download from: https://www.python.org/downloads/
2. **RRDTool**: A tool for storing time-series data. You need to have `rrdtool` installed to create and update the latency database.
   - Installation on **Linux** (Ubuntu/Debian):
     ```bash
     sudo apt-get install rrdtool
     ```
   - Installation on **macOS** (via Homebrew):
     ```bash
     brew install rrdtool
     ```

### Python Libraries
You need to install the following Python libraries:
- `ping3`: To measure network latency by sending ping requests.
- `rrdtool`: To interact with the RRD database.
- `smtplib` and `email`: Built-in libraries for sending email (no installation required).
- `python-dotenv`: Optional, for securely loading environment variables (e.g., email password).

You can install the necessary Python libraries using `pip`:

```bash
pip install ping3 rrdtool python-dotenv
```

## Configuration

1. **SMTP Server Configuration**: If you're using Gmail as the SMTP server, make sure you use an **App Password** (if 2FA is enabled) and update the following variables in the script:
   - `EMAIL_SENDER`: Your email address (e.g., `your-email@gmail.com`).
   - `EMAIL_PASSWORD`: The password to authenticate with or App Password generated (if 2FA is enabled).
   - `EMAIL_SMTP_SERVER`: Email SMTP server (`smtp.gmail.com`).
   - `EMAIL_SMTP_PORT`: Port for email's SMTP (465 for SSL).

2. **Target Host**: You can specify which host to ping (e.g., `8.8.8.8` or any other IP address). Change the `PING_HOST` variable in the script.

3. **Threshold**: Adjust the `LATENCY_THRESHOLD` variable to set the latency threshold (in milliseconds) that will trigger an email alert.

4. **Environment Variables**: To keep sensitive information secure, consider storing your email password in environment variables. You can use the `python-dotenv` library to load these values from a `.env` file.

### Example `.env` File

```ini
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

Then, in the script, you can load the variables like this:

```python
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
```

## How to Run the Script

1. **Clone the Repository** (or create a new Python file and paste the script content):
   ```bash
   git clone https://github.com/yourusername/latency-monitoring-script.git
   cd latency-monitoring-script
   ```

2. **Set Up the RRD Database**: When the script first runs, it will check if the RRD database file (`latency.rrd`) exists. If not, it will create the RRD file.

3. **Run the Script**:
   ```bash
   python latency_monitor.py
   ```

4. **Stop the Script**: You can stop the script by pressing `Ctrl+C`. The script will then send an exit email to notify the responsible team that the script has stopped unexpectedly.

### Running in the Background
You may want to run the script in the background, especially if you plan to monitor latency over a long period of time.

On **Linux** and **macOS**, you can use `nohup` to run the script in the background:

```bash
nohup python latency_monitor.py &
```

On **Windows**, you can use a task scheduler or a tool like `pythonw` to run the script without a terminal window.

## Script Behavior

- **Latency Monitoring**: The script pings the target host at regular intervals (`LATENCY_STEP` seconds) and records the latency in the RRD database.
- **Graph Generation**: The script generates a graph of the latency over the last 24 hours (`latency_graph.png`) whenever latency exceeds the defined threshold.
- **Alert Email**: If the latency exceeds the threshold (`LATENCY_THRESHOLD`), the script sends an email alert with the graph attached.
- **Exit Notification**: If the script is interrupted or stops unexpectedly, an email is sent notifying the recipient to restart the script.

## Troubleshooting

- **Cannot Send Email**:
  - Ensure you’re user can authenticate and if necessary using an App Password for Gmail if you have 2FA enabled.
  - Double-check your mail credentials and SMTP settings (host: `smtp.gmail.com`, port: `465`).
  - Verify that you have internet connectivity to send the email.

- **RRD File Not Created**:
  - Ensure `rrdtool` is installed and accessible via your command line (`rrdtool --version`).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any issues or feedback, please reach out to:
- Email: your-email@example.com

---

This `README.md` file includes all necessary details to configure and run the latency monitoring script.ncy of a link. It achieves this
