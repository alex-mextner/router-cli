<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Parental Control - Time of Day Access Policy</title>
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
function AddTodClient(index)
{
	window.document.UbeeParentalTimeFilter.addTodClient.value = 1;
}

function RemoveTodClient(index)
{
	window.document.UbeeParentalTimeFilter.removeTodClient.value = 1;
}

function clearAllDays()
{
	window.document.UbeeParentalTimeFilter.BlockSunday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockMonday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockTuesday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockWednesday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockThursday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockFriday.checked = false;
	window.document.UbeeParentalTimeFilter.BlockSaturday.checked = false;
}

function clearEveryDay()
{
	window.document.UbeeParentalTimeFilter.BlockEveryDay.checked = false;
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
	<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_USER_SETUP">User Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalBasic.asp" id="ID_A_BASIC_SETUP">Basic Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeParentalTimeFilter.asp" id="ID_A_TIME_FILTER">Time Filter</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_TIME_FILTER">Parental Control - Time of Day Access Policy</h1>
    <label id="ID_LABEL_TIME_FILTER_DESC">This page allows configuration of time access policies to block all internet traffic to and from specific network devices based on time of day settings.</label>
  </div>
<form action=/goform/UbeeParentalTimeFilter method=POST name="UbeeParentalTimeFilter">
<table>
<tr>
<td>

<tr>
<td align=left><h3 id="ID_H3_TIME_ACCESS_POLICY_CONF"><b>Time Access Policy Configuration </b></h3> 
<label id="ID_LABEL_TIME_ACCESS_POLICY_CONF_DESC">Create a new policy by giving it a descriptive name.</label></td>
</tr>

<tr>
<td>
<input type="text" name="TodClient" size="20" maxlength="20" value= >
<input type="submit" value="Add New Policy" onClick="AddTodClient();" id="ID_BUTTON_POLICY_ADD"><input type="hidden" name="addTodClient" value=0></td>
</tr>
<tr>
<td>&nbsp;</td>
</tr>
<tr>
<td align=left><b><label id="ID_LABEL_TIME_ACCESS_POLICY_LIST">Time Access Policy List</label></b></td>
</tr>

<tr>
<td><select name="ToDComputers" onChange="submit();"><option vlue=0>No filters entered.</select><input type="hidden" name="removeTodClient" value=0>
<input type="checkbox" name="TodBlockingEnabled" value=0x01 ><label id="ID_LABEL_POLICY_ENABLE">Enabled</label>
<input type="submit" value="Remove" onClick="RemoveTodClient();" id="ID_BUTTON_POLICY_REMOVE"></td>
</tr>
</table>
<table>
<tr><td colspan=4 align="left"><label id="ID_LABEL_DAYS_TO_BLOCK">Days to Block</label></td></tr>
<tr>
	<td><input type="checkbox" name="BlockEveryDay" onclick="clearAllDays();" value=0x01 ><label id="ID_LABEL_DAYS_FILT_EVERYDAY">Everyday</label></td>
	<td><input type="checkbox" name="BlockSunday" onclick="clearEveryDay();" value=1 ><label id="ID_LABEL_DAYS_FILT_SUNDAY">Sunday</label></td>
	<td><input type="checkbox" name="BlockMonday" onclick="clearEveryDay();" value=2 ><label id="ID_LABEL_DAYS_FILT_MONDAY">Monday</label></td>
	<td><input type="checkbox" name="BlockTuesday" onclick="clearEveryDay();" value=4 ><label id="ID_LABEL_DAYS_FILT_TUESDAY">Tuesday</label></td>
</tr>
<tr>
	<td><input type="checkbox" name="BlockWednesday" onclick="clearEveryDay();" value=8 ><label id="ID_LABEL_DAYS_FILT_WEDNESDAY">Wednesday</label></td>
	<td><input type="checkbox" name="BlockThursday" onclick="clearEveryDay();" value=16 ><label id="ID_LABEL_DAYS_FILT_THURSDAY">Thursday</label></td>
	<td><input type="checkbox" name="BlockFriday" onclick="clearEveryDay();" value=32 ><label id="ID_LABEL_DAYS_FILT_FRIDAY">Friday</label></td>
	<td><input type="checkbox" name="BlockSaturday" onclick="clearEveryDay();" value=64 ><label id="ID_LABEL_DAYS_FILT_SATURDAY">Saturday</label></td>
</tr>
</table>
<table>
<tr><td colspan=4 align="left"><label id="ID_LABEL_TIME_TO_BLOCK">Time to Block</label></td></tr>
<tr>
	<td colspan=4 align="left"><input type="checkbox" name="AllDay" value=0x01 ><label id="ID_LABEL_TIME_FILT_ALLDAY">All day</label></td>
</tr>
<tr>
	<td><label id="ID_LABEL_TIME_START">Start:</label></td><td><input type="text" size="4" name="StartHour" value=12>(<label id="ID_LABEL_TIME_FILT_HOUR">hour</label>)</td>
	<td><input type="text" size="4" name="StartMinute" value=00>(<label id="ID_LABEL_TIME_FILT_MIN">min</label>)</td>
	<td><select name="StartAmPm"><option value=1 selected>AM<option value=2 >PM</select></td>
</tr>
<tr>
	<td><label id="ID_LABEL_TIME_END">End:</label></td><td><input type="text" size="4"  name="EndHour" value=12>(<label id="ID_LABEL_TIME_FILT_HOUR1">hour</label>)</td>
	<td><input type="text" size="4"  name="EndMinute" value=00>(<label id="ID_LABEL_TIME_FILT_MIN1">min</label>)</td>
	<td><select name="EndAmPm"><option value=1 selected>AM<option value=2 >PM</select></td>
</tr>
</table>
<table>
<tr><td colspan=4 align="left"><label id="ID_LABEL_PORT_BLOCK">Ports to Block</label></td></tr>
<tr><td colspan=4 align="left"><input type="checkbox" name="PortCheckEnable" value=0 ><label id="ID_LABEL_PORT_BLOCK_ENABLE">Enabled</label></td></tr>

<tr>
<td><label id="ID_LABEL_PORT_START">Port Start:</label></td><td><input type="text" size="5" name="PortStart" value=0></td>
</tr>

<tr>
<td><label id="ID_LABEL_PORT_END">Port End:</label></td><td><input type="text" size="5" name="PortEnd" value=0></td>
</tr>

<tr>
<td><label id="ID_LABEL_PORT_PROTOCOL">Protocol:</label></td><td><select name="PortProtocol"><option value=3 >UDP<option value=4 >TCP<option value=254 >Both</select></td>
</tr>

<tr><td colspan=4 align="center"><input type="submit" value="Apply" id="ID_LABEL_TIME_FILTER_APPLY"></td></tr>
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
