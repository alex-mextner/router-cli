<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway WAN Status </title>
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
			<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeWanStatus.asp" id="ID_A_WAN">WAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeWanStatus.asp" id="ID_A_WAN_STATUS">Status</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
	</ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_WAN_TITLE">WAN Status </h1>
    <label id="ID_LABEL_WAN_STATUS_DESC">This page display WAN Status.</label>
  </div>


<table>
<tr valign=top>
<td>

<table>
<tr>
<td colspan=3 align=center></td>
</tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_WAN_HOST_NAME">Host Name</label> :</td><td><b>N/A</b></td></tr>

<tr><td><b><label id="ID_LABEL_V4_WAN">IPv4 WAN</label></b></td></tr><tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_WAN_IP_ADDRESS">IPv4 Address:</label></td><td><b>192.0.2.10</b></td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_WAN_SUBNETMASK">IPv4 Subnet Mask:</label></td><td><b>255.255.248.0</b></td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_WAN_GATEWAY">IPv4 Default Gateway:</label></td><td><b>192.0.2.1</b></td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_LEASE_TIME">Lease Time</label>:</td><td><b>345600</b>&nbsp(second)</td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_REBIND_TIME">Rebind Time</label> :</td><td><b>172800</b>&nbsp&nbsp(second)</td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_V4_RENEW_TIME">Renew Time</label>:</td><td><b>302400</b>&nbsp&nbsp(second)</td></tr>
<tr><td>&nbsp;<td><label id="ID_LABEL_V4_WAN_MAC">MAC Address</label>:</td><td><b>02:00:00:00:01:1c</b></td></tr>
<tr><td>&nbsp;</td><td>IPv4 DNS Servers:</td><td><b>198.51.100.30</b></td></tr>
<tr><td>&nbsp;</td><td>&nbsp;</td><td><b>198.51.100.40</b></td></tr>
<tr><td>&nbsp;</td><td>&nbsp;</td><td><b>198.51.100.50</b></td></tr>

</table>
</td>
</tr>
</table>
</form>

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
   		<div id="copyright">©2021 Ubee Interactive . All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->
</body>
</html>
