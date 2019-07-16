<#	
	.NOTES
	===========================================================================
	 Selenium Log Rotation
	 Environment:   Selenium Nodes
	 Created on:   	7-17-17
     Authored By:   Nick Serra	

     1. Stop SeleniumNode Process
     2. Rename Selenium.log -> Selenium-$Date.log
     3. Start SeleniumNode Process
	===========================================================================
	
#>

# Grabs the Path from relative location where script is executed from
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$ParentDir = Split-Path -Path $ScriptDir -Parent
Write-Host "Script Directory is: $ScriptDir"

# Formatted Date
$Date = (Get-Date).ToString("MM-dd-yyyy")
# Formatted Time
$Time = (Get-Date).ToString("HH_mm")

function Selenium-Process-Stop {
    Write-Host "Stopping SeleniumNode Process"
    Get-Process | Where-Object { $_.MainWindowTitle -like '*SeleniumNode' } | Stop-Process
}

function Log-Rotation {
    # Rotate Selenium Log
    Write-Host "Performing Log Rotation"
    Move-Item "$ParentDir\Logs\selenium.log" -destination "$ParentDir\Logs\selenium-$Date-$Time.log"
    write-progress -activity "Archiving Data" -status "Progress:"

    Get-Childitem -Path "$ParentDir\Logs" | Where-Object {$_.LastWriteTime -lt (get-date).AddDays(-7)} |
    ForEach {
        $filename = $_.fullname
        Write-Host "$filename is older than 7 days"
        remove-Item "$filename"
    }
}

function Selenium-Process-Start {
    Write-Host "Starting Selenium"
    Start-Process "$ScriptDir\SeleniumHub.bat" -Verb runAs
}

Selenium-Process-Stop
Log-Rotation
Selenium-Process-Start