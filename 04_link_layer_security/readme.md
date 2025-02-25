# Exercises: Link Layer Security

In this and following weeks you will be asked to operate multiple environments simultaneously, such as the guest operating system inside the VM, the host operating system and a mobile device. If it gets a bit overwhelming or setting up your machine fails for some reason, you can always pair up with a colleague.

## Preliminaries: software installation

You should begin by installing required dependencies. If you are completely new to Wireshark, a nice tutorial for beginners can be found [here](https://www.youtube.com/watch?v=TkCSr30UojM).

### Ubuntu 24.04 VM

```
sudo apt install net-tools aircrack-ng dsniff wireshark
```

Wireshark will ask about users without priviledges being able to capture packets, for which you should answer affirmatively. You should also add your user to the group `wireshark` so that no root priviledges are required for sniffing (after adding your user to a new group, you need to logout and login again for the change to apply).

### WSL

At the time of writing, Wireshark or ARP spoofing do not play well with the WSL virtualized network interface. Install native versions of [Wireshark](https://www.wireshark.org/download.html) and an [ARP spoofer](https://github.com/alandau/arpspoof).

### macOS

```
sudo brew install aircrack-ng libpcap libnet
```

You should install Wireshark natively by downloading from the [official website](https://www.wireshark.org/download.html).
Please use this [experimental port](https://github.com/KasperFan/macos-arpspoof) of the `arpspoof` command to Mac OS X.

Please notice that cloning software from a random GitHub repository and running it with root privileges goes against **everything** we teach in this course!

## Preliminaries: scanning the network

There are two access points, with SSIDs `SYSSEC` and `NETSEC`, that you need to find the link layer addresses for.
These two networks have different IP ranges: `192.168.1.0/24` and `192.168.2.0/24`, respectively.
You can find the link layer addresses using your **native** environment by using the commands below.

### GNU/Linux

You can scan the wireless networks by running:

```
iwlist <wifi_interface> scan
```

### macOS

The *deprecated* `airport`command lists the networks
```
sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s
```

### Windows

Apparently, you can scan the wireless networks by running the following command *when disconnected*:

```
netsh wlan show networks mode=bssid
```

## Exercise 1: Dictionary Attack

The first exercise requires breaking into one of the wireless networks available in the classroom by running a dictionary attack.
Both networks are configured to use WPA2-PSK with a **weak** password.

A typical attack starts by placing your network interface in _monitor_ mode, and then capturing traffic from other devices.
For attacking WPA-PSK2, a common approach is to capture the handshake packets when a new device enter the network, or alternatively to force the deauthentication of a device so it connects again and the handshake can be captured.

Because not all interfaces support monitor mode and this functionality is typically not available in Virtual Machines, we already provide packet captures of the handshake for the two access points in this repository, and refer interested readers to [a tutorial](https://www.aircrack-ng.org/doku.php?id=cracking_wpa) for more details.

Find a dictionary of common words in English to run the attack, and to discover the link layer address (MAC) of the access point.
With these informations, you can then run:

```
aircrack-ng -w <dictionary_file> -b <link_layer_address> <packet_capture>
```

You should be able to obtain the correct password after a few minutes of computation.

## Exercise 2: Sniffing the network

One immediate consequence of an attacker having access to traffic in plaintext at the link layer is the natural possibility of capturing sensitive data. This is especially dangerous in wireless networks, since essentially anyone within distance has access to the communication channel.

In this exercise, we will observe how sniffing works in practice. We will take the opportunity to assemble and verify a networking environment for the next exercises in the course, so please check your setup carefully.

### Material

You will need to have the Wireshark tool installed as per the dependencies above.
You will also need to configure your VM network interface to allow all network traffic to be captured inside the VM.

In VirtualBox, you have to change the Network Settings such that my Network Adapter was Attached to a Bridged Adapter. In Advanced, I marked Allow All in the Promiscuous Mode to be able to capture traffic from the host environment inside the VM. The screenshot below shows the settings:

![VirtualBox network configuration](vb-network.png)

### Procedure

We will abstract the Virtual Machine as a hostile node in a wireless network. Although the scenarios are obviously not the same, it should serve the illustration purposes we need here.

1. After the settings are changed, run Wireshark inside the Virtual Machine. You should be able to start a Capture session by clicking directly on the Shark symbol, and all traffic should become immediately visible. Depending on how the network interface driver is [implemented](https://www.virtualbox.org/manual/ch06.html#network_bridged), you might see traffic from the host as well.

2. We can perform more directed sniffing by restricting to a hostname. The _Options_ item under the _Capture_ menu accepts a capture filter that allows one to specify fine-grained traffic capturing rules.
To show how that works, the router runs an HTTP server running in the same network on every IP in the range `192.168.1.2--79` or `192.168.2.2--79`, depending on your network.
Pick one IP address in the range randomly and start a new capture with `host 192.168.X.Y` as the capture filter (replace `X` and `Y` with the actual address).

3. Now access the IP address on the VM machine by typing `http://192.168.X.Y/` in your browser, and you should be able to see the plaintext HTTP traffic in Wireshark. If your VM is able to capture traffic from the host, accessing the website from the host will also show traffic in the VM.

## Exercise 3: ARP Spoofing

We will use a classical ARP Spoofing attack to redirect traffic from a host in the local network to a malicious machine. Traffic redirection is a typical lower-level intermediate step in a higher-level attack such as man-in-the-middle at the network/transport layer. We will play with those in the next weeks, so today we will just focus on the link layer.

1. Setup the VM as instructed in the previous exercise. Notice that this does not allow the VM to capture traffic to/from other machines connected in the same local wireless network.

2. Connect a mobile device to the same wireless network (`SYSSEC` or `NETSEC`) you have your host machine connected. Take note of its IP address and the server you used previously and start again a Wireshark capture within the VM targeting the IP address for the mobile device.

3. Open the address `http://192.168.X.Y/` in your mobile device (smartphone or a friend's computer). You should see the same web page as you saw in the host (the OpenWRT administration page served by the router). If your mobile device has trouble staying in the wireless network without Internet access, try to disable your 3G/4G/5G data connection.

4. Run ARP spoofing to poison the ARP cache of your mobile device (using the `-t` option) with the MAC address of the VM instead of the real server. Replace the interface (mine is `enp0s3`), the victim's IP address (your mobile) and of the server (that you picked randomly) in the command below. Note that the `arpspoof` command takes IP addresses as arguments.

```
$ sudo arpspoof -i <interface> -t <victim> <server>
```
Or in Windows:

```
$ arpspoof.exe --oneway <victim> <server>
```

5. Now generate traffic from the mobile device by logging in with any username/password combination. You should suddenly see the traffic directed to your mobile in Wireshark.
This can include ARP traffic, TCP retransmission attempts and luckily an HTTP POST method sending the username/password.

6. Try a few times if it does not work at the first time, as there is a race condition between the ARP spoofing responses and the real ARP traffic. If successful, you should see the something similar to the screenshot below. It helps if you load the page, then start the ARP spoofing, and then submit the Login form.

![image](https://user-images.githubusercontent.com/5369810/135161121-8879b20a-8ae0-4bb5-abaa-431015ce3351.png)
