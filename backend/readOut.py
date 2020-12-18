#!usr/bin/python
#Kaifa   MA304C  3-fase kleinverbruik    RJ-11, 6-pins   DSMR 4.2.2  115200 8N1? Ja? /KFM5
#http://domoticx.com/p1-poort-slimme-meter-hardware/
# python /var/DRIVE/share/SmartMeterReadOut/SerialReadOut.py
import sys
import serial
import mysql.connector
import datetime
import traceback
import logging


# initialise logging
logging.basicConfig(filename='SerialReadOut.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.error("test")


#Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize=serial.SEVENBITS
ser.parity=serial.PARITY_EVEN
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=1
ser.rtscts=0
ser.timeout=20
ser.port="/dev/ttyUSB0"

#Open COM port
while True:
    try:
        ser.open()
        print("port opened")
    except Exception as e:
        logging.error(str(e))
    try:
        mydb = mysql.connector.connect(
      host="localhost",
      user="user",
      passwd="password",
      database="database",
      buffered=True
    )
        mycursor = mydb.cursor()
    except Exeption as e:
        logging.error(str(e))

    try:
        timeStamp = datetime.datetime.now()

        while True:
            tariffHigh = 0
            tariffLow = 0
            deliveredToClientHigh = 0
            deliveredToClientLow = 0
            deliveredByClientHigh = 0
            deliveredByClientLow = 0
            avgTariffSum = 0
            avgTariffCount = 0
            while True:
                p1_raw = ser.readline()
                message = str(p1_raw)
                if "1-0:1.8.1" in message:
                    deliveredToClientHigh = message[11:-7]
                    #print( deliveredToClientHigh)
                if "1-0:1.8.2" in message:
                    deliveredToClientLow = message[11:-7]
                    #print( deliveredToClientLow)
                if "1-0:2.8.1" in message:
                    deliveredByClientHigh = message[11:-7]
                    #print( deliveredByClientHigh)
                if "1-0:2.8.2" in message:
                    deliveredByClientLow = message[11:-7]
                    #print( deliveredByClientLow)
                if "1-0:1.7.0" in message:
                    tariffHigh = message[11:-6]
                    #print( tariffHigh)
                if "1-0:2.7.0" in message:
                    tariffLow = message[11:-6]
                    #print( tariffLow)
                    break
            #end
            
            # Calculate AVG of a period.
            tariff = float(tariffHigh) - float(tariffLow)
            avgTariffCount += 1
            avgTariffSum += tariff

            # Write current power to a file, so that the website can show this real time.
            file = open("/var/www/html/energieVerbruik/currentPower", 'w')
            file.write(str(tariff))
            file.close()

            # Inserte every five minutes the the AVG power. 
            if timeStamp + datetime.timedelta(minutes=5) <= datetime.datetime.now():
                print( "wil be inserted")

                avgTariff = avgTariffSum / avgTariffCount
                sql = "insert into energyTariffTable (timestamp, tariff) values (%s, %s)"
                val = (timeStamp.isoformat(), avgTariff)
                mycursor.execute(sql, val )
                avgTariffCount = 0
                avgTariffSum = 0
                timeStamp = datetime.datetime.now()
                mydb.commit()

                print(avgTariff)
            

            sql = "SELECT * FROM energyDayTable WHERE timestamp BETWEEN %s and %s"
            today = timeStamp.date().isoformat()
            arg = (today+" 00:00:00",today+" 23:59:59")
            mycursor.execute(sql, arg)
            result = mycursor.fetchone()
            #print result
            if result == None:
                sql = "insert into energyDayTable (timestamp,  deliveredToClientHigh, deliveredToClientLow, deliveredByClientHigh, deliveredByClientLow) values (%s, %s, %s, %s, %s)"
                val = (timeStamp.isoformat(), float(deliveredToClientHigh), float(deliveredToClientLow), float(deliveredByClientHigh), float(deliveredByClientLow))
                mycursor.execute(sql, val)
                mydb.commit()
    # Log the exceptions.            
    except Exception as e:
        logging.error(str(e))
        traceback.print_exc()