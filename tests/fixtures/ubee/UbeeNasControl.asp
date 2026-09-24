<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway NAS Control </title>
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


function RadioButtonFtpDisable()
{
	var the_box = window.document.UbeeNasControl.NasFtpDisable;
        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasFtpEnable.checked = false;
        }
}

function RadioButtonFtpEnable()
{
	var the_box = window.document.UbeeNasControl.NasFtpEnable;
        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasFtpDisable.checked = false;
        }
}


function RadioButtonSambaDisable()
{
	var the_box = window.document.UbeeNasControl.NasSambaDisable;
        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasSambaEnable.checked = false;
        }
}

function RadioButtonSambaEnable()
{
	var the_box = window.document.UbeeNasControl.NasSambaEnable;
        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasSambaDisable.checked = false;
        }
}


function RadioButtonEnableMsc()
{
        var the_box = window.document.UbeeNasControl.NasBasicEnableMsc;
        if (the_box.checked == true) {
                window.document.UbeeNasControl.NasBasicDisableMsc.checked = false;
        }
}

function RadioButtonDisableMsc()
{
        var the_box = window.document.UbeeNasControl.NasBasicDisableMsc;

        if (the_box.checked == true) {
                window.document.UbeeNasControl.NasBasicEnableMsc.checked = false;
        }
}

function RadioButtonPermissionAnonymous()
{
	var the_box = window.document.UbeeNasControl.NasPermissionAnonymous;

        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasPermissionAdmin.checked = false;
        }
}

function RadioButtonPermissionAdmin()
{
	var the_box = window.document.UbeeNasControl.NasPermissionAdmin;

        if (the_box.checked == true) {
			window.document.UbeeNasControl.NasPermissionAnonymous.checked = false;
        }
} 



function ApplyButton()
{
    window.document.UbeeNasControl.NasBasicApplyAction.value = 1;
	    window.document.UbeeNasControl.NasEjectAction.value = 0;
}

function RemoveDevices()
{
    window.document.UbeeNasControl.NasEjectAction.value = 1;
    window.document.UbeeNasControl.NasBasicApplyAction.value = 0;
}




function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}
// show me -->

</script>
</head>
<body >
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
	<li><a href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM" >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a class="current" href="UbeeLanSetup.asp" id="ID_A_GATEWAY" >Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li><font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
   			  </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
		
<div id="navigation_bar">
  <ul>
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeNasControl.asp" id="ID_A_NAS_CONTROL">NAS Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasStorageAdvSamba.asp" id="ID_A_NAS_STORAGE_ADVSAMBA">Samba</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasStorageAdvFtp.asp" id="ID_A_NAS_STORAGE_ADVFTP">FTP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasMediaServer.asp" id="ID_A_MEDIA_SERVER">MediaServer</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_NAS_CONTROL">NAS - Control </h1>
     <label id="ID_LABEL_NAS_CONTROL_DESC">This page allows basic control of the USB  
	devices shared over the network.</label>
  </div>

