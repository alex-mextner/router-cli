<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title> Residential Gateway Wlan Basic </title>
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

 
function commitRadio(band)
{
	if(band == 0)
	{
		window.document.wlanRadio.commitwlanRadio.value = 1;
	}
	else
	{
		window.document.wlanRadio5G.commitwlanRadio5G.value = 1;
	}
}

function restoreDefaults(band)
{
	if(band == 0)
	{
    	window.document.wlanRadio.restoreWirelessDefaults.value = 1;
		window.document.wlanRadio.commitwlanRadio.value = 1;
	}
	else
	{
    	window.document.wlanRadio5G.restoreWirelessDefaults5G.value = 1;
		window.document.wlanRadio5G.commitwlanRadio5G.value = 1;
	}
}

function CheckScanPopup()
{
   
}

function openScanWindow()
{
   window.document.wlanRadio.scanActions.value = 1;
}

function channelChanged(band )
{
	if(band == 0)
	{
		if(window.document.wlanRadio.ChannelNumber.selectedIndex == 0)
		{
			window.document.wlanRadio.ObssCoexistence.selectedIndex = 1;
		}
		else
		{
			window.document.wlanRadio.NBandwidth.disabled = false;
			window.document.wlanRadio.ObssCoexistence.disabled = false;
		}
		    window.document.wlanRadio.submit();
	}
	else
	{
		if(window.document.wlanRadio5G.ChannelNumber5G.selectedIndex == 0)
		{
			window.document.wlanRadio5G.ObssCoexistence5G.selectedIndex = 1;
		}
		else
		{
			window.document.wlanRadio5G.NBandwidth5G.disabled = false;
			window.document.wlanRadio5G.ObssCoexistence5G.disabled = false;
		}
		    window.document.wlanRadio5G.submit();
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

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}

function onLoadScript()
{
   
}

</script>
</head>

<body onLoad="CheckScanPopup(); onLoadScript()">
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
			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3boxl3box-final"><a class="current" href="UbeeWlanBasic.asp" id="ID_A_BASIC" >Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanSecurity.asp" id="ID_A_SECURITY" >Security</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanWPS.asp" id="ID_A_WPS">WPS</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanAccessControl.asp"  id="ID_A_ACL">Access Control</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		      </ul>
			  </div>
<div id="main_page">
  <div class="description" id="DESCRIPTION_2G">
    <h1 id="ID_H1_HEADER_WIRELESS_2G_TITLE">Wireless 2.4G Basic</h1>
    <label id="ID_LABEL_DESCRIPTION_2G">This page allows configuration of the Wireless 2.4G configuration including current channel number.</label>
  </div>
<form action=/goform/UbeeWlanBasic method=POST name="wlanRadio">
<div id="MAIN_PAGE_2G">
<table> 

	<tr><td align=right><label id="ID_LABEL_WIRELESS_ON_2G" > Wireless</label></td><td><select   name="WirelessEnable"><option value=1 >Enabled<option value=0 selected>Disabled</select></td></tr>

    <tr><td align=right><label id="ID_LABEL_NETWORK_NAME_2G" >Network Name (SSID)</label></td><td><input name="ServiceSetIdentifier" size=32 maxlength=32 value="TESTNET"></td></tr>
    <td align=right><label id="ID_LABEL_HIDE_NETWORK_2G" >Hidden SSID</label></td><td><select name="ClosedNetwork" "><option value=0 selected>Disabled<option value=1 >Enabled</select></td></tr>
   
	<tr><td align=right><label id="ID_LABEL_WIRELESS_MODE_2G" >802.11 mode</label></td><td><select name="NMode" size=1 onChange="submit();"><option value=0 >B/G/N-mix<option value=1 selected>G/N-mix<option value=2 >B/G-mix<option value=3 >N-only</select>&nbsp;</td></tr>
	
	<tr><td align=right><label id="ID_LABEL_OUTPUTPOWER_2G">Output Power</label></td><td><select name="OutputPower" size=1><option value=25 >25%<option value=50 >50%<option value=75 >75%<option value=100 selected>100%</select></td></tr>

    <tr><td align=right><label id="ID_LABEL_CHANNEL_2G" >Control Channel</label></td><td><select name="ChannelNumber" onChange="channelChanged(0);"><option value=0 >Auto<option value=1 >1 <option value=2 >2 <option value=3 >3 <option value=4 >4 <option value=5 >5 <option value=6 selected>6 <option value=7 >7 <option value=8 >8 <option value=9 >9 <option value=10 >10 <option value=11 >11 <option value=12 >12 <option value=13 >13 </select>

    </td></tr>

    <tr><td align=right><label id="ID_LABEL_CHANNEL_BANDWIDTH_2G" >Bandwidth</label></td><td><select   name="NBandwidth" size=1 onChange="submit();"><option value=20 selected>20 MHz<option value=40 >40 MHz</select>
    &nbsp;&nbsp;Current&nbsp;:&nbsp; 20MHz</td></tr>

    <tr><td align=right><label id="ID_LABEL_CONTROL_SIDE_BAND_2G" >Sideband for Control Channel (40 MHz only)</label></td><td><select name="NSideband" size=1 onChange="submit();" disabled><option value=-1 >Lower<option value=0 selected>None<option value=1 >Upper</select>
    

<tr><td>&nbsp;</td></tr>
<tr>
<td colspan=2 align=center><input type="Submit" id="ID_BUTTON_APPLY_2G"  align="MIDDLE"onClick="commitRadio(0);" value="Apply" >
                           <input type="hidden" name="restoreWirelessDefaults" value=0 >
                           <input type="hidden" name="commitwlanRadio" value=0 > 
                           <input name="ID_BUTTON_RESET_DEFAULT" type="Submit" id="ID_BUTTON_RESET_DEFAULT_2G" onClick="restoreDefaults(0);" value="Restore Wireless Defaults" align="MIDDLE"></td>
</tr>
<tr><td colspan=2><br><hr></td></tr>
    
</table>
</div>
<br><hr><br>
</form>

<div class="description" id="DESCRIPTION_5G">
  <h1 id="ID_H1_HEADER_WIRELESS_5G_TITLE">Wireless 5G Basic</h1>
<label id="ID_LABEL_DESCRIPTION_5G">  This page allows configuration of the Wireless 5G configuration including current channel number. </label></div>
<form action=/goform/UbeeWlanBasic method=POST name="wlanRadio5G">

<div id="MAIN_PAGE_5G">

  <table>
    <tr><td align=right><label id="ID_LABEL_WIRELESS_ON_5G" >Wireless</label></td><td><select   name="WirelessEnable5G"><option value=1 >Enabled<option value=0 selected>Disabled</select></td></tr>

    <tr><td align=right><label id="ID_LABEL_NETWORK_NAME_5G" >Network Name (SSID)</label></td><td><input name="ServiceSetIdentifier5G" size=32 maxlength=32 value="TESTNET"></td></tr>
    <td align=right><label id="ID_LABEL_HIDE_NETWORK_5G" >Hidden SSID</label></td><td><select name="ClosedNetwork5G" "><option value=0 selected>Disabled<option value=1 >Enabled</select></td></tr>
   
	<tr><td align=right><label id="ID_LABEL_WIRELESS_MODE_5G" >802.11 mode</label></td><td><select name="NMode5G" size=1 onChange="submit();"><option value=4 selected>A/N/AC-mix<option value=7 >N/AC-mix<option value=6 >AC-only<option value=5 >A-only</select>&nbsp;</td></tr>
	    
	<tr><td align=right><label id="ID_LABEL_OUTPUTPOWER_5G">Output Power</label></td><td><select name="OutputPower5G" size=1><option value=25 >25%<option value=50 >50%<option value=75 >75%<option value=100 selected>100%</select></td></tr>

    <tr><td align=right><label id="ID_LABEL_CHANNEL_5G" >Control Channel</label></td><td><select name="ChannelNumber5G" onChange="channelChanged(1);"><option value=0 >Auto<option value=36 selected>36 <option value=40 >40 <option value=44 >44 <option value=48 >48 <option value=52 >52 <option value=56 >56 <option value=60 >60 <option value=64 >64 <option value=100 >100 <option value=104 >104 <option value=108 >108 <option value=112 >112 <option value=116 >116 <option value=120 >120 <option value=124 >124 <option value=128 >128 <option value=132 >132 <option value=136 >136 <option value=140 >140 </select>

    </td></tr>

    <tr><td align=right><label id="ID_LABEL_CHANNEL_BANDWIDTH_5G" >Bandwidth</label></td><td><select   name="NBandwidth5G" size=1 onChange="submit();"><option value=20 selected>20 MHz<option value=40 >40 MHz<option value=80 >80 MHz</select>
    &nbsp;&nbsp;Current&nbsp;:&nbsp; 20MHz</td></tr>

    <tr><td align=right><label id="ID_LABEL_CONTROL_SIDE_BAND_5G" >Sideband for Control Channel (40 MHz only)</label></td><td><select name="NSideband5G" size=1 onChange="submit();" disabled><option value=-1 >Lower<option value=0 selected>None<option value=1 >Upper</select>
    
    <tr>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td colspan=2 align=center>
        <input name="ID_BUTTON_APPLY" type="Submit" id="ID_BUTTON_APPLY_5G" onClick="commitRadio(1);" value="Apply" align="MIDDLE" >
        <input type="hidden" name="restoreWirelessDefaults5G" value=0 >
        <input type="hidden" name="commitwlanRadio5G" value=0 >
        <input name="ID_BUTTON_RESET_DEFAULT" type="Submit" id="ID_BUTTON_RESET_DEFAULT_5G" onClick="restoreDefaults(1);" value="Restore Wireless Defaults" align="MIDDLE" ></td>
    </tr>
  </table>
</div>
</form>
<br><br><br><br>

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
