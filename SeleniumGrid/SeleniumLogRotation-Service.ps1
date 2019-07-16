<#	
	.NOTES
	===========================================================================
	 Selenium Log Rotation
	 Environment:   Selenium Nodes
	 Created on:   	7-17-17
     Authored By:   Nick Serra	

     1. Stop SeleniumNode Service
     2. Rename Selenium.log -> Selenium-$Date.log
     3. Start SeleniumNode Service
	===========================================================================
	
#>

# Grabs the Path from relative location where script is executed from
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Write-Host "Script Directory is: $ScriptDir"

# Formatted Date
$Date = (Get-Date).ToString("MM-dd-yyyy")
# Formatted Time
$Time = (Get-Date).ToString("HH_mm")

# Define Table
$table1 = "Services:"
# Create table objects
$table1 = New-Object System.Data.DataTable "Services"

# Define and Add Columns to table
$t1c1 = New-Object system.Data.DataColumn "Server",([string])
$table1.columns.add($t1c1) # Add Column
$t1c2 = New-Object system.Data.DataColumn "Date",([string])
$table1.columns.add($t1c2) # Add Column
$t1c3 = New-Object system.Data.DataColumn "Time",([string])
$table1.columns.add($t1c3) # Add Column
$t1c4 = New-Object system.Data.DataColumn "Status",([string])
$table1.columns.add($t1c4) # Add Column
$t1c5 = New-Object system.Data.DataColumn "Display Name",([string])
$table1.columns.add($t1c5) # Add Column
$t1c6 = New-Object system.Data.DataColumn "Service Name",([string])
$table1.columns.add($t1c6) # Add Column

$Services = @("SeleniumNode")


function Stop-Services {
    # Check Each Service in $Services Array specified from Server Check
    foreach ($Service in $Services) {
        $Server = $env:computerName

	    Write-Host "Stopping $Service on $Server"
	
	    $Serv = Get-Service -ComputerName $Server | Where-Object {$_.Name -match $Service}
	    Stop-Service -InputObject $Serv

	    $Name = $Serv | Select Name
	    $Name = $Name.Name

	    $Status = $Serv | Select Status
	    $Status = $Status.Status

	    $DisplayName = $Serv | Select DisplayName
	    $DisplayName = $DisplayName.DisplayName

        # Add a Row to the Table
        $row = $table1.NewRow()
	    $row.$t1c1 = $Server      #Add Variable to column
        $row.$t1c2 = $Date        #Add Variable to column
        $row.$t1c3 = $Time        #Add Variable to column
	    $row.$t1c4 = $Status      #Add Variable to column
	    $row.$t1c5 = $DisplayName #Add Variable to column
        $row.$t1c6 = $Name        #Add Variable to column
	    $table1.Rows.Add($row)	  #Add the row to table1
    } <#Add Maintenace Server additional / non tracked Services #>	
	
    # Output Table without a filter
    # $table1 | Out-GridView -Title "Stopped Services"
    # Create a txt file of the output
    $StartedServicesOutput = "$ScriptDir\Logs\Selenium-Refresh.log"
    $table1 | Out-File -FilePath $StartedServicesOutput -Append
 
    # Clear Contents of table1
    $table1.clear()
}


function Log-Rotation {
    # Rotate Selenium Log
    Write-Host "Performing Log Rotation"
    Move-Item "$ScriptDir\Logs\selenium.log" -destination "$ScriptDir\Logs\selenium-$Date-$Time.log"
    write-progress -activity "Archiving Data" -status "Progress:"

    Get-Childitem -Path "$ScriptDir\Logs" | Where-Object {$_.LastWriteTime -lt (get-date).AddDays(-7)} |
     ForEach {
         $filename = $_.fullname
         Write-Host "$filename is older than 7 days"
         remove-Item "$ScriptDir\Logs\$filename"
    }
}



function Start-Services {
    # Check Each Service in $Services Array specified from Server Check
    foreach ($Service in $Services) {
        $Server = $env:computerName

	    Write-Host "Starting $Service on $Server"
	
	    $Serv = Get-Service -ComputerName $Server | Where-Object {$_.Name -match $Service}
	    Start-Service -InputObject $Serv

	    $Name = $Serv | Select Name
	    $Name = $Name.Name

	    $Status = $Serv | Select Status
	    $Status = $Status.Status

	    $DisplayName = $Serv | Select DisplayName
	    $DisplayName = $DisplayName.DisplayName

        # Add a Row to the Table
        $row = $table1.NewRow()
	    $row.$t1c1 = $Server      #Add Variable to column
        $row.$t1c2 = $Date        #Add Variable to column
        $row.$t1c3 = $Time        #Add Variable to column
	    $row.$t1c4 = $Status      #Add Variable to column
	    $row.$t1c5 = $DisplayName #Add Variable to column
        $row.$t1c6 = $Name        #Add Variable to column
	    $table1.Rows.Add($row)	  #Add the row to table1
    } <#Add Maintenace Server additional / non tracked Services #>	

    # Output Table without a filter
    # $table1 | Out-GridView -Title "Started Services"
    # Create a txt file of the output
    $StartedServicesOutput = "$ScriptDir\Logs\Selenium-Refresh.log"
    $table1 | Out-File -FilePath $StartedServicesOutput -Append
 
    # Clear Contents of table1
    $table1.clear()
}

Stop-Services
Log-Rotation
Start-Services