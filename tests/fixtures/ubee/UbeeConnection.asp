<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway CableModem: Connection </title>
<script src="js/jquery-1.10.2.js"></script>
<script src="js/ubee_js_apis.js"></script>
<script LANGUAGE="javascript">

var language_jsonData = ' { "web_language": 0 } ' ;
var language_jsonObj = jQuery.parseJSON(language_jsonData); 

$(function() {

if ( !ubee_multi_language_control() )
{
	MultiLanguage_Hide();
}
else 
{
	 var page = document.location.href.match(/[^\/]+$/)[0].split(".")[0];

     ubee_jscript_setup_language(language_jsonObj, page);
     
	 ubee_get_language_list_str($('#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE'));
     $('#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE').val(language_jsonObj.web_language);
     
    //Data Post Back when select language dropdownlist
    $( '#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE' ).change(function() { 
        
        var jsonStr = '{ "web_language_cm" :' + $("select#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE option:selected").val() + ' }';

		var result =	$.ajax({
			url: '/goform/ubee_post',
			type: 'POST',
			data: jsonStr,
			contentType: 'application/json; charset=utf-8',
			dataType: 'json',
			async: false,
			success: function(msg) {
				alert("OK");
			}
		});	
        
        location.reload();
          
    });
}
});

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}

</script>
</head>

<body>
<div class="uuzp-portalContainer">
	<div class="uuzp-portalContainer-Style">
  		<div id="zp-header">
  			<a href="http://www.ubeeinteractive.com"><img src="generic_modemrouter_header.gif" BORDER=0 /></a>
  		</div>
		
		<div class="zp-portal-top-left">
			<div class="zp-portal-top-right">
				<div class="zp-portal-top-center"></div>
			</div>
		</div>
		<div class="zp-portal-center">
	    	<div id="navigation-top-line"></div>
	    	<div class="uuzp-contentholder">
	<!-- Main Menu  -->
				  
<div id="navigation_header">
   <ul>
	 <li><a class="current" href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM"  >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a href="UbeeLanSetup.asp" id="ID_A_GATEWAY">Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li>
                          <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
	
   </ul>
</div>
			<!-- Main Menu  -->

			<div id="navigation-bottom-line"></div>
<!-- Navigator bar  -->
<div id="navigation_bar">
       <ul>
        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeSysInfo.asp" id="ID_A_STATUS">Status</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeSysInfo.asp" id="ID_A_SYSTEM_INFORMATION" >System Information</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeConnection.asp" id="ID_A_SYSTEM_CONNECTION">Connection</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeConfiguration.asp" id="ID_A_SYSTEM_CONFIGURATION" >Configuration</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeCmProvisioning.asp" id="ID_A_PROVISIONING">Provisioning</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementPassword.asp" id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
      </ul>
    
</div>
<!-- Navigator bar  -->

<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_CONNECTION_TITLE" >Connection</h1>
   <label id="ID_LABEL_CONNECTION_DESC">This page displays the connection information.</label>
  </div>
  <form action=/goform/UbeeConnection method=POST name="Connection">
  <div class="table_data">
<table>
   <tr><th colspan=2><b><label id="ID_LABEL_TABLE_CONNECTION_INIT_SCAN">Initial Scan</label></b></th></tr>
   <tr>
       <td><label id="ID_LABEL_TABLE_CONNECTION_FAVORITE_FREQ">Favorite Frequency</label> (MHz)</td>
       <td><input name="CmConfigFrequency" type="text" size=3 maxlength=3 value=></td>
       <td><input type="submit" id="ID_LABEL_TABLE_CONNECTION_FREQ_APPLY" value="Apply" align="MIDDLE"></td>
   </tr> 
</table><br>
<br>
<table style="font-family: Helvetica;font-size:14">
<tr bgcolor=#CE0000><th colspan=9><b><label id="ID_LABEL_TABLE_DOWNSTREAM">Downstream Bonded Channels</label></b></th></tr>

