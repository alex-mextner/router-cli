<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<title>Residential Gateway Management Password </title>
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
     

	 $('#ID_BUTTON_APPLY_PASSWORD').click(function(e) { 
	 
        if($('#ID_INPUTBOX_NEW_PASSWORD').val().length <= 0 )
		{
			alert("New password can't be null string.");
			e.preventDefault();
			return;

		}
		
		if($('#ID_INPUTBOX_CONFIRM_NEW_PASSWORD').val() != $('#ID_INPUTBOX_NEW_PASSWORD').val() )
		{
			alert("Password confirmation failure.");
			e.preventDefault();
			return;
		}
          
     });

	 
    //Data Post Back when select language dropdownlist
    $( '#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE' ).change(function() { 
        
        var jsonStr = '{ "web_language_cm" :' + $("select#ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE option:selected").val() + ' }';

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
	<li><a class="current" href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM"  >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a href="UbeeLanSetup.asp" id="ID_A_GATEWAY">Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li>
                 <font  id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
			<div id="navigation_bar">
                  <ul>
			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeSysInfo.asp" id="ID_A_STATUS">Status</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeCmProvisioning.asp" id="ID_A_PROVISIONING">Provisioning</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeManagementPassword.asp" id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeManagementPassword.asp" id="ID_A_PASSWORD">Password</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		          </ul>
			  </div>
			<div id="main_page">
			  <div class="description">
    <h1 id="ID_H1_HEADER_PASSWORD_TITLE">Change Password</h1>
    <label id="ID_LABEL_PASSWORD_DESC">This page allows configuration of your password. The new password can be any ACSII code and max length is 24 digits.</label>
</div>

<form action=/goform/UbeeManagementPassword method=POST name="Security">

<table>
<tr valign=top>

<td>

<table>
<tr>
<td><label id="ID_LABEL_USERNAME">Username</label></td>
<td><input name="UserId" size="24" maxlength="24" disabled="disable" value=admin ></td>
</tr>
<tr>
  <td><label id="ID_LABEL_OLD_PASSWORD">Old Password</label></td>
  <td><input id="ID_INPUTBOX_OLD_PASSWORD" type="password" name="OldPassword" size="24" maxlength="24" value=></td>
</tr>
<tr>
<td><label id="ID_LABEL_NEW_PASSWORD">New Password</label></td>
<td><input id="ID_INPUTBOX_NEW_PASSWORD" type="password" name="Password" size="24" maxlength="24" value=></td>
</tr>
<tr>
<td><label id="ID_LABEL_NEW_PASSWORD_CONFIRM">Retype the Password</label></td>
<td><input  id="ID_INPUTBOX_CONFIRM_NEW_PASSWORD"type="password" name="PasswordReEnter" size="24" maxlength="24" value=></td>
</tr>
</table>

</td>

</tr>

<tr>
<td colspan=3 align=center><input id="ID_BUTTON_APPLY_PASSWORD" type="Submit" value="Apply" align="MIDDLE"></td>
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
