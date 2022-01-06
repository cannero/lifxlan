''' Set lights for day/night '''
import argparse
import yaml
from lifxlan import LifxLAN, RGBtoHSBK

DURATION = 2000
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument('setting', help='the setting to use for the lights', nargs='?')
    group.add_argument('-l', '--list-settings', help='the setting to use for the lights',
                       action='store_true', dest='list_settings')
    group.add_argument('-c', '--set_color', help='set the color for a light, "name hue saturation lightness kelvin"',
                       nargs=5, dest='set_color')
    group.add_argument('--rgb', help='display HSL for RGB',
                       nargs=3)

    return parser.parse_args()

def set_color(args, config, lights):
    name, *hslk = args.set_color
    if name not in config[LIGHTS_KEY][MAC_ADDRESSES_KEY]:
        print(f'unknown light "{name}"')
        return -1
    mac = config[LIGHTS_KEY][MAC_ADDRESSES_KEY][name]
    light = next((l for l in lights if l.get_mac_addr() == mac), None)
    if light is None:
        print(f'mac {mac} not found')
        return -1
    light.set_color(hslk, DURATION)
    return 0

def get_hsl_color(args):
    r, g, b = args.rgb
    print(RGBtoHSBK([int(r), int(g), int(b)]))
    return 0

def main():
    config = read_yaml(SETTINGS_FILENAME)
    args = parse_args()

    if args.list_settings:
        print(list(config[SETTINGS_KEY].keys()))
        return 0

    if args.rgb is not None:
        return get_hsl_color(args)

    mac_lookup = build_mac_lookup(config)
    get_light_name = get_name_from_mac(mac_lookup)
    num_lights = len(config[LIGHTS_KEY][MAC_ADDRESSES_KEY])
    lifx = LifxLAN(num_lights)
    lights = lifx.get_lights()

    read_out_lights(lifx, get_light_name)

    if args.set_color is not None:
        return set_color(args, config, lights)

    settings = config[SETTINGS_KEY]
    if args.setting not in settings:
        print(f"UNKNOWN SETTING {args.setting}")
        print("=================================")
        return 0

    colors = settings[args.setting]
    for light in lights:
        light_name = get_light_name(light.get_mac_addr())
        if light_name not in colors:
            print(f"light not configured {light_name}")
            continue
        light.set_color(colors[light_name], duration=DURATION)
    return 0

if __name__ == '__main__':
    main()
