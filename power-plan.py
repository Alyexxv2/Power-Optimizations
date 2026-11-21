#!/usr/bin/env python3
import subprocess
import gi
import os
from gi.repository import Gio, GLib

dimmed = False # to allow manual brightness override and recovery of saved brightness
max_brightness = int(subprocess.check_output(["brightnessctl", "max"], text=True)) # gets max brightness of screen
desired_dim = 0.25 # set to desired dim level as a decimal. (1% = 0.01)
battery_thresthold = 30 #set to what you define low battery is. should be a percent as a whole number (1% = 1)
saved_brightness_path = os.path.expanduser("~/.local/cache/saved-brightness.txt") # saved brightness file path. if ~/.local/cache doesn't exist, the saved brightness will not function.
saved_brightness = str(max_brightness * 2/3) # default brightness if no saved value is found
warned = False # prevent repeat low battery warnings
last_change = None # to allow manual bypass in the power settings. i.e., wont override power plan if has already been changed to the target. will make bypass = True
bypass = False # allow manual override of power plan

def set_power_profile(on_battery, battery_percentage):
    global dimmed
    global warned
    global saved_brightness
    global last_change
    global bypass
    try: #try to read the saved brightness value from the file, if it exists
        with open(saved_brightness_path, "r", encoding="utf-8") as f:
            saved_brightness = f.read().strip()
    except Exception as e:
        print(f"Error reading saved brightness: {e}")
    # Choose power mode based on battery status
    if on_battery and battery_percentage > battery_thresthold: # just on battery. balanced mode
        if dimmed:
            subprocess.run(["brightnessctl", "set", saved_brightness], check=True) # recovers saved brightness
        dimmed = False
        warned = False
        if not last_change == "on_battery": #checks to see if it already changed the power mode. allows bypassing if not.
            last_change = "on_battery"
            target_profile = "balanced" #sets target profile
            bypass = False
        else:
            bypass = True
    elif not on_battery: # plugged in. performance mode since battery will not drain
        if dimmed:
            subprocess.run(["brightnessctl", "set", saved_brightness], check=True)
        dimmed = False
        warned = False
        if not last_change == "charging":
            last_change = "charging"
            target_profile = "performance"
            bypass = False
        else:
            bypass = True
    else: # low battery. power-saver mode and dimmed screen
        if not dimmed:
            saved_brightness = subprocess.check_output(["brightnessctl", "get"], text=True).strip()
            try:
                with open(saved_brightness_path, "w", encoding="utf-8") as f:
                    f.write(saved_brightness)
            except Exception as e:
                print(f"Failed to save brightness to file. value: {e}")
            dimmed = True
            if not int(saved_brightness) < max_brightness * desired_dim: # will not brighten screen if it is already lower than 25% brightness
                subprocess.run(["brightnessctl", "set", str(max_brightness * desired_dim)], check=True)
            if not warned:
                subprocess.run(["notify-send", "-u", "normal", "Battery low (30%). Plug in your charger."], check = True)
                warned = True
        if not last_change == "low_battery":
            last_change = "low_battery"
            target_profile = "power-saver"
            bypass = False
        else:
            bypass = True

    try:
        # Check the current mode first so we don't run unnecessary commands
        current = subprocess.check_output(
            ["powerprofilesctl", "get"],
            text=True
        ).strip()

        if not bypass and current != target_profile: # if the target profile is actually different and hasnt been changed yet, change to target profile
            subprocess.run(["powerprofilesctl", "set", target_profile], check=True)
            print(f"Switched power profile to: {target_profile}")
    except Exception as e:
        print(f"Failed to switch power profile: {e}")

def check_battery_state(upower_proxy, battery_proxy):
    # Read the current OnBattery and Percentage property from UPower right when the script starts or when either changes
    on_battery_variant = upower_proxy.get_cached_property("OnBattery")
    battery_percentage = battery_proxy.get_cached_property("Percentage")
    if on_battery_variant is not None and battery_percentage is not None:
        set_power_profile(on_battery_variant.unpack(), battery_percentage.unpack())

def update_battery_status(proxy, changed_properties, invalidated_properties):
    # Convert the GLib dictionary into a normal Python dictionary
    props = changed_properties.unpack()
    # Only react if the OnBattery or Percentage property was part of this change event
    if "OnBattery" in props or "Percentage" in props:
        check_battery_state(upower_proxy, battery_proxy)

# Connect to the system D-Bus and create a proxy for UPower
system_bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
upower_proxy = Gio.DBusProxy.new_sync(
    system_bus,
    Gio.DBusProxyFlags.NONE,
    None,
    "org.freedesktop.UPower",
    "/org/freedesktop/UPower",
    "org.freedesktop.UPower",
    None
)

#Create another proxy relating to battery levels
battery_proxy = Gio.DBusProxy.new_sync(
    system_bus,
    Gio.DBusProxyFlags.NONE,
    None,
    "org.freedesktop.UPower",
    "/org/freedesktop/UPower/devices/DisplayDevice",
    "org.freedesktop.UPower.Device",
    None
)
# Listen for hardware power changes from UPower
upower_proxy.connect("g-properties-changed", update_battery_status)
battery_proxy.connect("g-properties-changed", update_battery_status)

# Update immediately on startup, then wait for charger events
check_battery_state(upower_proxy, battery_proxy)
GLib.MainLoop().run()
