<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

<script type="text/javascript">
 
function getStatus() { 
    $('div#status').load('/cgi-bin/scaleReport.py');
    setTimeout("getStatus()",500); 
}

 
</script>
<script src="http://code.jquery.com/jquery-1.8.2.min.js" type="text/javascript"></script>
 
<script type="text/javascript">
 
$(function() {
 
    getStatus();
 
});
 
 
</script>

<style>/**
 * CSS bar graph (SO)
 */
 body,html {
	margin:10;
	padding:0;
	color:#000;
//	background:#a7a09a;
}

#content { 
  overflow:auto; 
  width: 600px; 
	border: 1px solid #aeaeae; 
}

#left, #right {
	width: 40%;
  margin:5px; 
  padding: 1em; 
}

#left  { float:left;  }
#right { float:right; } 

.graph {
	width: 250px;
	height: 550px;
	border: 1px solid #aeaeae;
	background-color: #eaeaea;
}
.bar {
	width: 230px;
	margin: 7px;
	display: inline-block;
	position: relative;
	background-color: #755A42;
	vertical-align: baseline;
}
.barholder {
	display: inline-block;
	position: relative;
	vertical-align: baseline;
}
</style>
</head>

<body>

<h1>TEST SCALE READINGS REAL TIME</h1>
<div id="content">
	<div id="status">
	</div>
</div>

</body>
</html>