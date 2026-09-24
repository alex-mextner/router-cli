<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Parental Control - Basic Setup</title>
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
	window.document.UbeeParentalBasic.KeywordAction.value = 1;
}

function RemoveKeyword()
{
	window.document.UbeeParentalBasic.KeywordAction.value = 2;
}
function AddDomain()
{
	window.document.UbeeParentalBasic.DomainAction.value = 1;
}

function RemoveDomain()
{
	window.document.UbeeParentalBasic.DomainAction.value = 2;
}

function ContentFilterAlways()
{
        var the_box = window.document.UbeeParentalBasic.FilterPolicyAlways;
        
        if (the_box.checked == true) {
                window.document.UbeeParentalBasic.FilterPolicyTimeInterval.checked = false;
        }
}

function ContentFilterTimerInterval()
{
        var the_box = window.document.UbeeParentalBasic.FilterPolicyTimeInterval;
        
        if (the_box.checked == true) {
                window.document.UbeeParentalBasic.FilterPolicyAlways.checked = false;
        }
}

function AddAllowedDomain()
{
	window.document.UbeeParentalBasic.AllowedDomainAction.value = 1;
}

function RemoveAllowedDomain()
{
	window.document.UbeeParentalBasic.AllowedDomainAction.value = 2;
}

function addContentRule()
{
	window.document.UbeeParentalBasic.AddContentRule.value = 1;
}

