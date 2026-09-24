<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway NAS Storage Advanced</title>
<script src="js/jquery-1.10.2.js"></script>
<script src="js/ubee_js_apis.js"></script>
<script LANGUAGE="javascript">

var language_jsonData = ' { "web_language": 0 } ' ;
var language_jsonObj = jQuery.parseJSON(language_jsonData); 

$(function() {

var usb_status=false;

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

function ApplyButton()
{
    window.document.UbeeNasStorageAdvanced.NasStorageAdvancedApplyAction.value = 1;
}

function FolderPopup(action, share_id, share_device, share_name, share_path, share_permissions) {
	if (action == 'edit')
	{
		var win = window.open( "../UbeeNasEditFolderPopup.asp?action="+action+
		"&id="+share_id+
		"&device="+share_device+
		"&name="+share_name+
		"&path="+share_path+
		"&permissions="+share_permissions
		, "myWindow", 
		"status = 1, height=500, width=500, resizable=yes, scrollbars=yes, left=20, top=20" )
		var timer = setInterval(function() {   
		    if(win.closed) {  
	        clearInterval(timer);  
	        window.location.reload();  
		    }  
		}, 1000); 
	}
	else if (action == 'remove')
	{
		var win = window.open( "../UbeeNasRemoveFolderPopup.asp?action="+action+
		"&id="+share_id+
		"&device="+share_device+
		"&name="+share_name+
		"&path="+share_path
		, "myWindow", 
		"status = 1, height=500, width=500, resizable=yes, scrollbars=yes, left=20, top=20" )
		var timer = setInterval(function() {   
		    if(win.closed) {  
	        clearInterval(timer);  
	        window.location.reload();  
		    }  
		}, 1000); 
	}
	else if (action == 'create')
	{
		var win = window.open( "../UbeeNasCreateFolderPopup.asp?action="+action, "myWindow", 
		"status = 1, height=500, width=500, resizable=yes, scrollbars=yes, left=20, top=20" );
		var timer = setInterval(function() {   
			if(win.closed) {  
		    //The popup closed, reload and clear the timer
	        clearInterval(timer);  
	        window.location.reload();  
		    }  
		}, 1000); 
	}
	else if (action == 'admin')
	{
		var win = window.open( "../UbeeNasAdminInfo.asp?action="+action, "myWindow", 
		"status = 1, height=500, width=500, resizable=yes, scrollbars=yes, left=20, top=20" );
		var timer = setInterval(function() {   
			if(win.closed) {  
		    //The popup closed, reload and clear the timer
	        clearInterval(timer);  
	        window.location.reload();  
		    }  
		}, 1000); 
	}
}

function ReloadMe()
{
	alert("reloading");
	window.location.reload();
}
function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}
// show me -->

function RadioButtonFtpDisable()
{
	var the_box = window.document.UbeeNasStorageAdvFtp.NasFtpDisable;
	if (the_box.checked == true) {
			window.document.UbeeNasStorageAdvFtp.NasFtpEnable.checked = false;
	}
}

function RadioButtonFtpEnable()
{
	var the_box = window.document.UbeeNasStorageAdvFtp.NasFtpEnable;
	if (the_box.checked == true) {
			window.document.UbeeNasStorageAdvFtp.NasFtpDisable.checked = false;
	}
}


function ApplyButton()
{
    window.document.UbeeNasStorageAdvFtp.NasBasicApplyAction.value = 1;
}

function RadioButtonDisableShareAllFolders()
{
	var the_box = window.document.UbeeNasStorageAdvFtp.NasFtpDisableShareAllFolders;
	if (the_box.checked == true) {
		window.document.UbeeNasStorageAdvFtp.NasFtpEnableShareAllFolders.checked = false;
		if (usb_status == true) {
			window.document.UbeeNasStorageAdvFtp.CreateNetWorkFolderButton.disabled = false;
		}else{
			window.document.UbeeNasStorageAdvFtp.CreateNetWorkFolderButton.disabled = true;
		}
	}
}

function RadioButtonEnableShareAllFolders()
{
	var the_box = window.document.UbeeNasStorageAdvFtp.NasFtpEnableShareAllFolders;
	if (the_box.checked == true) {
		window.document.UbeeNasStorageAdvFtp.NasFtpDisableShareAllFolders.checked = false;
		window.document.UbeeNasStorageAdvFtp.CreateNetWorkFolderButton.disabled = true;
	}
}

function setControls()
{
	var the_box = window.document.UbeeNasStorageAdvFtp.NasFtpEnableShareAllFolders;
	if (the_box.checked == true || usb_status == false){ 
		window.document.UbeeNasStorageAdvFtp.CreateNetWorkFolderButton.disabled = true;
	} else {
		window.document.UbeeNasStorageAdvFtp.CreateNetWorkFolderButton.disabled = false;
	}
}

</script>
</head>

<body onLoad="setControls();">
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
	<li><a href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM" >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a class="current" href="UbeeLanSetup.asp" id="ID_A_GATEWAY" >Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li> <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
   			  </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
		
<div id="navigation_bar">
  <ul>
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasControl.asp" id="ID_A_NAS_CONTROL">NAS Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasStorageAdvSamba.asp" id="ID_A_NAS_STORAGE_ADVSAMBA">Samba</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeNasStorageAdvFtp.asp" id="ID_A_NAS_STORAGE_ADVFTP">FTP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasMediaServer.asp" id="ID_A_MEDIA_SERVER">MediaServer</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_NAS_STORAGE_ADVANCED">NAS - FTP</h1>
       <label id="ID_LABEL_NAS_STORAGE_ADVANCED_DESC">This page allows configuration of the USB folders shared over the FTP.</label></div>
  	

<form action=/goform/UbeeNasStorageAdvFtp method=POST name="UbeeNasStorageAdvFtp">
<table width="100%" border="0">
   <tr>
  	<td><table width="100%" border="0" cellspacing="0" cellpadding="0">
  	  <tr>
  	    <td width="22%"><label id="ID_LABEL_NAS_ENABLE_FTP">Enable FTP File Sharing:</label></td>
  	    <td width="11%"><input name="NasFtpEnable" type="radio" value="1"  onClick="RadioButtonFtpEnable();"   >
  	     <label id="ID_RADIO_Ftp_SHARE_ENABLE"> Yes</label></td>
  	    <td width="67%"><input type="radio" name="NasFtpDisable" value="0"  onClick="RadioButtonFtpDisable();" CHECKED >
  	     <label id="ID_RADIO_Ftp_SHARE_DISABLE" >No</label></td>
  	    </tr>
  	  <tr>
  	    <td><strong>
  	      <label id="ID_LABEL_NAS_FTP_PORT">FTP Port:</label></strong></td>
  	    <td colspan="2"><b>
  	      <input name=NasStorageAdvancedNetworkName disabled="disabled" value="21" size=25 maxlength=25 >
	      </b></td>
  	    </tr>
  	  <tr>
		<td width="22%"><label id="ID_LABEL_NAS_SHARE_ALL_FOLDERS">Share All Folders: </label></td>
		<td width="11%"><input name="NasFtpEnableShareAllFolders" type="radio" value="1" onClick="RadioButtonEnableShareAllFolders();"   >
		<label id="ID_RADIO_ENABLE_SHARE_ALL_FOLDERS" > Yes</label></td>
		<td width="67%"><input type="radio" name="NasFtpDisableShareAllFolders" value="0"  onClick="RadioButtonDisableShareAllFolders();" CHECKED >
		<label id="ID_RADIO_DISABLE_SHARE_ALL_FOLDERS" > No</label></td>
  	    </tr>

  	  <tr>
  	    <td>&nbsp;</td>
  	    <td>&nbsp;</td>
  	    <td>&nbsp;</td>
	    </tr>
  	  <tr>
  	    <td colspan="3">(<label id="ID_LABEL_SHARE_PATH_DESC">Root folder will be share by default, Share folder can be accessed via</label> ftp://
  	      EVW32C-0N-TEST
  	      )</td>
  	    </tr>
		<tr>
			<td colspan="3">(<label id="ID_LABEL_FTP_ANONYMOUS_DESC">FTP anonymous user has limitation of access privilege, they can download/upload files instead of delete files</label> )</td>
		</tr>
	  </table></td>
  
  </tr>
  <tr>
    <td align=left>&nbsp;</td>
  </tr>

  <tr>
    <td colspan="3" align=left><input name="CreateNetWorkFolderButton" type="button" value="Create Network Folder" align="MIDDLE" id="ID_BUTTON_NAS_STORAGE_ADVANCED_CREATE_FOLDER" onClick="FolderPopup('create', 0,0,0,0,0)" disabled="disabled">    </tr>

  <tr>
    <td colspan="3" align=left>
    <div class="table_data">
    <table width="100%" cellpadding="3">
	  <tr valign>
	    <th colspan="9"><label id="ID_LABEL_SHARE_TABLE_TITLE">Available Network Folders</label></th>
	  </tr>
    <tr bgcolor=#FF8C00><td><label id="ID_LABEL_NAS_STORAGE_ADV_ACTIONS">Actions</label></td><td><label id="ID_LABEL_NAS_STORAGE_ADV_SHARE_NAME">Share Name</label></td><td><label id="ID_LABEL_NAS_STORAGE_ADV_DEVICE">Device</label></td><td><label id="ID_LABEL_NAS_STORAGE_ADV_FOLDER">Folder</label></td><td><label id="ID_LABEL_NAS_STORAGE_ADV_WRITE_ACCESS">Write Access</label></td></tr>

    </table>
    </div>
    </td>
  </tr>
  <tr>
    <td colspan=3 align=left>&nbsp;</td>
  </tr>
<hr>
  <tr>
    
    <td valign=center> <input type="Submit" value="Apply" align="MIDDLE" id="ID_BUTTON_NAS_STORAGE_ADVANCED_APPLY" onClick="ApplyButton();">
 <input type="hidden" name="NasBasicApplyAction" value=>
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
</body></html>
