# oe-mqtt

OE-MQTT (Opportunistically Encrypted MQTT) is a proof of concept that was completed for my honours project at Carleton University, under Professor David Barrera. Please note that while the code did work at the time of creation, there are several flaws in the design and implementation of this project, and I have not maintained the code base in any way. Changes to the libraries used (for example, AMQTT) may have broken some things. 

For an in depth discussion on the motivation for this project, implementation details, and known weaknesses, please review my project report "Securing MQTT Communications on IoT Devices".

If you are interested in getting my code working for you, read below.

# Installation

The below instructions assume you are using some version of Linux. The project was not developed for Windows or MacOS.

First you'll want to clone this repository, and install the AMQTT and Pycryptodome libraries through pip. When I created this project, I used AMQTT version 0.10.1 and Pycryptodome version 3.15.0. Please note that this was also developed with Python version 3.8.10.

After installing the libraries, you'll need to modify the local install of AMQTT. You can refer to the project report to see exactly what changes I made to the AMQTT library and why.

If you do not already have iptables installed, you'll also need to use your package manager or another method to install iptables. This will depend entirely on your version and distribution of Linux.

Assuming you make it this far, all that's left is to create the firewall rules using iptables. You'll need to create a rule in the NAT table & OUTPUT chain, that matches all packets coming from the IP address of the publisher, and uses the DNAT option to reroute them to the IP address of the encryption proxy. 

You'll need to create an almost identical rule for the packets being sent from the subscriber.

If you're having trouble with this step, please refer to Figures 1.1 & 1.2 in the project report, and don't hesitate to contact me directly.

