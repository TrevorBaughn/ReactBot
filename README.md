# InnocentBot
The most innocent Discord bot.

# What is it?
     InnocentBot is a Discord bot that follows my musings.  It has been made to be able to do all sorts of things through the power of networking and the Discord bot API.
Right now, it's functionality is:

-It can tase people.

# Taser Functionality
`|shock <target> <shock_length>`

      The taser functionality is only possible if the Raspberry Pi on the client side has a taser set up. Taking the syntax above into account, the `target` is the person with the client, while the `shock_length` is the amount of time in hundreds of milliseconds to tase them for, maxing out at 500 milliseconds.

# How to set up your own
<h1> Host </h1>

1. Set up an internet connection and forward a port on a Raspberry Pi

2. Clone the repository into your desired directory onto the Pi

3. Be sure the Pi has Python 3.8+

4. Remove "EXAMPLE" from "EXAMPLEconfig.ini" and fill out the ini file

5. Run HostLauncher.py

<h1> Client </h1>

1. Set up an internet connection and forward a port on a Raspberry Pi

2. Do some other shit SprusedGoose knows what to do on the hardware end

3. Clone the repository into your desired directory onto the Pi

4. Be sure the Pi has Python 3.8+

5. Remove "EXAMPLE" from "EXAMPLEconfig.ini" and fill out the ini file

6. Run ClientLauncher.py
