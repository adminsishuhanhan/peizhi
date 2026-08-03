<?php
$num = str_pad(rand(1,36),2,'0',STR_PAD_LEFT);
header("Location:https://cdn.jsdelivr.net/gh/adminsishuhanhan/peizhi@main/part/{$num}.jpg",true,302);
exit;
?>
