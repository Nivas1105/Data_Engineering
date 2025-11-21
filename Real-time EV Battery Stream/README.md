# Real-time EV Battery Telemetry & Alerting Pipeline

This project is a complete, end-to-end data pipeline that simulates the acquisition, processing, and monitoring of data from an Electric Vehicle's Battery Management System (BMS). It demonstrates a professional workflow using modern data engineering principles, containerization, and cloud-native services.

The pipeline ingests raw CAN bus data, transforms it into a structured format, streams it securely to the AWS cloud, and triggers real-time alerts for critical events like over-temperature conditions.

---

### Architecture Diagram

```
[CAN Data Simulator] ---> [Docker Container on EC2] ---> [AWS IoT Core] ---> [AWS IoT Rule] ---> [AWS SNS] ---> [Email Alert]
      (vcan)                 (Python ETL)                (MQTT Broker)       (Filter: temp > 60)   (Notification)
```


---

### Features

*   **Real-time Streaming:** Ingests and processes data with sub-second latency from the source to the cloud.
*   **ETL Processing:** Transforms raw, cryptic hexadecimal CAN bus data into a structured, human-readable JSON format.
*   **Containerized:** The entire application is packaged with Docker, ensuring a consistent and portable deployment environment.
*   **Cloud-Native:** Built entirely on scalable and managed AWS services (EC2, IoT Core, SNS).
*   **Serverless Alerting:** Uses an AWS IoT Rule and SNS to create an efficient, event-driven alerting system that requires zero server management.

---

### Technology Stack

*   **Cloud / DevOps:** AWS (EC2, IoT Core, SNS), Docker
*   **Languages & Libraries:** Python, awsiotsdk, python-can
*   **Protocols & Formats:** CAN bus, MQTT, JSON
*   **Platform:** Linux (Ubuntu 22.04)

---

### Setup & Deployment

**1. AWS Prerequisites:**
*   An AWS account with an IAM user and programmatic access.
*   **AWS IoT Core Setup:**
    *   Create an IoT "Thing" for your device.
    *   Create a "Policy" allowing the device to connect and publish.
    *   Download the **Device Certificate**, **Private Key**, and **Amazon Root CA 1** file.
*   **AWS SNS Setup:**
    *   Create an SNS Topic (e.g., `battery_alerts`).
    *   Create an email subscription to that topic and confirm it in your inbox.

**2. Configure the Application:**
*   Clone this repository to your EC2 instance or local development environment.
*   Place your three downloaded credential files (`-certificate.pem.crt`, `-private.pem.key`, `AmazonRootCA1.pem`) into the `certs/` directory.
*   Open `logging.py` and update the following configuration variables at the top of the file with your specific values:
    *   `ENDPOINT`: Your unique AWS IoT Core endpoint.
    *   `PATH_TO_CERT`: The exact filename of your device certificate.
    *   `PATH_TO_KEY`: The exact filename of your private key.

**3. Build and Run the Container:**
*   From the root of the project directory, build the Docker image:
    ```bash
    docker build -t logger:2.0 .
    ```
*   Run the container. The `--network=host` flag is required for it to access the host's `vcan0` interface.
    ```bash
    docker run -it --rm --network=host logger:2.0
    ```

**4. Start the Simulation:**
*   In a separate terminal, make the simulation script executable:
    ```bash
    chmod +x signal.sh
    ```
*   Run the script to start generating test data. This script will send a normal temperature reading, wait 5 seconds, and then send a high-temperature reading.
    ```bash
    ./scripts/signal.sh
    ```

---

### How to Test

1.  In the AWS IoT Core Console, navigate to the **MQTT test client**.
2.  Subscribe to the topic `dt/battery_data`.
3.  Run the container and the simulation script.
4.  You will see both the normal and high-temperature messages appear in the MQTT client.
5.  Check your email. You should receive an alert containing the JSON payload for the high-temperature message, proving the entire pipeline and alerting rule works.