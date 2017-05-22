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
	}
?>

<a href="?cmd=P" style="width:100%;font-size:250px">Party</a>
<a href="?cmd=O" style="width:100%;font-size:250px">On/Off</a>