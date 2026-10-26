---
title: proxmark
description: Setup Proxmark on Ubuntu
published: true
date: 2026-10-26T14:12:39.085Z
tags: rfid, proxmark
editor: markdown
dateCreated: 2026-02-20T15:01:51.775Z
---

# Setup
Complete Setup Guide for Installing Proxmark3 and RfidResearchGroup Proxmark3 on Ubuntu 22.04
Keep in mind that you can not use both tools at the same time.<br>
This means you have to flash firmware to Proxmark3 every time you change the tool.

## Prerequisites
1. Update and Upgrade System:
```bash
sudo apt update
sudo apt upgrade -y
```
2. Install Required Dependencies:
```bash
sudo apt-get install git ca-certificates build-essential pkg-config libreadline-dev gcc-arm-none-eabi libnewlib-dev qtbase5-dev libbz2-dev libclang-dev libssl-dev
```

## Cloning the Repositories
1. Clone the Proxmark3 Repository:
```bash
mkdir -p ~/git
cd ~/git
git clone https://github.com/Proxmark/proxmark3.git Proxmark_proxmark3
```
2. Clone the RfidResearchGroup Repository:
```
mkdir -p ~/git
cd ~/git
git clone https://github.com/RfidResearchGroup/proxmark3.git RfidResearchGroup_proxmark3
```

## Building the Software
1. For Proxmark3:
```bash
cd ~/git/Proxmark_proxmark3
make clean
make all
```
2. For RfidResearchGroup:
* https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/md/Use_of_Proxmark/4_Advanced-compilation-parameters.md#firmware
* https://medium.com/@jeroenverhaeghe/getting-started-with-the-proxmark-3-easy-888cdda8bca4
```bash
cd ~/git/RfidResearchGroup_proxmark3
make clean PLATFORM=PM3GENERIC
make PLATFORM=PM3GENERIC all # This is for proxmark3 easy
make PLATFORM=PM3OTHER all   # just a hint if you encounter problems when connecting usb after flashing
sudo make install PLATFORM=PM3GENERIC
```

## Setting Up Permissions
1. Add User to Dialout Group:
```bash
sudo usermod -aG dialout $USER
```
2. Setup Access Rights:
```bash
cd ~/git/RfidResearchGroup_proxmark3
make accessrights
```
3. Disable ModemManager (if applicable):
```bash
sudo systemctl stop ModemManager
sudo systemctl disable ModemManager
sudo apt-get remove --purge modemmanager
```
4. udev rules
* `/etc/udev/rules.d/53-proxmark3.rules`
```
# Proxmark3
SUBSYSTEM=="usb", ATTRS{idVendor}=="2d2d", ATTRS{idProduct}=="504d", GROUP="plugdev", MODE="0666"
```

## Flashing the Firmware (RfidResearchGroup Only)
1. Install the Proxmark3 client:
```bash
sudo make install
```
2. Flash the BOOTROM & FULLIMAGE:
```bash
pm3-flash-bootrom
pm3-flash-all
```
3. Button Trick (if flasher can't detect Proxmark3):
Unplug Proxmark3, press and hold the button, plug it into USB, release the button. Two LEDs should stay on.
4. Forcing Flashing if Firmware Mismatch:
```bash
pm3-flash-all --force
```

## Running the Client
1. Connect the Proxmark3 device to your computer.
2. Run the Client:
- For Proxmark3:
```bash
cd ~/git/Proxmark_proxmark3/client
./proxmark3 /dev/ttyACM0
```
- For RfidResearchGroup:
```bash
cd ~/git/RfidResearchGroup_proxmark3/client
./pm3
```

## Using Proxmark3 Tools

### Basic Operations
1. Scan for Tags:
```bash
hf search
```
2. Read Tag Data:
```bash
hf mf dump
```
3. Write Data to Tag:
```bash
hf mf wrbl -b 1 -d 112233445566
```
4. Clone a Tag:
```bash
hf mf cload -f mydump.mfd
```

### Emulating Tags
1. Emulate a Tag:
```bash
hf 14a sim -u
```
2. Replay Attacks:
```bash
hf 14a snoop
hf 14a list
```

### Analyzing Communication
1. Sniff Communication:
```bash
hf 14a snoop
```
2. Analyze Captured Data:
```bash
hf list 14a reader
```

### Security Testing
1. Brute Force Attacks:
```bash
hf mf hardnested
```
2. Exploit Vulnerabilities:
```bash
hf mf mifare
```
## Lua Scripts for Automation
1. `loop_hf_payment_scan.lua`
```lua
function sleep(n)
    os.execute("sleep " .. tonumber(n))
end

while true do
    -- Run the hf search command
    local result = core.console('hf search')

    -- Check if the result is not nil
    if result then
        -- Check the result for known contactless payment card types
        if string.match(result, "Visa") or
           string.match(result, "Mastercard") or
           string.match(result, "American Express") or
           string.match(result, "Apple Pay") or
           string.match(result, "Google Pay") or
           string.match(result, "Samsung Pay") then
           print("Contactless payment card detected:")
           print(result)
        else
           print("No known contactless payment card detected")
        end
    else
        print("No result from hf search command")
    end

    -- Delay between each search (1 second)
    sleep(1)
end
```

2. loop_hf_search.lua
```lua
function sleep(n)
    os.execute("sleep " .. tonumber(n))
end

while true do
    -- Run the hf search command
    core.console('hf search')

    -- Delay between each search (1 second)
    sleep(1)
end
```

## References
- [Proxmark3 GitHub Repository](https://github.com/Proxmark/proxmark3)<br>
- [RfidResearchGroup GitHub Repository](https://github.com/RfidResearchGroup/proxmark3)<br>
- [RfidResearchGroup Compilation Instructions](https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/md/Use_of_Proxmark/0_Compilation-Instructions.md)