<tr bgcolor="#FF8C00"><td><label id="ID_LABEL_TABLE_DOWNSTREAM_CHANNEL">Channel</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_LOCK_STATUS">Lock Status</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_MODULATION">Modulation</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_FREQUENCY">Frequency</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_POWER">Power</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_SNR">SNR</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_SYMBOL_RATE">Symbol Rate</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_CORRECTABLE">Correctables</label></td><td><label id="ID_LABEL_TABLE_DOWNSTREAM_UNCORRECTABLE">Uncorrectables</label></td></tr>
<tr bgcolor="#9999CC"><td>1</td><td>Locked</td><td>QAM256</td><td>266000000 Hz</td><td> 3.6 dBmV</td><td>39.7 dB</td><td>6952 Ksym/sec</td><td>30092</td><td>8305</td></tr>
<tr bgcolor="#99CCFF"><td>2</td><td>Locked</td><td>QAM256</td><td>154000000 Hz</td><td> 4.1 dBmV</td><td>39.6 dB</td><td>6952 Ksym/sec</td><td>22645</td><td>5303</td></tr>
<tr bgcolor="#9999CC"><td>3</td><td>Locked</td><td>QAM256</td><td>162000000 Hz</td><td> 4.2 dBmV</td><td>39.3 dB</td><td>6952 Ksym/sec</td><td>24073</td><td>6150</td></tr>
<tr bgcolor="#99CCFF"><td>4</td><td>Locked</td><td>QAM256</td><td>170000000 Hz</td><td> 4.1 dBmV</td><td>39.7 dB</td><td>6952 Ksym/sec</td><td>22898</td><td>5586</td></tr>
<tr bgcolor="#9999CC"><td>5</td><td>Locked</td><td>QAM256</td><td>210000000 Hz</td><td> 4.0 dBmV</td><td>39.9 dB</td><td>6952 Ksym/sec</td><td>32028</td><td>16748</td></tr>
<tr bgcolor="#99CCFF"><td>6</td><td>Locked</td><td>QAM256</td><td>250000000 Hz</td><td> 3.4 dBmV</td><td>39.6 dB</td><td>6952 Ksym/sec</td><td>34409</td><td>19526</td></tr>
<tr bgcolor="#9999CC"><td>7</td><td>Locked</td><td>QAM256</td><td>370000000 Hz</td><td> 4.2 dBmV</td><td>39.6 dB</td><td>6952 Ksym/sec</td><td>24396</td><td>21174</td></tr>
<tr bgcolor="#99CCFF"><td>8</td><td>Locked</td><td>QAM256</td><td>146000000 Hz</td><td> 4.1 dBmV</td><td>39.5 dB</td><td>6952 Ksym/sec</td><td>32569</td><td>10472</td></tr>
<tr bgcolor="#9999CC"><td>9</td><td>Locked</td><td>QAM256</td><td>306000000 Hz</td><td> 3.2 dBmV</td><td>39.5 dB</td><td>6952 Ksym/sec</td><td>32185</td><td>15250</td></tr>
<tr bgcolor="#99CCFF"><td>10</td><td>Locked</td><td>QAM256</td><td>314000000 Hz</td><td> 3.6 dBmV</td><td>39.6 dB</td><td>6952 Ksym/sec</td><td>23545</td><td>4741</td></tr>
<tr bgcolor="#9999CC"><td>11</td><td>Locked</td><td>QAM256</td><td>322000000 Hz</td><td> 4.1 dBmV</td><td>39.7 dB</td><td>6952 Ksym/sec</td><td>35641</td><td>15610</td></tr>
<tr bgcolor="#99CCFF"><td>12</td><td>Locked</td><td>QAM256</td><td>330000000 Hz</td><td> 4.1 dBmV</td><td>39.4 dB</td><td>6952 Ksym/sec</td><td>35009</td><td>12499</td></tr>
<tr bgcolor="#9999CC"><td>13</td><td>Locked</td><td>QAM256</td><td>338000000 Hz</td><td> 3.9 dBmV</td><td>39.3 dB</td><td>6952 Ksym/sec</td><td>33982</td><td>17261</td></tr>
<tr bgcolor="#99CCFF"><td>14</td><td>Locked</td><td>QAM256</td><td>378000000 Hz</td><td> 4.6 dBmV</td><td>39.8 dB</td><td>6952 Ksym/sec</td><td>34804</td><td>21195</td></tr>
<tr bgcolor="#9999CC"><td>15</td><td>Locked</td><td>QAM256</td><td>386000000 Hz</td><td> 4.8 dBmV</td><td>39.8 dB</td><td>6952 Ksym/sec</td><td>32768</td><td>20430</td></tr>
<tr bgcolor="#99CCFF"><td>16</td><td>Locked</td><td>QAM256</td><td>394000000 Hz</td><td> 4.6 dBmV</td><td>37.4 dB</td><td>6952 Ksym/sec</td><td>30752</td><td>19785</td></tr>
<tr bgcolor="#9999CC"><td>17</td><td>Locked</td><td>QAM256</td><td>402000000 Hz</td><td> 4.4 dBmV</td><td>40.3 dB</td><td>6952 Ksym/sec</td><td>33106</td><td>23739</td></tr>
<tr bgcolor="#99CCFF"><td>18</td><td>Locked</td><td>QAM256</td><td>410000000 Hz</td><td> 4.9 dBmV</td><td>40.3 dB</td><td>6952 Ksym/sec</td><td>30652</td><td>23684</td></tr>
<tr bgcolor="#9999CC"><td>19</td><td>Locked</td><td>QAM256</td><td>418000000 Hz</td><td> 5.0 dBmV</td><td>40.6 dB</td><td>6952 Ksym/sec</td><td>29085</td><td>23990</td></tr>
<tr bgcolor="#99CCFF"><td>20</td><td>Locked</td><td>QAM256</td><td>426000000 Hz</td><td> 4.9 dBmV</td><td>40.4 dB</td><td>6952 Ksym/sec</td><td>28044</td><td>21262</td></tr>
<tr bgcolor="#9999CC"><td>21</td><td>Locked</td><td>QAM256</td><td>434000000 Hz</td><td> 4.7 dBmV</td><td>40.3 dB</td><td>6952 Ksym/sec</td><td>28503</td><td>23981</td></tr>
<tr bgcolor="#99CCFF"><td>22</td><td>Locked</td><td>QAM256</td><td>442000000 Hz</td><td> 4.7 dBmV</td><td>40.3 dB</td><td>6952 Ksym/sec</td><td>27823</td><td>20622</td></tr>
<tr bgcolor="#9999CC"><td>23</td><td>Locked</td><td>QAM256</td><td>450000000 Hz</td><td> 4.7 dBmV</td><td>40.3 dB</td><td>6952 Ksym/sec</td><td>28028</td><td>21017</td></tr>
<tr bgcolor="#99CCFF"><td>24</td><td>Locked</td><td>QAM256</td><td>458000000 Hz</td><td> 5.0 dBmV</td><td>40.4 dB</td><td>6952 Ksym/sec</td><td>25509</td><td>19926</td></tr>
</table>

