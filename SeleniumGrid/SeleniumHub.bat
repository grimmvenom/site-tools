TITLE SeleniumHub
echo.>> C:\SeleniumGrid\Logs\selenium.log
java -Dwebdriver.ie.driver="C:\SeleniumGrid\IEDriverServer.exe" -jar C:\SeleniumGrid\selenium-server-standalone-3.4.0.jar -role hub >> "C:\SeleniumGrid\Logs\selenium.log"
pause
