<?php
	// requires apache and php running
	// mkdir commands and chmod777
	//	ln -s ~/clockjr/clockjrwww.php /var/www/html/index.php
		
	if(!empty($_REQUEST['cmd'])){
		$command = $_REQUEST['cmd'];
		$dir = "/home/pi/clockjr/commands/";

		$cmdfile = fopen($dir . ".clockjrcommand", "w");
		$cmdfile;
		fwrite($cmdfile, $command);
		fclose($cmdfile);
		header('Location: /');
	}
	
	if(!empty($_REQUEST['ssid']) && !empty($_REQUEST['password'])){
		$command = 'network={' . "\n\t" . 'ssid="' . $_REQUEST['ssid'] . '"' . "\n\t" . 'psk="' . $_REQUEST['password'] . '"' . "\n}\n";
		$dir = "/home/pi/clockjr/commands/";
		
		$cmdfile = fopen($dir . ".wifi", "w");
		$cmdfile;
		fwrite($cmdfile, $command);
		fclose($cmdfile);
		header('Location: /');
	}
	
	$log = shell_exec("tail -n 10 /home/pi/clockjr/clocklog.log | tac");
	
?>
<html>
<head>
<title>ClockJr</title>
<meta name="viewport" content="initial-scale=1, maximum-scale=1">
</head>
<body>
<a href="?cmd=P" style="font-size: 10vw">Party</a><br>
<a href="?cmd=O" style="font-size: 10vw">On/Off</a><br>
<hr>
<form action="/index.php"  style="font-size: 2vw">
	Add WiFi access:<br>
	Network Name:<br>
	<input type="text" name="ssid" value="">
	<br>
	Password:<br>
	<input type="text" name="password" value="">
	<br><br>
	<input type="submit" value="Submit">
</form> 

<pre>
<?php echo $log ?>
</pre>
</body>
</html>