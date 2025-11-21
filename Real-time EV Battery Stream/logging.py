import can
import time
import json
import uuid
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder


ENDPOINT = "Endpoint"
CLIENT_ID = "logger-" + str(uuid.uuid4())
PATH_TO_CERT = "certs/your-device-cert.pem.crt"
PATH_TO_KEY = "certs/your-private-key.pem.key"
PATH_TO_ROOT = "certs/AmazonRootCA1.pem"
TOPIC = "dt/battery_data"

def parse_bms_message(message: can.Message) -> dict:
    message_id = message.arbitration_id
    data = message.data
    decoded_data = {}
    if message_id == 0x101:
        decoded_data = {
            'type': 'bms_heartbeat',
            'soc_percent': data,
            'pack_voltage': int.from_bytes(data[1:3], 'big') * 0.1,
            'pack_current': int.from_bytes(data[3:5], 'big', signed=True) * 0.1
        }
    elif message_id == 0x102:
        decoded_data = {
            'type': 'bms_temperatures',
            'average_temp_c': data,
            'max_cell_temp_c': data,
            'min_cell_temp_c': data
        }
    else:
        return None
    decoded_data['timestamp'] = message.timestamp
    return decoded_data

def main():
    print("Initializing MQTT connection...")
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        client_bootstrap=client_bootstrap,
        ca_filepath=PATH_TO_ROOT,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=6
    )
    print(f"Connecting to {ENDPOINT} with client ID '{CLIENT_ID}'...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("MQTT Connection Successful!")
    print("Starting CAN bus listener...")
    try:
        bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
        print("Successfully connected to the CAN bus.")
        while True:
            message = bus.recv(timeout=1.0)
            if message is None:
                continue

            parsed_data = parse_bms_message(message)
            if parsed_data is not None:
                payload = json.dumps(parsed_data)
                print(f"Publishing: {payload}")
                mqtt_connection.publish(topic=TOPIC, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE)
    except can.CanError as e:
        print(f"Error connecting to or reading from CAN bus: {e}")
    except KeyboardInterrupt:
        print("\nShutting down.")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()

if __name__ == "__main__":
    main()