function removeContentRule()
{
	window.document.UbeeParentalBasic.RemoveContentRule.value = 1;
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
	<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_USER_SETUP">User Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeParentalBasic.asp" id="ID_A_BASIC_SETUP">Basic Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeParentalTimeFilter.asp" id="ID_A_TIME_FILTER">Time Filter</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_BASIC_SETUP">Parental Control - Basic Setup</h1>
    <label id="ID_LABEL_PC_BASIC_DESC">This page allows basic selection of rules which block certain Internet content and certain web sites.</label>
  </div>

<form action=/goform/UbeeParentalBasic method=POST name="UbeeParentalBasic">

<tr><label id="ID_LABEL_PC_ACTIVATION"><b>Parental Control Activation</b></label></tr>
<br>
<tr><label id="ID_LABEL_PC_ACTIVATION_DESC"> This box must be checked to turn on Parental Control</label></tr>
<br>
<tr>
<input type="checkbox" name="ParentalControlEnabled" value=0x01  > <label id="ID_LABEL_ENABLE_CHKBOX">Enable Parental Control</label>
</tr>
<tr>
<input type="Submit" value="Apply" id="ID_BUTTON_PC_APPLY" align="MIDDLE">
</tr>

<TR><TD><TABLE bgColor=#c0c0c0 border=1>
<tr>
<td>
<table>

<tr>
<td align=left><h3><label id="ID_LABEL_PC_CONTENT_POLICY_CONF"><b>Content Policy Configuration </b></label></h3> </td>
</tr>
<tr><td>
<input type="text" name="NewContentRule" size="17" maxlength="17" value= >
<input type="submit" value="Add New Policy" onClick="addContentRule();" id="ID_BUTTON_PC_NEW_POLICY"><input type="hidden" name="AddContentRule" value=0>
</td></tr>
<tr>
<td align=left><label id="ID_LABEL_PC_CONTENT_POLICY_LIST"><b>Content Policy List</b></label></td>
</tr>
<tr>
<td><select name="ContentRules" onChange="submit();"><option value=0 selected>1. Default</select>
<input type="hidden" name="RemoveContentRule" value=0>
<input type="submit" value="Remove Policy" onClick="removeContentRule();" id="ID_BUTTON_PC_REMOVE_POLICY"></td>
</tr>

</table>
</td>
</tr>

<!-- lower left -->

<tr><td><table>
	<td>
		<table>
			<td align=left><label id="ID_LABEL_CONTENT_POLICY_KEYWORD_LIST">Keyword List</label></td>
			<tr>
				<td><select name="KeywordList" size=5><option value="1">anonymizer</select>
				</td>
			</tr>
			<tr>
				<td><input type="text" name="NewKeyword" size="10" maxlength="31" value=>
					<input type="Submit" value="Add Keyword" align="MIDDLE" onClick="AddKeyword();" id="ID_BUTTON_PC_ADD_KEYWORD">
				</td>
			</tr>
			<tr>
				<td><input type="Submit" value="Remove Keyword" align="MIDDLE"  onClick="RemoveKeyword();" id="ID_BUTTON_PC_REMOVE_KEYWORD">
					<input type="hidden" name="KeywordAction" value=0>
				</td>
			</tr>
		</table>
	</td>

	<td>
		<table>
			<td align=left><label id="ID_LABEL_CONTENT_POLICY_BLOCKED_DOMAIN_LIST">Blocked Domain List</label></td>
				<tr>
					<td><select name="DomainList" size=5><option value="1">anonymizer.com</select>
					</td>
				</tr>
				<tr>
					<td><input type="text" name="NewDomain" size="10" maxlength="63" >
						<input type="Submit" value="Add Domain" align="MIDDLE" onClick="AddDomain();" id="ID_BUTTON_PC_ADD_DOMAIN">
					</td>
				</tr>
				<tr>
					<td><input type="Submit" value="Remove Domain" align="MIDDLE"  onClick="RemoveDomain();" id="ID_BUTTON_PC_REMOVE_DOMAIN">
						<input type="hidden" name="DomainAction" value=0>
					</td>
				</tr>
		</table>
	</td>

	<td>
		<table>
			<td align=left><label id="ID_LABEL_CONTENT_POLICY_ADL">Allowed Domain List</label></td>
				<tr>
					<td><select name="AllowedDomainList" size=5><option value="">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</select>
					</td>
				</tr>
				<tr>
					<td><input type="text" name="NewAllowedDomain" size="10" maxlength="63" >
						<input type="Submit" value="Add Allowed Domain" align="MIDDLE" onClick="AddAllowedDomain();" id="ID_BUTTON_PC_ADD_ALLOW_DOMAIN">
					</td>
				</tr>
				<tr>
					<td><input type="Submit" value="Remove Allowed Domain" align="MIDDLE"  onClick="RemoveAllowedDomain();" id="ID_BUTTON_PC_REMOVE_ALLOW_DOMAIN">
						<input type="hidden" name="AllowedDomainAction" value=0>
					</td>
				</tr>
		</table>
	</td>

</tr></td></table>
</table>
<tr><td><table>
<tr>&nbsp;&nbsp;</tr>
<tr><td align=left><label id="ID_LABEL_OVERRIDE_PASSWORD"><b>Override Password</b></label></td></tr>
<tr><td align=left><label id="ID_LABEL_OVERRIDE_PASSWORD_DESC">If you encounter a blocked website, you can override the block by entering the following password</label></td></tr>
<tr><td>
	<table border="1" bgcolor="#C0C0C0">
		<tr>
			<td><label id="ID_LABEL_OVERRIDE_PASSWORD_PWD">Password</label></td><td><input type="password" name="ParentalPassword" size="8" maxlength="8" value= changeme >
			</td>
		</tr>
		<tr>
			<td><label id="ID_LABEL_OVERRIDE_PASSWORD_RE_PWD">Re-Enter Password</label>
			</td>
			<td><input type="password" name="ParentalPasswordReEnter" size="8" maxlength="8" value= changeme >
			</td>
		</tr>
		<tr>
			<td><label id="ID_LABEL_OVERRIDE_PASSWORD_AD">Access Duration</label>
			</td>
			<td><input type="text" name="AccessDuration" size="8" maxlength="8" value= 30 >
			</td>
		</tr>
		<tr>
			<td><input type="Submit" value="Apply" align="MIDDLE" id="ID_BUTTON_PASSWORD_APPLY">
			</td>
		</tr>
	</table>
</td></tr>
</tr></td></table>

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
