<html>

<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway WLAN Access Control</title>
<script src="js/jquery-1.10.2.js"></script>
<script src="js/ubee_js_apis.js"></script>
<script LANGUAGE="javascript">


var web_item_data_wireless_page_setup_jsonData =  ' { "wireless_2g_page_enable": 1, "wireless_5g_page_enable": 1 }'  ;
var web_item_data_wireless_page_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_page_setup_jsonData);



var language_jsonData = ' { "web_language": 0 } ' ;
var language_jsonObj = jQuery.parseJSON(language_jsonData); 

function disablePages()
{
	if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable == 0)
	{
		$("div#DESCRIPTION_2G").hide();
		$("div#MAIN_PAGE_2G").hide();
	}
	
	if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable == 0)
	{
		$("div#DESCRIPTION_5G").hide();
		$("div#MAIN_PAGE_5G").hide();
	}
}


$(function() {

disablePages();

if ( !ubee_multi_language_control() )
{
	MultiLanguage_Hide();
}
else 
{
	
//  var page = document.location.href.match(/[^\/]+$/)[0].split(".")[0];
    var pathArray = window.location.pathname.split( '?' );
	    var page = pathArray[0].split(".")[0].replace(/\//g,'');
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

function commitAccess(band)
{
	if(band == 0)
	{
		window.document.UbeeWlanAccessControl.commitwlanAccess.value = 1;
	} 
	else 
	{
		window.document.UbeeWlanAccessControl5G.commitwlanAccess5G.value = 1;
	}
}

function onLoadScript()
{
   
}

function wlanAccessChangeMbssIndex(band)
{
	if (band == 0 ) 
	{
	   window.document.UbeeWlanAccessControl.wlanAccessMbssIndexChanged.value = 1;
	   window.document.UbeeWlanAccessControl.submit();
	}
	else
	{
	   window.document.UbeeWlanAccessControl.wlanAccessMbssIndexChanged5G.value = 1;
	   window.document.UbeeWlanAccessControl.submit();
	}
}

function checkMacRestrictWps2Dialog(band)
{
	if (band == 0 ) 
	{
		if((window.document.UbeeWlanAccessControl.MacRestrictMode.value == 1) &&
		  (window.document.UbeeWlanAccessControl.WirelessMac01.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac09.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac02.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac10.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac03.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac11.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac04.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac12.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac05.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac13.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac06.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac14.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac07.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac15.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac08.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac16.value == "")) 
		  {
			if(!confirm("Setting MAC Restrict Mode to Allow with empty MAC addresses will disable WPS. Do you want to continue?")){
				window.document.UbeeWlanAccessControl.MacRestrictMode.value = 0;
			}
		}
	}
	else 
	{
		if((window.document.UbeeWlanAccessControl.MacRestrictMode5G.value == 1) &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G01.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G09.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G02.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G10.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G03.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G11.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G04.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G12.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G05.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G13.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G06.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G14.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G07.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G15.value == "") &&
		  (window.document.UbeeWlanAccessControl.WirelessMac5G08.value == "")&&(window.document.UbeeWlanAccessControl.WirelessMac5G16.value == "")) 
		  {
			if(!confirm("Setting MAC Restrict Mode to Allow with empty MAC addresses will disable WPS. Do you want to continue?")){
				window.document.UbeeWlanAccessControl.MacRestrictMode5G.value = 0;
			}
		}
	}
}

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}
// show me -->

function onLoadScript()
{
   
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
                 <font id="ID_LABEL_WEB_LANGUAGE"  color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
<div id="navigation_bar">
	  <ul>
			<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanBasic.asp" id="ID_A_BASIC">Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanSecurity.asp" id="ID_A_SECURITY" >Security</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanWPS.asp" id="ID_A_WPS">WPS</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeWlanAccessControl.asp" id="ID_A_ACL" >Access Control</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div> 

		      </ul>
			  </div>
			<div id="main_page">
			  <div class="description" id="DESCRIPTION_2G">
    <h1 id="ID_H1_WIRELESS_ACCESS_HEADER_TITLE_2G">Wireless 2.4G Access Control</h1>
    
  <label id="ID_LABEL_WIRELESS_ACCESS_HEADER_DESC_2G"> This page allows configuration of the Access Control to the AP as well as status on the connected clients.</label>
  </div>
<div id="MAIN_PAGE_2G">
<form action=/goform/UbeeWlanAccessControl method=POST name="UbeeWlanAccessControl">
<br>

<br>

<table> 
<tr><td align=right><label id="ID_LABEL_WIRELESS_ACCESS_HEADER_MODE_2G">MAC Restrict Mode</label></td><td><select name="MacRestrictMode" onChange="submit();"><option value=0 selected>Disabled<option value=1 >Allow<option value=2 >Deny</select></td><td>&nbsp;</td></tr>

<tr><td align=right><label id="ID_LABEL_WIRELESS_MAC_ADDRESS_2G">MAC Addresses</label></td><td><input type="text" name="WirelessMac01" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac09"size=17 maxlength=17  value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac02" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac10" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac03" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac11" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac04" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac12" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac05" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac13" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac06" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac14" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac07" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac15" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac08" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac16" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="submit" value="Apply" onClick="commitAccess(0);" id="ID_BUTTON_APPLY_WIRELESS_ACL_2G" ></td><td><input type="hidden" name="commitwlanAccess" value=0 ></td></tr>
</table>
</form>
<table>
  
  <tr valign=top>
    <td align=right><label id="ID_LABEL_HEADER_CONNECTED_CLIENT_2G">Connected Clients</label></td>
    <td><table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_2G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_2G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_2G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_2G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_2G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_2G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_2G">Speed</label> (kbps)</td></tr><tr><td colspan=5><label id="ID_LABEL_NO_STA_DESC_2G">No wireless clients are connected.</label></td></tr>
    </table></td>
  </tr>
</table>
</div>

<hr/>
 <div class="description" id="DESCRIPTION_5G">
    <h1 id="ID_H1_WIRELESS_ACCESS_HEADER_TITLE_5G">Wireless 5G Access Control</h1>
    
 <label id="ID_LABEL_WIRELESS_ACCESS_HEADER_DESC_5G" > This page allows configuration of the Access Control to the AP as well as status on the connected clients.</label></div>
<div id="MAIN_PAGE_5G">
<form action=/goform/UbeeWlanAccessControl method=POST name="UbeeWlanAccessControl5G">
<br>


<table> 
<tr><td align=right><label id="ID_LABEL_WIRELESS_ACCESS_HEADER_MODE_5G">MAC Restrict Mode</label></td><td><select name="MacRestrictMode5G" onChange="submit();"><option value=0 selected>Disabled<option value=1 >Allow<option value=2 >Deny</select></td><td>&nbsp;</td></tr>

<tr><td align=right><label id="ID_LABEL_WIRELESS_MAC_ADDRESS_5G">MAC Addresses</label></td><td><input type="text" name="WirelessMac5G01" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G09"size=17 maxlength=17  value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G02" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G10" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G03" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G11" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G04" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G12" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G05" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G13" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G06" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G14" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G07" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G15" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="text" name="WirelessMac5G08" size=17 maxlength=17 value=""></td><td><input type="text" name="WirelessMac5G16" size=17 maxlength=17 value=""></td></tr>
<tr><td align=right>&nbsp;</td><td><input type="submit" value="Apply" onClick="commitAccess(1);" id="ID_BUTTON_APPLY_WIRELESS_ACL_5G"></td><td><input type="hidden" name="commitwlanAccess5G" value=0 ></td></tr>
</table>
</form>
<table>
  
  <tr valign=top>
    <td align=right><label id="ID_LABEL_HEADER_CONNECTED_CLIENT_5G">Connected Clients</label></td>
    <td><table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_5G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_5G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_5G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_5G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_5G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_5G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_5G">Speed</label> (kbps)</td></tr><tr><td colspan=5><label id="ID_LABEL_NO_STA_DESC_5G">No wireless clients are connected.</label></td></tr>
    </table></td>
  </tr>
</table>
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
