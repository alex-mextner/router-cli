<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced IP Filtering</title>
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

/*
	  $('#ID_BUTTON_APPLY_IP_FILTER').click(function(e) { 
	 
		for(i = 1; i < 7; i++)
		{
			for( j = 2; j<=3 ; j++)
			{
				var start_ip_selector_name = "#IpFilterAddressStart"+i+"IP"+j ;
				var end_ip_selector_name = "#IpFilterAddressEnd"+i+"IP"+j ;
				if( parseInt($(start_ip_selector_name).val()) > parseInt($(end_ip_selector_name).val()))
				{
					alert("IP range in rule "+i+ " is invalid.");					
					e.preventDefault();
					return;
				}
			}			
		}
          
     });
*/
	 
	 
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
$('#ID_BUTTON_APPLY_IP_FILTER').click(function(e) {

    for(i = 1; i < 11; i++)
    {
        for( j = 2; j<=3 ; j++)
        {
            var start_ip_selector_name = "#IpFilterAddressStart"+i+"IP"+j ;
            var end_ip_selector_name = "#IpFilterAddressEnd"+i+"IP"+j ;
            if( parseInt($(start_ip_selector_name).val()) > parseInt($(end_ip_selector_name).val()))
            {
                alert("IP range in rule "+i+ " is invalid.");
                e.preventDefault();
                return;
            }
        }
    }
});
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
			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvConnectedDevicesList.asp"  id="ID_A_CONNECTED_DEVICES_LIST">Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvancedIpFiltering.asp"  id="ID_A_IP_FILTER"  >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		      </ul>
			  </div>
			<div id="main_page">
			  <div class="description">
    <h1 id="ID_H1_HEADER_IP_FILTER_TITLE">Advanced IP Filtering</h1>
   <label id="ID_H1_HEADER_IP_FILTER_DESC">This page allows configuration of IP address filters in order to block internet traffic to specific network <br>
    devices on the LAN.</label>
  </div>

<form action=/goform/UbeeAdvancedIpFiltering method=POST>

<table>

<tr>

<td>
<table border>
<tr>
<td colspan=3 align=center><label id="ID_LABEL_HEADER_IP_FILTER_TITLE">IP Filtering</label></td>
</tr>
<tr>
<td><label id="ID_LABEL_START_ADDRESS">Start Address</label></td><td><label id="ID_LABEl_END_ADDRESS">End Address</label></td><td><label id="ID_LABEL_FILTER_ENABLE">Enabled</label></td>
</tr>
<!-- Entry 1 -->
<tr><td>
<b>192.168.</b><input type="text" name=IpFilterAddressStart1IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart1IP3 name=IpFilterAddressStart1IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" name=IpFilterAddressEnd1IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd1IP3 name=IpFilterAddressEnd1IP3 size=3 maxlength=3 value=0>
</td>
<td><input type="checkbox" name="IpFilteringEnable1" value="0x01" >
</td>
</tr>
<!-- Entry 2 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart2IP2 name=IpFilterAddressStart2IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart2IP3 name=IpFilterAddressStart2IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd2IP2 name=IpFilterAddressEnd2IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd2IP3 name=IpFilterAddressEnd2IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable2" value="0x01" >
</td>
</tr>
<!-- Entry 3 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart3IP2 name=IpFilterAddressStart3IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart3IP3 name=IpFilterAddressStart3IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd3IP2 name=IpFilterAddressEnd3IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd3IP3 name=IpFilterAddressEnd3IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable3" value="0x01" >
</td>
</tr>
<!-- Entry 4 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart4IP2 name=IpFilterAddressStart4IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart4IP3 name=IpFilterAddressStart4IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd4IP2 name=IpFilterAddressEnd4IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd4IP3 name=IpFilterAddressEnd4IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable4" value="0x01" >
</td>
</tr>
<!-- Entry 5 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart5IP2 name=IpFilterAddressStart5IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart5IP3 name=IpFilterAddressStart5IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd5IP2 name=IpFilterAddressEnd5IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd5IP3 name=IpFilterAddressEnd5IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable5" value="0x01" >
</td>
</tr>
<!-- Entry 6 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart6IP2 name=IpFilterAddressStart6IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart6IP3 name=IpFilterAddressStart6IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd6IP2 name=IpFilterAddressEnd6IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd6IP3 name=IpFilterAddressEnd6IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable6" value="0x01" >
</td>
</tr>
<!-- Entry 7 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart7IP2 name=IpFilterAddressStart7IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart7IP3 name=IpFilterAddressStart7IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd7IP2 name=IpFilterAddressEnd7IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd7IP3 name=IpFilterAddressEnd7IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable7" value="0x01" >
</td>
</tr>
<!-- Entry 8 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart8IP2 name=IpFilterAddressStart8IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart8IP3 name=IpFilterAddressStart8IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd8IP2 name=IpFilterAddressEnd8IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd8IP3 name=IpFilterAddressEnd8IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable8" value="0x01" >
</td>
</tr>
<!-- Entry 9 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart9IP2 name=IpFilterAddressStart9IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressStart9IP3 name=IpFilterAddressStart9IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd9IP2 name=IpFilterAddressEnd9IP2 size=3 maxlength=3  disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd9IP3 name=IpFilterAddressEnd9IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable9" value="0x01" >
</td>
</tr>
<!-- Entry 10 -->
<tr><td>
<b>192.168.</b><input type="text" id=IpFilterAddressStart10IP2 name=IpFilterAddressStart10IP2 size=3 maxlength=3 disabled="disabled"  value=0>.</b><input type="text" id=IpFilterAddressStart10IP3 name=IpFilterAddressStart10IP3 size=3 maxlength=3 value=0>
</td>
<td>
<b>192.168.</b><input type="text" id=IpFilterAddressEnd10IP2 name=IpFilterAddressEnd10IP2 size=3 maxlength=3 disabled="disabled" value=0>.</b><input type="text" id=IpFilterAddressEnd10IP3 name=IpFilterAddressEnd10IP3 size=3 maxlength=3 value=0>
</td></td>
<td><input type="checkbox" name="IpFilteringEnable10" value="0x01" >
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td colspan=2 align=center><input type="Submit" value="Apply" align="MIDDLE" id="ID_BUTTON_APPLY_IP_FILTER"></td>
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
