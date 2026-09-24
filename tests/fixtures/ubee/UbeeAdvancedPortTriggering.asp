<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced Port Triggering</title>
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
   
    $('#ID_BUTTON_APPLY_PORT_TRIGGER').click(function(e) { 

		if( parseInt($('#PortTriggeringTargetStartPort').val()) > parseInt($('#PortTriggeringTargetEndPort').val()))
		{
			alert("Target Port range is invalid.");					
			e.preventDefault();
			return;
		}
		
		if( parseInt($('#PortTriggeringTriggerStartPort').val()) > parseInt($('#PortTriggeringTriggerEndPort').val()))
		{
			alert("Triggering Port range is invalid.");					
			e.preventDefault();
			return;
		}			
          
     });
   
     
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

<!-- hide me
function createEntry()
{
    window.document.UbeeAdvancedPortTriggering.PortTriggeringCreateRemove.value = 1;
    window.document.UbeeAdvancedPortTriggering.submit();
}
function removeAllEntries()
{
    window.document.UbeeAdvancedPortTriggering.PortTriggeringCreateRemove.value = 3;
    window.document.UbeeAdvancedPortTriggering.submit();
}
function removeEntry(entry)
{
    window.document.UbeeAdvancedPortTriggering.PortTriggeringCreateRemove.value = 2;
    window.document.UbeeAdvancedPortTriggering.PortTriggeringTable.value = entry;
    window.document.UbeeAdvancedPortTriggering.submit();
}
function editEntry(entry)
{
    window.document.UbeeAdvancedPortTriggering.PortTriggeringCreateRemove.value = 0;
    window.document.UbeeAdvancedPortTriggering.PortTriggeringTable.value = entry;
    window.document.UbeeAdvancedPortTriggering.submit();
}
function applyCommitTriggering()
{
    window.document.UbeeAdvancedPortTriggering.PortTriggeringApply.value = 1;
}

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}
// show me -->

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
			   
			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvConnectedDevicesList.asp"  id="ID_A_CONNECTED_DEVICES_LIST">Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		          </ul>
		       
			  </div>
			<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_ADVANCED_PORT_TRIGGERING_TITLE">Advanced Port Triggering</h1>
    <label id="ID_LABEL_ADVANCED_PORT_TRIGGERING_DESC">This page allows configuration of dynamic triggers to specific devices on the LAN. This allows for special applications that require specific port numbers with bi-directional traffic to function properly. Applications such as video conferencing, voice, gaming, and some messenging program features may require these special settings.</label>
  </div>

<form action=/goform/UbeeAdvancedPortTriggering method=POST name="UbeeAdvancedPortTriggering">

<table><tr><td><table>
<tr>
<td>
<input type="submit" onclick="createEntry();" value="Create" id="ID_LABEL_TABLE_CREATE"align="left">
<input type="hidden" value="0" name="PortTriggeringCreateRemove">
</td>
</tr>
<tr><td>&nbsp;</td></tr>








</table>

<div class="table_data table_data12">
<table>
<tr><th colspan=2><label id="ID_LABEL_TABLE_PORT_TRIGGER">Trigger</label></th><th colspan=2><label id="ID_LABEL_TABLE_PORT_TARGET">Target</label></th></tr>
<tr><th><label id="ID_LABEL_TABLE_START_PORT">Start Port</label></th><th><label id="ID_LABEL_TABLE_END_PORT">End Port</label></th><th><label id="ID_LABEL_TABLE_START_PORT1">Start Port</label></th><th><label id="ID_LABEL_TABLE_END_PORT1">End Port</label></th><th><label id="ID_LABEL_TABLE_PROTOCOL">Protocol</label></th><th><label id="ID_LABEL_TABLE_DESCRIPTION1">Description</label></th><th><label id="ID_LABEL_TABLE_ENABLE1">Enabled</label></th>
<th>&nbsp;</th>
<th><input type="submit" onclick="removeAllEntries();" value="Remove All" id="ID_BUTTON_REMOVE_ALL_PORT_TRIGGER" align="left"></th>
<td><input type="hidden" value="0" name="PortTriggeringTable"></td>
</table>
</div>
</td>
</tr></table>


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
