<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced Port Filtering</title>
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
     
	 
	 $('#ID_BUTTON_APPLY_PORT_FILTER').click(function(e) { 
	 
		for(i = 1; i < 10; i++)
		{
			var start_port_selector_name = "#IpFilterPortStart"+i ;
			var end_port_selector_name = "#IpFilterPortEnd"+i;
			if( parseInt($(start_port_selector_name).val()) > parseInt($(end_port_selector_name).val()))
			{
				alert("Port range in rule "+i+ " is invalid.");					
				e.preventDefault();
				return;
			}		
		}
          
     });
	 
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

			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvConnectedDevicesList.asp"  id="ID_A_CONNECTED_DEVICES_LIST">Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		      </ul>
			  </div>
			<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_ADVANCED_PORT_FILTERING_TITLE">Advanced Port Filtering</h1>
  <label id="ID_H1_HEADER_ADVANCED_PORT_FILTERING_DESC">  This page allows configuration of port filters in order to block specific internet services to all devices on the LAN.</label>
  </div>

<form action=/goform/UbeeAdvancedPortFiltering method=POST>

<table>

<tr>

<td>

<table border>
<tr>
<td colspan=4 align=center><label id="ID_LABEL_TABLE_PORT_FILTER">Port Filtering</label></td>
</tr>
<tr>
<td><label id="ID_LABEL_TABLE_START_PORT">Start Port</label></td><td><label id="ID_LABEL_TABLE_END_PORT">End Port</label></td><td><label id="ID_LABEL_TABLE_PROTOCOL">Protocol</label></td><td><label id="ID_LABEL_TABLE_ENABLE">Enabled</label></td>
</tr>
<!-- Entry 1 -->
<tr><td>
<input type="text" id=IpFilterPortStart1 name=IpFilterPortStart1 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd1 name=IpFilterPortEnd1 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol1" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable1" value="0x01" >
</td>
</tr>
<!-- Entry 2 -->
<tr><td>
<input type="text" id=IpFilterPortStart2 name=IpFilterPortStart2 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd2 name=IpFilterPortEnd2 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol2" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable2" value="0x01" >
</td>
</tr>
<!-- Entry 3 -->
<tr><td>
<input type="text" id=IpFilterPortStart3 name=IpFilterPortStart3 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd3 name=IpFilterPortEnd3 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol3" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable3" value="0x01" >
</td>
</tr>
<!-- Entry 4 -->
<tr><td>
<input type="text" id=IpFilterPortStart4 name=IpFilterPortStart4 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd4 name=IpFilterPortEnd4 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol4" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable4" value="0x01" >
</td>
</tr>
<!-- Entry 5 -->
<tr><td>
<input type="text" id=IpFilterPortStart5 name=IpFilterPortStart5 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd5 name=IpFilterPortEnd5 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol5" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable5" value="0x01" >
</td>
</tr>
<!-- Entry 6 -->
<tr><td>
<input type="text" id=IpFilterPortStart6 name=IpFilterPortStart6 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd6 name=IpFilterPortEnd6 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol6" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
</td>
<td><input type="checkbox" name="PortFilteringEnable6" value="0x01" >
</td>
</tr>
<!-- Entry 7 -->
<tr><td>
<input type="text" id=IpFilterPortStart7 name=IpFilterPortStart7 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd7 name=IpFilterPortEnd7 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol7" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable7" value="0x01" >
</td>
</tr>
<!-- Entry 8 -->
<tr><td>
<input type="text" id=IpFilterPortStart8 name=IpFilterPortStart8 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd8 name=IpFilterPortEnd8 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol8" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable8" value="0x01" >
</td>
</tr>
<!-- Entry 9 -->
<tr><td>
<input type="text" id=IpFilterPortStart9 name=IpFilterPortStart9 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd9 name=IpFilterPortEnd9 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol9" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable9" value="0x01" >
</td>
</tr>
<!-- Entry 10 -->
<tr><td>
<input type="text" id=IpFilterPortStart10 name=IpFilterPortStart10 size=5 maxlength=5 value=1>
</td>
<td>
<input type="text" id=IpFilterPortEnd10 name=IpFilterPortEnd10 size=5 maxlength=5 value=65535>
</td>
<td>
<select name="PortFilteringProtocol10" size=1>
<option value="4" >TCP</option>
<option value="3" >UDP</option>
<option value="254" selected>BOTH</option>

</select>
</td>
<td><input type="checkbox" name="PortFilteringEnable10" value="0x01" >
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td colspan=2 align=center><input type="Submit" value="Apply" align="MIDDLE" id="ID_BUTTON_APPLY_PORT_FILTER" ></td>
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
   		<div id="copyright">©2021 Ubee Interactive. All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->
</body>

</html>

