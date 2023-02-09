## What is this?
A personal project to simulate an [EPever](https://www.epever.com/) Tracer solar charge controller to assist in developing a Modbus integration against it without having the charger to hand.

You'll probably know if this is what you're looking for, but in particular it is _not_ a client for talking to EPever chargers, there are other Python projects that seek to do that:

 - [epevermodbus](https://github.com/rosswarren/epevermodbus)
 - [python-modbus-epever-xtra](https://github.com/plopp/python-modbus-epever-xtra)

... and probably others.

The data in it is static in the current implementation, you have to restart the program to pick up any changes you make (in the code).

## Is it complete?
No. I only implemented the registers I wanted to access, so large blocks of registers aren't present and some registers (like the bitmask ones) aren't set to sensible values. Feel free to improve it and send me a PR!

## Why is it implemented this way?
I started out trying to use the [pymodbus simulation system](https://pymodbus.readthedocs.io/en/latest/source/library/simulator/simulator.html) (which uses JSON files), but I couldn't make it work. It appeared to be at quite an early stage of development at the point where I built this. Possibly it's good enough by now. This seemed an easy enough way to do it.

## License
BSD 2-Clause.
