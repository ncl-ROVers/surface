# surface
Surface code 2020-21

Setting the static ip

On the Ubuntu Desktop
Note: This is for Ubuntu desktop. The interface for Mate may be different

On the computer, which is connected to the Internet, click the network icon in the panel and go to "Edit Connections..." at the bottom of the menu.

Edit Connection...

Double click your Wired Connection (Leave your wireless connection untouched, the one connected to Internet and the one you want to share, as I understand).

Network Connections Dialog

On the "IPv4 Settings tab", select Method: "Shared to other computers"

Editing Wired Connection

Reconnect by clicking on the Wired Network, so it gets a new IP address. (The two computers must be connected by an ethernet cable for this step, so connect them now if you haven't already.)

Click on "Connection Information" in the network menu and write down the IP address and network mask (in my case it was assigned 10.42.0.1/255.255.255.0 but I do not know if that will always be the case).

Connection Information

On the Raspberry Pi
Assign static IP to the Ethernet connection

In Pi the WiFi device is called wlan but the ethernet device name is hard to guess. To find the device names use the command:

$ ip link show

The output will show your Ethernet device in Pi enxb827eb3d64cc

Next we need to find the current IP addresses assigned to enxb827eb3d64cc:

$ ip -4 addr show dev enxb827eb3d64cc | grep inet

I get something like this, yours may be different:

inet 10.42.0.211/24 brd 10.42.0.255 scope global enxb827eb3d64cc
You can keep the assigned IP address or choose a different one in the same subnet. Add the following lines at the end of /etc/dhcpcd.conf by:

$ sudo nano /etc/dhcpcd.conf

With the following content to make the assigned IP address static:

# Custom static IP address for enxb827eb3d64cc
interface enxb827eb3d64cc
static ip_address=10.42.0.211/24
static routers=10.42.0.255
static domain_name_servers=10.42.0.255
Change 10.42.0.211 above to 10.42.0.x where x is a number between 2 and 254 if you want to assign a different IP address.

Reboot Pi to make the new IP address take effect:

$ sudo reboot now

Now you should be able to ssh from the desktop to the Pi with the following command:

$ ssh pi@10.42.0.211
Hope this helps