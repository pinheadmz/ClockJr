# The Bitcoin Block Clock -- JUNIOR!

Raspberry Pi Zero full node with 40 multicolor LED circular visualizer and 1.3" display screen

(see the original, bigger Bitcoin Block Clock here: https://github.com/pinheadmz/ClockBlocker) 

### Dependencies:

* bcoin: https://github.com/bcoin-org/bcoin

* Adafruit GPIO and SSD1306 drivers: https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/usage?view=all#dependencies

* Raspberry Pi NeoPixel support: https://learn.adafruit.com/neopixels-on-raspberry-pi?view=all#compile-and-install-rpi-ws281x-library

* Apache and PHP (for the local web interface): https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md

### Installation:

Clone this repository:

`$ git clone https://github.com/pinheadmz/ClockJr.git`

Add this line to /etc/rc.local to run ClockJr on startup and direct output to log file:

`sudo /home/pi/clockjr/startclock.sh  `

Run this command to link the included PHP script to the web root directory:

`ln -s ~/clockjr/clockjrwww.php /var/www/html/index.php`

NOTE: To use SPV mode (default) a small patch is recommended in the bcoin source to print coinbase scriptSigs to disk so the Clock Jr script can retrive them:

https://github.com/pinheadmz/bcoin/commit/b65e499533b2b8507cd5be9bfbf853fa674abede

### Hardware:
Here's a "wishlist" I made on Adafruit (accepts Bitcoin!) with most the components I used for the build:

https://www.adafruit.com/wishlists/424551

Here's the lucite case I'm using as a project enclosure:

https://www.containerstore.com/s/acrylic-hockey-puck-premium-display-cube/d?productId=11004068&q=hockey%20puck
