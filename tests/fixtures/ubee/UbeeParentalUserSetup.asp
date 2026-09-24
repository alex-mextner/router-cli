<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Parental Control - User Setup</title>
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

function addUser()
{
	window.document.UbeeParentalUserSetup.AddUser.value = 1;
}

function removeUser()
{
	window.document.UbeeParentalUserSetup.RemoveUser.value = 1;
}

function trustedUser()
{
	var trustedUser = window.document.UbeeParentalUserSetup.cbTrustedUser;
	var selectUserRules = window.document.UbeeParentalUserSetup.UserRules;
	var selectTodRule = window.document.UbeeParentalUserSetup.TodRule;
	var whiteListOnly = window.document.UbeeParentalUserSetup.cbWhiteListOnly;

	if (trustedUser.checked == true) 
	{
		selectUserRules.disabled = true;
		selectTodRule.disabled = true;
		whiteListOnly.disabled = true;
	}
	else
	{                
		selectUserRules.disabled = false;
		selectTodRule.disabled = false;
		whiteListOnly.disabled = false;
	}
}

function enableUser()
{
	var enableUser = window.document.UbeeParentalUserSetup.cbEnableUser;
	var userPassword = window.document.UbeeParentalUserSetup.UserPassword;
	var userPasswordReEnter = window.document.UbeeParentalUserSetup.UserPasswordReEnter;
	var selectUserRules = window.document.UbeeParentalUserSetup.UserRules;
	var selectTodRule = window.document.UbeeParentalUserSetup.TodRule;
	var sessionDuration = window.document.UbeeParentalUserSetup.SessionDuration;
	var inactivityTime = window.document.UbeeParentalUserSetup.InactivityTime;
	var trustedUser = window.document.UbeeParentalUserSetup.cbTrustedUser;
	var whiteListOnly = window.document.UbeeParentalUserSetup.cbWhiteListOnly;

	if (enableUser.checked == true) 
	{
		userPassword.disabled = false;
		userPasswordReEnter.disabled = false;
		selectUserRules.disabled = false;
		selectTodRule.disabled = false;
		sessionDuration.disabled = false;
		inactivityTime.disabled = false;
		trustedUser.disabled = false;
		whiteListOnly.disabled = false;
	}
	else
	{                
		userPassword.disabled = true;
		userPasswordReEnter.disabled = true;
		selectUserRules.disabled = true;
		selectTodRule.disabled = true;
		sessionDuration.disabled = true;
		inactivityTime.disabled = true;
		trustedUser.disabled = true;
		whiteListOnly.disabled = true;
	}
}

function AddTrustedClient()
{
	window.document.UbeeParentalUserSetup.addTrustedClient.value = 1;
}

function RemoveTrustedClient()
{
	window.document.UbeeParentalUserSetup.removeTrustedClient.value = 1;
}

