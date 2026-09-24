<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway  LAN DHCP </title>
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

function EnableButton()
{
        var the_box = window.document.UbeeLanDhcp.DhcpServerEnable;

        if (the_box.checked == true) {
                window.document.UbeeLanDhcp.DhcpServerDisable.checked = false;
        }
}

function DisableButton()
{
        var the_box = window.document.UbeeLanDhcp.DhcpServerDisable;

        if (the_box.checked == true) {
                window.document.UbeeLanDhcp.DhcpServerEnable.checked = false;
        }
}

function ApplyButton()
{
    window.document.UbeeLanDhcp.ApplyAction.value = 1;
}

function CheckLastIPRange_start(IP)
{
    var ipVal;
    ipVal = parseInt(IP.value);

    //except x.x.x.255
    if(IP.value > 254 || IP.value <2 || (isNaN(ipVal) == true))
    {
        alert("Warning - Invalid DHCP Start IP");
        window.location.reload();
        return;
    }
}
function CheckLastIPRange_end(IP)
{
    var ipVal;
    ipVal = parseInt(IP.value);

    //except x.x.x.255
    if(IP.value > 254 || IP.value <2 || (isNaN(ipVal) == true))
    {
        alert("Warning - Invalid DHCP End IP");
        window.location.reload();
        return;
    }
}

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}



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
        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN_SETUP" >Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeLanDhcp.asp"  id="ID_A_LAN_DHCP" >DHCP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanStaticLease.asp" id="ID_A_LAN_STATICLEASE">Static Lease</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_LAN_DHCP_TITLE" >LAN DHCP</h1>
   <label id="ID_LABEL_LAN_DHCPV4_DESC"> This page allows configuration and status of the optional internal DHCP server for the LAN.</label>
  </div>

<form action=/goform/UbeeLanDhcp method=POST name="UbeeLanDhcp">

<table>
<tr valign=top>
<td>

<h3 id="ID_H3_HEADER_LAN_DHCPV4_MODE_TITLE" >DHCP Mode</h3>
<table>
<tr valign>
<td><label id="ID_LABEL_DHCPV4_SERVER_ENABLE_TITLE">DHCP Server</label></td>

<td><input type="radio" name="DhcpServerEnable" value="0x1000" CHECKED onClick="EnableButton();" ><label id="ID_LABEL_DHCPV4_SERVER_ENABLE_ON">Yes</label></td>
<td><input type="radio" name="DhcpServerDisable" value="0x1000"   onClick="DisableButton();" ><label id="ID_LABEL_DHCPV4_SERVER_ENABLE_OFF">No</label></td>
</tr>
<tr valign>
  <td><input type="Submit" value="Apply" align="MIDDLE" onClick="ApplyButton();" id="ID_BUTTON_DHCPV4_SERVER_ENABLE_APPLY"></td>
  <td>&nbsp;</td>
  <td>&nbsp;</td>
</tr>
</table>

<hr noshade="noshade">
<h3 class="module" id="ID_H3_HEADER_LAN_DHCPV4_SETTINGS_TITLE" >DHCP Settings</h3>
<table>
<tr valign>
<td><label id="ID_LABEL_LAN_DHCPV4_START_IP">DHCP Start IP</label></td>
<td><b>



<input name="DhcpIpStart0" type="text" size=3 maxlength=3 value=192 disabled="disabled" >.<input name="DhcpIpStart1" type="text" size=3 maxlength=3 value=168 disabled="disabled" >.<input name="DhcpIpStart2" type="text" size=3 maxlength=3 value=0 disabled="disabled" >.<input name="DhcpIpStart3" type="text" size=3 maxlength=3 value=10  onchange="CheckLastIPRange_start(this);">
</b></td></tr>
<tr valign>
<td><label id="ID_LABEL_LAN_DHCPV4_END_IP">DHCP End IP</label></td>
<td>


<input name="DhcpIpEnd0" type="text" size=3 maxlength=3 value=192 disabled="disabled" >.<input name="DhcpIpEnd1" type="text" size=3 maxlength=3 value=168 disabled="disabled" >.<input name="DhcpIpEnd2" type="text" size=3 maxlength=3 value=0 disabled="disabled" >.<input name="DhcpIpEnd3" type="text" size=3 maxlength=3 value=254  onchange="CheckLastIPRange_end(this);"> </td>
</tr>
<tr valign>
<td><label id="ID_LABEL_LAN_DHCPV4_LEASE_TIME">Lease Time</label></td>
<td><input type="text" name="LeaseTime" size="10" maxlength="10" value=3600></td>
</tr>
</table>

</td>

</tr>
<tr>
<td colspan=3 align=left><input type="Submit" value="Apply" align="MIDDLE" onClick="ApplyButton();" id="ID_BUTTON_DHCPV4_SERVER_SETTING_APPLY">
                         <input type="hidden" name="ApplyAction" value=></td>
</tr>
<br>
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
