<html>

<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway  VPN - Basic</title>
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

function CreateTunnel()
{
   window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 1;
}

function DeleteTunnel(index)
{
   window.document.UbeeVpnBasic.UbeeListIndex.value = index;
   window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 2;
}

function EditTunnel(index)
{
   window.document.UbeeVpnBasic.UbeeListIndex.value = index;
   window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 3;
}

function ConnectCommand(index)
{
    window.document.UbeeVpnBasic.UbeeListIndex.value = index;
	window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 4;
}

function DisconnectCommand(index)
{
    window.document.UbeeVpnBasic.UbeeListIndex.value = index;
	window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 5;
}

function EnableCommand(index)
{
    window.document.UbeeVpnBasic.UbeeListIndex.value = index;
	window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 6;
}

function DisableCommand(index)
{
    window.document.UbeeVpnBasic.UbeeListIndex.value = index;
	window.document.UbeeVpnBasic.UbeeTunnelCommand.value = 7;
}

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
        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeVpnBasic.asp"  id="ID_A_VPN_BASIC_L3" >Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeVpnIPSec.asp" id="ID_A_VPN_IPSEC_L3" >IPSec</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
   <h3 id="ID_A_VPN_BASIC" >Basic</h3>
   <label id="ID_LABEL_VPN_BASIC_DESC"> This page allows you to enable VPN protocols and manage VPN tunnels.</label>
  </div>

<form action=/goform/UbeeVpnBasic method=POST name="UbeeVpnBasic">
      <input type="hidden" name="UbeeTunnelCommand" value=0>
      <input type="hidden" name="UbeeListIndex" value=0>
      
      <!-- need comments to generate enums
      <select name="UbeeL2tpServerEnable" size=1 onChange="submit();"></select>
      <select name="UbeePptpServerEnable" size=1 onChange="submit();"></select>
      -->
      <B><font style="FONT-SIZE: 13pt" face="Arial">
      <label id="ID_LABEL_VPN_BASIC_IPSEC">IPSec</label></font></B><br>
      <table>
      <tr><td><label id="ID_LABEL_VPN_BASIC_IPSEC_ENDPOINT">IPSec Endpoint</label>&nbsp;<select name="UbeeIpsecEnable" size=1 onChange="submit();"><option value=0 selected><label id="ID_LABEL_VPN_BASIC_IPSEC_DISABLE">Disabled</label><option value=1 ><label id="ID_LABEL_VPN_BASIC_IPSEC_ENABLE">Enabled</label></select></td></tr>
      </table>
      <table border="1" cellspacing="0" width="100%" id="AutoNumber2" cellpadding="0" style="border-width: 0">
      <tr>
        <td style="padding: 0" align="center" width="5%">
        <p style="margin-top: 0; margin-bottom: 0"><b>#</b></td>
        <td style="padding: 0" align="center" width="25%">
        <p style="margin-top: 0; margin-bottom: 0"><b><label id="ID_LABEL_VPN_BASIC_NAME">Name</label></b></td>
        <td style="padding: 0" align="center" width="20%">
        <p style="margin-top: 0; margin-bottom: 0"><b><label id="ID_LABEL_VPN_BASIC_STATUS">Status</label></b></td>
        <td style="padding: 0" align="center" width="20%">
        <p style="margin-top: 0; margin-bottom: 0"><b><label id="ID_LABEL_VPN_BASIC_CONTROL">Control</label></b></td>
        <td style="padding: 0" align="center" width="20%">
        <p style="margin-top: 0; margin-bottom: 0"><b><label id="ID_LABEL_VPN_BASIC_CONFIG">Configure</label></b></td>
      </tr>
      
      <tr>
        <td style="padding: 0" align="center" colspan="5" width="5%">
        <p style="margin-top: 0; margin-bottom: 0">
        <input id="ID_BUTTON_VPN_BASIC_ADDTUNNEL" type="submit" value="Add New Tunnel..." style="float: left" onClick="CreateTunnel();"></td>
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
