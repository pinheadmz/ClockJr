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
	
	$log = shell_exec("tail -n 10 /home/pi/clockjr/clockjr.log | tac");
	
?>

<a href="?cmd=P" style="width:100%;font-size:250px">Party</a>
<a href="?cmd=O" style="width:100%;font-size:250px">On/Off</a>
<pre>
<?php echo $log ?>
</pre>