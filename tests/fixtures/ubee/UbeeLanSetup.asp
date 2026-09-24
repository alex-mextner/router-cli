<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway LAN Setup </title>
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

function ApplyRgSetupButton()
{
    window.document.UbeeLanSetup.ApplyRgLanSetupAction.value = 1;
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
        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeLanSetup.asp"  id="ID_A_LAN_SETUP" >Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanDhcp.asp" id="ID_A_LAN_DHCP">DHCP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanStaticLease.asp" id="ID_A_LAN_STATICLEASE">Static Lease</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_A_LAN_SETUP" >LAN Setup</h1>
   <label id="ID_LABEL_LAN_SETUP_DESC"> This page allows configuration of the basic features of the broadband gateway related to your LAN connection.</label>
  </div>

<form action=/goform/UbeeLanSetup method=POST name="UbeeLanSetup">

<table>
<tr valign=top>
<td>
<table>
<tr>
<td colspan=3 align=center></td>
</tr>
<tr><td></td><td><label id="ID_LABEL_MAC_ADDRESS">MAC Address</label></td><td><b>
02:00:00:00:01:1a
</b></td></tr>
<tr><td>&nbsp;</td><td><label id="ID_LABEL_IP_ADDRESS">IP Address:</label></td><td>192.
168.
<input   name="LocalIpAddressIP2" type="text" size=3 maxlength=3 value=0><b>.</b>
1
<tr><td>&nbsp;</td><td><label id="ID_LABEL_SUBNET_MASK">Subnet Mask:</label></td><td>255.
255.
255.
0
<tr><td>&nbsp;</td><td><label id="ID_LABEL_DNS1">Primary DNS</label></td><td><input name="PrimaryDnsIpAddressIP0" type="text" size=3 maxlength=3 value=198><b>.</b><input name="PrimaryDnsIpAddressIP1" type="text" size=3 maxlength=3 value=51><b>.</b><input name="PrimaryDnsIpAddressIP2" type="text" size=3 maxlength=3 value=100><b>.</b><input name="PrimaryDnsIpAddressIP3" type="text" size=3 maxlength=3 value=30></td></tr><tr><td>&nbsp;</td><td><label id="ID_LABEL_DNS2">Secondary DNS</label></td><td><input name="SecondaryDnsIpAddressIP0" type="text" size=3 maxlength=3 value=198><b>.</b><input name="SecondaryDnsIpAddressIP1" type="text" size=3 maxlength=3 value=51><b>.</b><input name="SecondaryDnsIpAddressIP2" type="text" size=3 maxlength=3 value=100><b>.</b><input name="SecondaryDnsIpAddressIP3" type="text" size=3 maxlength=3 value=40></td></tr><tr><td>&nbsp;</td><td><label id="ID_LABEL_DNS3">Third DNS</label></td><td><input name="ThirdDnsIpAddressIP0" type="text" size=3 maxlength=3 value=198><b>.</b><input name="ThirdDnsIpAddressIP1" type="text" size=3 maxlength=3 value=51><b>.</b><input name="ThirdDnsIpAddressIP2" type="text" size=3 maxlength=3 value=100><b>.</b><input name="ThirdDnsIpAddressIP3" type="text" size=3 maxlength=3 value=50></td></tr>
<!-- TRW - need to list all possible controls to generate the enums.
      <input name="PrimaryDnsIpAddressIP0" type="text" size=3 maxlength=3 value=>
      <input name="PrimaryDnsIpAddressIP1" type="text" size=3 maxlength=3 value=>
      <input name="PrimaryDnsIpAddressIP2" type="text" size=3 maxlength=3 value=>
      <input name="PrimaryDnsIpAddressIP3" type="text" size=3 maxlength=3 value=>
      <input name="SecondaryDnsIpAddressIP0" type="text" size=3 maxlength=3 value=>
      <input name="SecondaryDnsIpAddressIP1" type="text" size=3 maxlength=3 value=>
      <input name="SecondaryDnsIpAddressIP2" type="text" size=3 maxlength=3 value=>
      <input name="SecondaryDnsIpAddressIP3" type="text" size=3 maxlength=3 value=>
      <input name="ThirdDnsIpAddressIP0" type="text" size=3 maxlength=3 value=>
      <input name="ThirdDnsIpAddressIP1" type="text" size=3 maxlength=3 value=>
      <input name="ThirdDnsIpAddressIP2" type="text" size=3 maxlength=3 value=>
      <input name="ThirdDnsIpAddressIP3" type="text" size=3 maxlength=3 value=>
-->
<tr><td>&nbsp;</td><td> <label id="ID_LABEL_DOMAIN_NAME"> Domain Name</label></td><td> <input name="DomainName" type="text" size=15 maxlength=255 value=></td></tr>
</td></tr>
</table>
</td>
</tr>
<tr>
<td colspan=3 align=center><input type="Submit" value="Apply" align="MIDDLE" onClick="ApplyRgSetupButton()" id="ID_BUTTON_APPLY_LAN_SETUP" >
<input type="hidden" name="ApplyRgLanSetupAction" value="0"></td>
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
   		<div id="copyright">©2021 Ubee Interactive. All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->
</body>
</html>
