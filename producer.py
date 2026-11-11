"""dispositivo iot: manda lecturas al broker cada 15-30 s hasta que lo paren."""
import random
import time

from confluent_kafka import Producer

from codec import CODECS
from config import SENSOR_KEY, TOPIC, kafka_config, parse_mode
from sensor import read_sensors

SEND_INTERVAL = (15, 30)


def _on_delivery(err, msg):
    if err:
        print(f"  error al entregar: {err}")
    else:
        print(f"  ok -> topic={msg.topic()} particion={msg.partition()} offset={msg.offset()}")


def main():
    mode = parse_mode("producer de la estacion meteorologica")
    codec = CODECS[mode]
    producer = Producer(kafka_config())
    print(f"producer en modo '{mode}' publicando a topic {TOPIC} (ctrl+c para parar)")
    try:
        while True:
            reading = read_sensors()
            payload = codec.encode(reading)
            print(f"enviando {reading} -> {payload!r} ({len(payload)} bytes)")
            producer.produce(TOPIC, key=SENSOR_KEY, value=payload, on_delivery=_on_delivery)
            producer.flush(10)
            time.sleep(random.uniform(*SEND_INTERVAL))
    except KeyboardInterrupt:
        print("producer detenido")
    finally:
        producer.flush(10)


if __name__ == "__main__":
    main()
