# Power-Optimizations
Adjusts screen brightness and power mode based on battery level and state. Also allows manual bypass

This is meant for Linux Mint, specifically the cinnamon desktop. Full compatibility is not guaranteed with other distros or desktop enviroments!!! if it uses UPower it should work.
Linux Mint 22.3 with Cinnamon 6.6 - works flawlessly
CachyOS 260809 with KDE Plasma 6.8 - works flawlessly
if you are not sure UPower is installed, it should be in your distro's official repository.

# Installation
This is a general section on how to install it. The process is very simple (and not super strict)! ! !

REQUIRED: 
1) download power-plan.py
2) move it into ~/.local/bin (or another folder if you prefer)
3) create "~/.local/cache" if it doesnt exist already
4) download brightnessctl. Ubuntu/Debian: "sudo apt install brightnessctl", Arch: "sudo pacman -S brightnessctl:, Fedora: "sudo dnf install brightnessctl"
5) add the user into the video group so it can use brightnessctl without sudo. "sudo usermod -aG video $USER". requires a restart to take effect

two different ways from here

#1 - chmod: 
    i) run chmod +x ~/.local/bin/power-plan.py (or where ever else you have it)
    ii) add it to startup applications so it starts with your system
    
#2 - python 3:
    i) add as a custom command in startup applications. The command is python3 ~/.local/bin/power-plan.py (or where ever else you have it)


# How to Customize
It is really simple! 
add what percentage you want it to dim to after the battery gets low. the battery threshold can also be edited. max brightness is automatically retrieved

# Last Comments
Please credit me if you use my code for something. Personal use does not require it. Do not used in closed source projects as per the GNU v2.0 license. Any ideas on how to improve or any bug reports would be appreciated! you can also fix them for yourself if you like.
