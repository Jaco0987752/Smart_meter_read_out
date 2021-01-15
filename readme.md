Smart meter read out
===================
This application helps to take control over your energy usage!
---------------------------------------------------------------

Install the application in the following steps.
Made for khalifa 

necessarily stuff
--------------------

- raspberry pi and supply.
- SD card 16 gb or larger.
- connection cable from usb to smart meter output.

Preparations
-------------
- Install a web server like apache, including a php interpretor. Install a sql server like mySQl or mariaDB. I recommend that you this by installing 'xaml', this is a all in package and it will make the installation much simpler.
- Install python3.
- Download the source code.
- Create the database using the 'makeDatabase' script, replace the default creditionals with yours.
- Connect the Raspberry pi to the serial port of smart meter. Check if the serialport given in the 'readout.py' is the the same as the port on your system.
- Replace the defaults database credentials with yours.  
- Try to run the script with the python interpretater. If it print meaningful messages on the console, and on error messages, then it is okey. It can be useful to create a systemd service which runs the 'readout.py' script, so that is starts up automatically after a system reboot.

- Move the folder SmartMeterReadOut to the webroot, to make it accessible. And replace in the file 'getData.php', the defaults of the connection string with your sql creditional.

To test the system, go to your browser on your raspberry pi, and type "http://localhost/SmartMeterReadOut"

Working of the system
-----------------------
The code exists of three parts:

- The python that gathers the messages from the smartmeter. It decodes the messages and, and saves the information in the database that is running on the raspberry pi.  
- The backend script thats runs on the server, which gathers the information from the database. It runs when a client querries some information specified in the parameters. It sents a JSON object with the information to the client.
- The frontend javascript that is inbedded in the html. This code runs when the website is loading and on user demand. It draws a graph using a external library. 