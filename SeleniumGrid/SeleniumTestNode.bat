TITLE TestNode
java -Dwebdriver.ie.driver="C:\SeleniumTestGrid\IEDriverServer.exe" -jar C:\SeleniumTestGrid\selenium-server-standalone-3.4.0.jar -role node -hub http://10.128.194.172:4444/grid/register/ -hubPort 4444 -log "C:\SeleniumTestGrid\Logs\TestNode.log" -id TestHub
pause
