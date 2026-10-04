import random
import json
from datetime import datetime


class IoTDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.status = "ONLINE"

    def generate_sensor_data(self):
        temperature = round(random.uniform(20.0, 35.0), 2)
        humidity = round(random.uniform(40.0, 80.0), 2)

        sensor_data = {
            "device_id": self.device_id,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": datetime.now().isoformat(),
            "status": self.status
        }

        return sensor_data


if __name__ == "__main__":
    print("======================================")
    print("      Secure IoT Device Simulator")
    print("======================================")

    device = IoTDevice("IOT-001")

    print("\nDevice ID:", device.device_id)
    print("Device Status:", device.status)

    sensor_data = device.generate_sensor_data()

    print("\nGenerated Sensor Data:")
    print(json.dumps(sensor_data, indent=4))