<br>
<table style="font-family: Helvetica;font-size:14">
<tr bgcolor=#CE0000><th colspan=7><b><label id="ID_LABEL_TABLE_UPSTREAM">Upstream Bonded Channels</label></b></th></tr>

<tr bgcolor="#FF8C00"><td><label id="ID_LABEL_TABLE_UPSTREAM_CHANNEL">Channel</label></td><td><label id="ID_LABEL_TABLE_UPSTREAM_LOCK_STATUS">Lock Status</label></td><td><label id="ID_LABEL_TABLE_UPSTREAM_CHANNEL_TYPE">US Channel Type</label></td><td><label id="ID_LABEL_TABLE_UPSTREAM_SYMBOL_RATE">Symbol Rate</label></td><td><label id="ID_LABEL_TABLE_UPSTREAM_FREQUENCY">Frequency</label></td><td><label id="ID_LABEL_TABLE_UPSTREAM_POWER">Power</label></td></tr>
<tr bgcolor="#9999CC"><td>1</td><td>Locked</td><td>ATDMA</td><td>2560 Ksym/sec</td><td>50600000 Hz</td><td>44.0 dBmV</td></tr>
<tr bgcolor="#99CCFF"><td>2</td><td>Locked</td><td>ATDMA</td><td>5120 Ksym/sec</td><td>55400000 Hz</td><td>44.8 dBmV</td></tr>
<tr bgcolor="#9999CC"><td>3</td><td>Locked</td><td>ATDMA</td><td>5120 Ksym/sec</td><td>61800000 Hz</td><td>45.1 dBmV</td></tr>
<tr bgcolor="#99CCFF"><td>4</td><td>Locked</td><td>ATDMA</td><td>2560 Ksym/sec</td><td>47400000 Hz</td><td>43.8 dBmV</td></tr>
<tr bgcolor="#9999CC"><td>5</td><td>Locked</td><td>ATDMA</td><td>5120 Ksym/sec</td><td>68200000 Hz</td><td>45.0 dBmV</td></tr>
<tr bgcolor="#99CCFF"><td>6</td><td>Locked</td><td>ATDMA</td><td>5120 Ksym/sec</td><td>74600000 Hz</td><td>44.1 dBmV</td></tr>
<tr bgcolor="#9999CC"><td>7</td><td>Not Locked</td><td>Unknown</td><td>0 Ksym/sec</td><td>0 Hz</td><td> 0.0 dBmV</td></tr>
<tr bgcolor="#99CCFF"><td>8</td><td>Not Locked</td><td>Unknown</td><td>0 Ksym/sec</td><td>0 Hz</td><td> 0.0 dBmV</td></tr>
</table>

<br>
</div>


</div>

</div> <!-- hold -->

	<div id=hold-bottom-line></div>
	
</div> <!-- center -->
		<div class="zp-portal-bottom-left">
			<div class="zp-portal-bottom-right">
				<div class="zp-portal-bottom-center"></div>
			</div>
		</div>
		
	<div id=footer>
   		<div id="copyright">©2021 Ubee Interactive. All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->
</body>

</html>
