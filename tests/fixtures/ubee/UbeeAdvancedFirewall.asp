<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 4.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced Firewall</title>
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

<!-- hide me
function AddKeyword()
{
	window.document.UbeeAdvancedFirewall.KeywordAction.value = 1;
}

function RemoveKeyword()
{
	window.document.UbeeAdvancedFirewall.KeywordAction.value = 2;
}
function AddDomain()
{
	window.document.UbeeAdvancedFirewall.DomainAction.value = 1;
}

function RemoveDomain()
{
	window.document.UbeeAdvancedFirewall.DomainAction.value = 2;
}

function DenyButton()
{
        var the_box = window.document.UbeeAdvancedFirewall.DomainDeny;
        
        if (the_box.checked == true) {
                window.document.UbeeAdvancedFirewall.DomainAllow.checked = false;
        }
}

function AllowButton()
{
        var the_box = window.document.UbeeAdvancedFirewall.DomainAllow;
        
        if (the_box.checked == true) {
                window.document.UbeeAdvancedFirewall.DomainDeny.checked = false;
        }
}

function ContentFilterAlways()
{
        var the_box = window.document.UbeeAdvancedFirewall.FilterPolicyAlways;
        
        if (the_box.checked == true) {
                window.document.UbeeAdvancedFirewall.FilterPolicyTimeInterval.checked = false;
        }
}

function ContentFilterTimerInterval()
{
        var the_box = window.document.UbeeAdvancedFirewall.FilterPolicyTimeInterval;
        
        if (the_box.checked == true) {
                window.document.UbeeAdvancedFirewall.FilterPolicyAlways.checked = false;
        }
}

function AddTrustedClient()
{
	window.document.UbeeAdvancedFirewall.addTrustedClient.value = 1;
}

function RemoveTrustedClient()
{
	window.document.UbeeAdvancedFirewall.removeTrustedClient.value = 1;
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
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvConnectedDevicesList.asp"  id="ID_A_CONNECTED_DEVICES_LIST">Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_ADV_FIREWALL_TITLE" >Firewall</h1>
   <label id="ID_H1_ADV_FIREWALL_DESC"> This page allows configuration of Firewall features. It is highly recommended that the Firewall 
   is left enabled at all times for protection against Denial of Service attacks. </label>
  </div>
<form action=/goform/UbeeAdvancedFirewall method=POST name="UbeeAdvancedFirewall">
<table>
<tr>
  <td>
  <table>
    <tr>
<!-- upper left -->

<!-- upper right -->
<td valign=top>
<table>
<tr>
<td><label id="ID_LABEL_FIREWALL_IPV4_PROTECTION">IPv4 Firewall Protection</label></td><td><select name="AdvFirewall">
<option value=0 ><label id="ID_LABEL_IPV4_PROTECTION_OFF">Off</label><option value=1 selected><label id="ID_LABEL_IPV4_PROTECTION_LOW">Low</label><option value=2 ><label id="ID_LABEL_IPV4_PROTECTION_MED">Medium</label><option value=3 ><label id="ID_LABEL_IPV4_PROTECTION_HIGH">High</label></select></td>
</tr>







<tr><td>&nbsp;</td></tr>
<tr>
<td><label id="ID_LABEL_FIREWALL_BLOCKIP">Blocked Fragmented IP Packets</label></td><td><input type="CheckBox" name="AdvBlockIpFragments" value="0x800"  ><i><label id="ID_LABEL_FIREWALL_BLOCKIP_ENABLE">Enable</label></i></td>
</tr>

<tr>
<td><label id="ID_LABEL_FIREWALL_PORTSCAN">Port Scan Detection</label></td><td><input type="CheckBox" name="AdvPortScanDetection" value="0x4000"  ><i><label id="ID_LABEL_FIREWALL_PORTSCAN_ENABLE">Enable</label></i></td>
</tr>

<tr>
<td><label id="ID_LABEL_FIREWALL_SYNFLOOD">IP Flood Detection</label></td><td><input type="CheckBox" name="AdvSynFloodDetection" value="0x8000"  ><i><label id="ID_LABEL_FIREWALL_SYNFLOOD_ENABLE">Enable</label></i></td>
</tr>

    </table>
    </td>
</tr>
</table>
</td>

  <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td align=middle><label id="ID_LABEL_ALLOW_SERVICE">Allowed Services</label>
<table>
  <tr>
  <td>
  <div style="overflow:auto; height:210px; width:300px; border:1px solid #000000">
  <table cellpadding="0" cellspacing="0" style="width:275px;">
  <tr><td>&nbsp;No Ports Restricted</td></tr>
  </table>
  </div>
  </td>
  </tr>
</table>
</td>


</tr>
<!-- Middle -->
<tr><td colspan=2 align=middle><input type="Submit" value="Apply" align="MIDDLE" id="ID_BUTTON_APPLY_ADV_FIREWALL" ></td>
<!--</td></tr>-->
<!-- lower left -->

<!-- lower right -->
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

