''' Set lights for day/night '''
import argparse
import yaml
from lifxlan import LifxLAN

# yaml parameters
LIGHTS_KEY = 'lights'
MAC_ADDRESSES_KEY = 'macs'
SETTINGS_KEY = 'settings'
SETTINGS_FILENAME = 'settings.yaml'

def get_name_from_mac(mac_lookup):
    def get_name(mac):
        if mac in mac_lookup:
            return mac_lookup[mac]
        return f"unknown {mac}"
    return get_name

def read_out_lights(lifx, get_name):
    print("power:")
    for light, power in lifx.get_power_all_lights().items():
        print("\t", get_name(light.mac_addr), min(power, 1))

    print("color:")
    for light, color in lifx.get_color_all_lights().items():
        print("\t", get_name(light.mac_addr), color)

def get_stand_daylight():
    hue = 65535
    saturation = 65535
    brightness = 65535//2
    kelvin = 5000
    return [hue, saturation, brightness, kelvin]

def read_yaml(file_path):
    with open(file_path, "r") as y_f:
        return yaml.safe_load(y_f)

def build_mac_lookup(config):
    return {v:k for k, v in config[LIGHTS_KEY][MAC_ADDRESSES_KEY].items()}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('setting', help='the setting to use for the lights')
    return parser.parse_args()

def main():
    config = read_yaml(SETTINGS_FILENAME)
    args = parse_args()

    mac_lookup = build_mac_lookup(config)
    get_light_name = get_name_from_mac(mac_lookup)
    num_lights = len(config[LIGHTS_KEY][MAC_ADDRESSES_KEY])
    lifx = LifxLAN(num_lights)
    lights = lifx.get_lights()

    read_out_lights(lifx, get_light_name)

    settings = config[SETTINGS_KEY]
    if args.setting not in settings:
        print(f"UNKNOWN SETTING {args.setting}")
        print("=================================")
        return

    colors = settings[args.setting]
    duration = 2000
    for light in lights:
        light_name = get_light_name(light.get_mac_addr())
        if light_name not in colors:
            print(f"light not configured {light_name}")
            continue
        light.set_color(colors[light_name], duration=duration)

if __name__ == '__main__':
    main()
