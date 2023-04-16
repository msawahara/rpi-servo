import sys
from time import sleep
from typing import NamedTuple
import yaml

from adafruit_motor.servo import Servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

class ConfigProfile(NamedTuple):
    on: int
    off: int

class ConfigPort(NamedTuple):
    profile: str
    offset: int

class Config(NamedTuple):
    profile: dict[str, ConfigProfile]
    port: dict[int, ConfigPort]

def load_config(path: str) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)

    profiles = {str(k): ConfigProfile(**{"on" if k2 else "off": int(v2) for k2, v2 in v.items()}) for k, v in data["profile"].items()}
    ports = {int(k): ConfigPort(**v) for k, v in data["port"].items()}
    return Config(profile=profiles, port=ports)

def main(argv: list[str]) -> None:
    config = load_config("config.yaml")

    if len(argv) < 3:
        print("error: arg")
        exit(1)
    
    action = argv[1]
    if argv[2] == "all":
        targets = list(config.port.keys())
    else:
        targets = list(map(int, argv[2].split(","))) 
    if len(argv) > 3:
        push_time = float(argv[3])
    else:
        push_time = None

    if action == "push" and push_time is None:
        print("error: need push_time")
        exit(1) 

    # Initalize PCA9685
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    servos = {ch: Servo(pca.channels[ch]) for ch in targets}

    for ch, srv in servos.items():
        port_config = config.port[ch]
        profile = config.profile[port_config.profile]

        if action == "push":
            srv.angle = profile.on + port_config.offset
            sleep(push_time)

        if action == "push" or action == "init":
            srv.angle = profile.off + port_config.offset
            sleep(1)

        srv.angle = None
    pca.deinit()

main(sys.argv)
