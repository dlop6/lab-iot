"""consumer: lee el topic desde el inicio y grafica la telemetria en vivo."""
from datetime import datetime

from confluent_kafka import Consumer

from codec import CODECS
from config import TOPIC, kafka_config, parse_mode
from plot import LivePlot

POLL_TIMEOUT = 0.5
BATCH_SIZE = 100


def _build_consumer(mode: str) -> Consumer:
    return Consumer({
        **kafka_config(),
        "group.id": f"{TOPIC}-{mode}-plot",
        # sin commit siempre arranca del inicio, asi se grafica lo pasado y lo nuevo
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })


def main():
    mode = parse_mode("consumer de la estacion meteorologica")
    codec = CODECS[mode]
    consumer = _build_consumer(mode)
    consumer.subscribe([TOPIC])
    plot = LivePlot(f"estacion meteorologica - topic {TOPIC} - modo {mode}")
    print(f"consumer en modo '{mode}' escuchando topic {TOPIC} (cerrar la grafica para parar)")
    try:
        while plot.is_open():
            messages = consumer.consume(BATCH_SIZE, POLL_TIMEOUT)
            for msg in messages:
                if msg.error():
                    print(f"error de kafka: {msg.error()}")
                    continue
                try:
                    reading = codec.decode(msg.value())
                except ValueError as exc:
                    # en el topic pueden quedar mensajes del otro modo
                    print(f"ignorado offset {msg.offset()}: {exc}")
                    continue
                when = datetime.fromtimestamp(msg.timestamp()[1] / 1000)
                print(f"recibido offset={msg.offset()} {msg.value()!r} -> {reading}")
                plot.add(when, reading)
            if messages:
                plot.render()
            plot.wait(0.1)
    except KeyboardInterrupt:
        print("consumer detenido")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
