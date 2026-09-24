<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced Connected Devices </title>
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
        
        var jsonStr = '{ "web_language" :' + $("select#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE option:selected").val() + ' }';

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


function onLoadScript()
{
   
}



function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}

// show me -->

</script>
</head>

<body onLoad="onLoadScript()">
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
		
<div id="navigation_header">
   <ul>
	<li><a href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM" >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a class="current" href="UbeeLanSetup.asp" id="ID_A_GATEWAY" >Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li>
                 <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
<div id="navigation_bar">
	  <ul>
			<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_CONNECTED_DEVICES_LIST" >Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div> 

		      </ul>
			  </div>
			<div id="main_page">
              
<div class="description"><h1 id="ID_H1_ADV_CONNECTED_HEADER_TITLE_2G">Connected Stations of Wireless 2.4G</h1><label id="ID_LABEL_ADV_CONNECTED_HEADER_DESC_2G"> This table allows configuration of the Access Control to the AP as well as status on the connected clients.</label></div>

<table>
  
  <tr valign=top>
   
    <td>
    <table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_2G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_2G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_2G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_2G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_2G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_2G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_2G">Speed</label> (kbps)</td></tr><tr><td colspan=5><label id="ID_LABEL_NO_STA_DESC_2G">No wireless clients are connected.</label></td></tr>
    </table>
    </td>
  </tr>
</table>
<hr/>
<div class="description"><h1 id="ID_H1_ADV_CONNECTED_HEADER_TITLE_5G">Connected Stations of Wireless 5G </h1><label id="ID_LABEL_ADV_CONNECTED_HEADER_DESC_5G" > This table allows configuration of the Access Control to the AP as well as status on the connected clients.</label></div>
<table>
  
  <tr valign=top>
    
    <td>
    <table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_5G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_5G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_5G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_5G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_5G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_5G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_5G">Speed</label> (kbps)</td></tr><tr><td colspan=5><label id="ID_LABEL_NO_STA_DESC_5G">No wireless clients are connected.</label></td></tr>
    </table>
    </td>
  </tr>
</table>

            <div class="description">
	    	      <h1 id="ID_H1_HEADER_ADV_CONNECTED_TITLE">Connected Stations of LAN Users</h1>
	    	    <label id="ID_LABEL_ADV_CONNECTED_TITLE_DESC">  This table shows users connected to LAN.</label> 
    	      </div>
	    	 
	    	      <table>
	    	        <br>
	    	        <tr>
	    	          <td><table style="font-family: Helvetica;font-size:14"><tr bgcolor=#FF8C00><td><label id="ID_LABEL_MAC_ADDRESS">MAC Address</label></td><td><label id="ID_LABEL_IP_ADDRESS">IP Address</label><td><label id="ID_LABEL_DURATION">Duration</label></td><td><label id="ID_LABEL_EXPIRES">Expires</label></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:08</td><td>192.168.0.13</td><td>D:-- H:-- M:-- S:--</td><td>*** STATIC IP ADDRESS **</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:09</td><td>192.168.0.14</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:20:57 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:0A</td><td>192.168.0.16</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:30:31 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:0B</td><td>192.168.0.17</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:26:18 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:0C</td><td>192.168.0.18</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:22:36 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:0D</td><td>192.168.0.19</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:21:39 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:0E</td><td>192.168.0.20</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:31:25 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:0F</td><td>192.168.0.22</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:29:34 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:10</td><td>192.168.0.24</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:37:34 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:05</td><td>192.168.0.26</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:28:35 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:11</td><td>192.168.0.29</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:10:33 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:12</td><td>192.168.0.30</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:30:31 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:13</td><td>192.168.0.35</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:33:01 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:14</td><td>192.168.0.36</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:20:30 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:01</td><td>192.168.0.39</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:37:14 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:15</td><td>192.168.0.43</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:27:01 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:03</td><td>192.168.0.66</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:12:19 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:16</td><td>192.168.0.104</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:36:14 2026
</td><td align=center></td></tr>
<tr bgcolor=#99CCFF><td>02:00:00:00:01:17</td><td>192.168.0.121</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:36:16 2026
</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>02:00:00:00:01:18</td><td>192.168.0.123</td><td>D:00 H:01 M:00 S:00</td><td>Thu Sep 24 20:37:00 2026
</td><td align=center></td></tr>
</table>
</td>
    	            </tr>
	    	        
    	          </table>
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