function configureUser()
{
	window.document.UbeeParentalUserSetup.UserConfigChanged.value = 1;
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
	<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeParentalUserSetup.asp" id="ID_A_USER_SETUP">User Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalBasic.asp" id="ID_A_BASIC_SETUP">Basic Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalTimeFilter.asp" id="ID_A_TIME_FILTER">Time Filter</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_USER_SETUP">Parental Control - User Setup</h1>
    <label id="ID_LABEL_PC_USER_SETUP_DESC">This page allows configuration of users. 'White List Only' feature limits the user to visit only the sites, specified in the Allowed Domain List of his/her content rule.</label>
  </div>

<form action=/goform/UbeeParentalUserSetup method=POST name="UbeeParentalUserSetup">
<table>
<tr>
<td>
<!-- User Configuration-->
<tr>
<td>
<table border="1" bgcolor="#C0C0C0">
<tr>
<td align=left><h3 id="ID_H3_USER_CONF"><b>User Configuration </b></h3> </td>
</tr>
<tr><td>
<input type="text" name="NewUser" size="8" maxlength="8" value= >
<input type="submit" value="Add User" onClick="addUser();" id="ID_BUTTON_ADD_USER"><input type="hidden" name="AddUser" value=0>
</td></tr>
<tr>
<td align=left><label id="ID_LABEL_PC_USER_SETTINGS"><b>User Settings</b></label></td>
</tr>
<tr>
<td><select name="UserList" onChange="submit();"><option value=Default selected>1. Default</select>
<input type="CheckBox" name="cbEnableUser" onclick="enableUser();" value="0x2000"  ><i><label id="ID_BUTTON_REMOVE_USER_ENABLE">Enable</label></i>
<input type="hidden" name="RemoveUser" value=0>
<input type="submit" value="Remove User" onClick="removeUser();" id="ID_BUTTON_REMOVE_USER"></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_PASSWORD">Password</label></td>
<td><input type="password" name="UserPassword" size="8" maxlength="8" DISABLED value= ></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_RE_ENTER_PASSWORD">Re-Enter Password</label></td>
<td><input type="password" name="UserPasswordReEnter" size="8" maxlength="8" DISABLED value= ></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_TRUSTED_USERS">Trusted User</label></td><td><input type="CheckBox" name="cbTrustedUser" onclick="trustedUser();" value="0x1000"  DISABLED ><i><label id="ID_BUTTON_TRUST_USER_ENABLE">Enable</label></i></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_CONTENT_RULE">Content Rule</label> &nbsp;&nbsp;&nbsp;&nbsp;<input type="CheckBox" name="cbWhiteListOnly" value="0x80000000"  DISABLED > <label id="ID_LABEL_PC_WHITE_LIST">White List Access Only</label> </td>
<td><select name="UserRules" DISABLED><option value=0 selected>1. Default<option value=99999 >No rule set.</select></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_TIME_ACCESS_RULE">Time Access Rule</label></td>
<td><select name="TodRule" multiple size="2" DISABLED><option value=99999 selected>No rule set.</select></td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_SESSION_DURATION">Session Duration</label></td>
<td><input type="text" name="SessionDuration" size="8" maxlength="8" value=0 DISABLED> min</td>
</tr>

<tr>
<td><label id="ID_LABEL_PC_USER_INACTIVITY_TIME">Inactivity time</label></td>
<td><input type="text" name="InactivityTime" size="8" maxlength="8" value=0 DISABLED> min</td>
</tr>

<input type="hidden" name="UserConfigChanged" value=0>
<tr><td><input type="Submit" value="Apply" onClick="configureUser();" align="MIDDLE" id="ID_BUTTON_PC_APPLY"></td></tr>
</table>
</td>
</tr>
<!-- end User Configuration-->
</td>

<td>
<!-- upper right -->

<table>
<tr>
<td><label id="ID_LABEL_PC_USER_TRUSTED_COMPUTERS"><b>Trusted Computers</b></label></td>
</tr>

<tr>
<td><label id="ID_LABEL_TRUSTED_COMPUTERS_DESC1">Optionally, the user profile displayed above can be assigned </label></td></tr>
<tr><td><label id="ID_LABEL_TRUSTED_COMPUTERS_DESC2">to a computer to bypass the Parental Control login on that computer. </label></td>
</tr>

<tr>
<td><input type="text" name="NewTrustedComputerMA0" size="2" value=00 ><b>:</b>
<input type="text" name="NewTrustedComputerMA1" size="2" value=00 ><b>:</b>
<input type="text" name="NewTrustedComputerMA2" size="2" value=00 ><b>:</b>
<input type="text" name="NewTrustedComputerMA3" size="2" value=00 ><b>:</b>
<input type="text" name="NewTrustedComputerMA4" size="2" value=00 ><b>:</b>
<input type="text" name="NewTrustedComputerMA5" size="2" value=00 >
<input type="submit" value="Add" onClick="AddTrustedClient();" id="ID_BUTTON_ADD_TRUST"><input type="hidden" name="addTrustedClient" value=0></td>
</tr>
<tr><td>&nbsp;</td></tr>
<tr><td><select name="TrustedComputers" size="3"><option value=0>No Trusted Computers</select><input type="submit" value="Remove" onClick="RemoveTrustedClient();" id="ID_BUTTON_REMOVE_PC"><input type="hidden" name="removeTrustedClient" value=0></td></tr>
</table>
</td>
</tr>
<!-- end Trusted Computers -->

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












