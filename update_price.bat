@echo off

CALL  C:\Users\zianc\Miniconda3\Scripts\activate.bat C:\Users\zianc\Miniconda3\
cd "%OneDriveConsumer%\Garage\MTGOPrice"
python update_price_db.py

echo on 