create database energyBase;
create user 'user'@'localhost'  identified by 'password';
grant all privileges on energyBase.* to  'user'@'localhost';
FLUSH PRIVILEGES;

USE energyBase; 

create table energyTariffTable (
     timestamp timestamp,
     tariff float
     );

create table energyDayTable (
     timestamp timestamp,
     deliveredToClientHigh float,
     deliveredToClientLow float,
     deliveredByClientHigh float,
     deliveredByClientLow float
     );