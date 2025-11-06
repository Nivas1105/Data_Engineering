echo "Starting CAN data simulation..."

while true; do
    echo "Sending NORMAL temperature reading (35°C)..."
    cansend vcan0 102#2326200000000000
    sleep 5

    echo "Sending HIGH temperature reading (64°C)..."
    cansend vcan0 102#4042380000000000
    sleep 5
done