<form action=/goform/UbeeNasControl method=POST name="UbeeNasControl">
<table width="100%">
  <tr  >
    <td width="24%" ><label id="ID_LABEL_NAS_USB_SLOT">USB Slot</label></td>
    <td width="15%">Disconnected.</td>
    <td width="23%"><input type="Submit" value="Eject USB Device" align="MIDDLE" id="ID_BUTTON_NAS_APPROVED_SAFELY_REMOVE_DEVICE" disabled=true onClick="RemoveDevices()"></td>
    <td width="9%">&nbsp;</td>
    <td width="29%" align="left">&nbsp;</td>
  </tr>
  <tr>
	  <td><strong>
		  <label id="ID_LABEL_NAS_STORAGE_ADVANCED_DEVICE_NAME">Network/Device Name:</label>
	  </strong></td>
	  <td colspan="2"><b>
	  <input name=NasStorageAdvancedNetworkName size=25 maxlength=25 value="EVW32C-0N-TEST" >
	  </b></td>
  </tr>
  <tr  >
    <td  ><label id="ID_LABEL_NAS_ENABLE_SAMBA">Enable Samba File Sharing</label></td>
    <td><input name="NasSambaEnable" type="radio" value="1"  onClick="RadioButtonSambaEnable();" CHECKED >
     <label id="ID_RADIO_SAMBA_SHARE_ENABLE" > Yes </label></td>
    <td><input name="NasSambaDisable" type="radio" value"0"  onClick="RadioButtonSambaDisable();"   >
     <label id="ID_RADIO_SAMBA_SHARE_DISABLE" > No </label></td>
    <td></td>
    <td  align=left>&nbsp;</td>
  </tr>
  <tr >
    <td  ><label id="ID_LABEL_NAS_ENABLE_FTP">Enable FTP File Sharing</label></td>
    <td><input type="radio" name="NasFtpEnable" value="1"    onClick="RadioButtonFtpEnable();" >
      <label id="ID_RADIO_FTP_SHARE_ENABLE" > Yes</label></td>
    <td><input type="radio" name="NasFtpDisable" value="0"  CHECKED onClick="RadioButtonFtpDisable();" >
      <label id="ID_RADIO_FTP_SHARE_DISABLE">No</label></td>
    <td>&nbsp;</td>
    <td  align=left>&nbsp;</td>
  </tr>
  <tr>
    <td  ><label id="ID_LABEL_NAS_ENABLE_DLNA">Enable the Media Server (DLNA)</label></td>
    <td><input type="radio" name="NasBasicEnableMsc" value="1" CHECKED onClick="RadioButtonEnableMsc();" >
     <label id="ID_RADIO_NAS_DLNA_ENABLE" > Yes </label></td>
    <td><input type="radio" name="NasBasicDisableMsc" value="0"    onClick="RadioButtonDisableMsc();" >
     <label id="ID_RADIO_NAS_DLNA_DISABLE" >No</label></td>
    <td>&nbsp;</td>
    <td  align=left>&nbsp;</td>
  </tr>
  
  <tr>
    <td  >&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td  align=left>&nbsp;</td>
  </tr>
  <tr >
    <td  ><label id="ID_LABEL_ALLOW_ANONYMOUS" >Allow Anonymous Access</label></td>
    <td><input type="radio" name="NasPermissionAnonymous" value="1"   onClick="RadioButtonPermissionAnonymous();" >
       <label id="ID_RADIO_DEFAULT_PERMISSION_ANONYMOUS" >Yes</label></td>
    <td><input type="radio" name="NasPermissionAdmin" value="0" CHECKED onClick="RadioButtonPermissionAdmin();" >
      <label id="ID_RADIO_DEFAULT_PERMISSION_Admin" > No </label></td>
    <td>&nbsp;</td>
    <td  align=left>&nbsp;</td>
  </tr>
  <tr >
    <td  ><label id="ID_LABEL_NAS_ADMIN_USERNAME">Username for file sharing </label></td>
    <td colspan="4"><label for="NasUsername"></label>
      <input name="NasUsername" type="text" id="NasUsername" maxlength="32" value="admin"></td>
  </tr>
  <tr  >
    <td  ><label id="ID_LABEL_NAS_ADMIN_PASSWORD">Password for file sharing</label></td>
    <td colspan="4"><input name="NasPassword" type="password" id="NasPassword" maxlength="32" value="fixture-nas-pass" ></td>
  </tr>
  
  <tr>
  <p></p>
    <td colspan=3 align=left><input type="Submit" value="Apply" id="ID_BUTTON_NAS_APPLY" align="MIDDLE" onClick="ApplyButton();">
                         <input type="hidden" name="NasBasicApplyAction" id="ID_BUTTON_NAS_APPLY_ACTION"  value=>
                         <input type="hidden" name="NasEjectAction" value=></td>
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
</body></html>
