TITLE SeleniumNode
echo.>> C:\SeleniumGrid\Logs\selenium.log
java -Dwebdriver.ie.driver="C:\SeleniumGrid\EDriverServer.exe" -jar C:\SeleniumGrid\selenium-server-standalone-3.4.0.jar -role node -hub http://10.128.194.170:4444/grid/register/ >> "C:\SeleniumGrid\Logs\selenium.log"
pause
