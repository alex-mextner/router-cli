<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css">
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway - CableModem: Configuration </title>
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

function ResetYesButton()
{
        var the_box = window.document.Configuration.ResetYes;
        
        if (the_box.checked == true) {
                window.document.Configuration.ResetNo.checked = false;
                window.document.Configuration.ResetFactoryNo.checked = true;
                window.document.Configuration.ResetFactoryYes.checked = false;
        }
}

function ResetNoButton()
{
        var the_box = window.document.Configuration.ResetNo;
       
        if (the_box.checked == true) {
                window.document.Configuration.ResetYes.checked = false;
        }
}

function ResetFactoryYesButton()
{
        var the_box = window.document.Configuration.ResetFactoryYes;
        
        if (the_box.checked == true) {
                window.document.Configuration.ResetFactoryNo.checked = false;
                window.document.Configuration.ResetNo.checked = true;
                window.document.Configuration.ResetYes.checked = false;
        }
}

function ResetFactoryNoButton()
{
        var the_box = window.document.Configuration.ResetFactoryNo;
       
        if (the_box.checked == true) {
                window.document.Configuration.ResetFactoryYes.checked = false;
        }
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
  		<!--	<a href="http://www.ubeeinteractive.com/"><img src="generic_modemrouter_header.gif" border="0"></a> -->
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
			<!-- Main Menu  -->
				<div id="navigation_header">
				   <ul>
					 <li><a class="current" href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM"  >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a href="UbeeLanSetup.asp" id="ID_A_GATEWAY">Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li>
                     <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
				   </ul>
				</div>
			<!-- Main Menu  -->

				<div id="navigation-bottom-line"></div>
			
			<!-- Navigator bar  -->
				<div id="navigation_bar">
				  <ul>
					<ul>
						 <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeSysInfo.asp" id="ID_A_STATUS">Status</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeSysInfo.asp" id="ID_A_SYSTEM_INFORMATION" >System Information</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeConnection.asp" id="ID_A_SYSTEM_CONNECTION" >Connection</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeConfiguration.asp" id="ID_A_SYSTEM_CONFIGURATION">Configuration</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeCmProvisioning.asp" id="ID_A_PROVISIONING">Provisioning</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementPassword.asp" id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
					</ul>
				  </ul>
				</div>
			<!-- Navigator bar  -->

				<div id="main_page">  <!-- main_page  -->
					<div class="description">
						<h1 id="ID_H1_CONFIGURATION_TITLE" >Configuration</h1>
						<label id="ID_LABEL_CONFIGURATION_DESC"> This page allows reboot and restore factory defaults to the system.</label>
					</div>
					
					<form action=/goform/UbeeConfiguration method=POST name="Configuration">
					
					<div class="table_data">
						<table>
            <tr><th colspan=2><b><label id="ID_LABEL_TABLE_CONF_RESET_FACTORY">Reboot/Factory Reset</label></b></th></tr>
            <tr>
              <table>
              <tr valign>
              <td><label id="ID_LABEL_TABLE_CONF_RESET">Reboot</label></td>
              <td><input type="radio" name="ResetYes" value=0x01 onClick="ResetYesButton();" ><label id="ID_LABEL_TABLE_CONF_RESET_YES">Yes</label></td>
              <td><input type="radio" name="ResetNo" value=0x00 CHECKED onClick="ResetNoButton();"><label id="ID_LABEL_TABLE_CONF_RESET_NO">No</label></td>
              </tr>
              </table>
            </tr>
            <br>
            <tr>
              <table>
              <tr valign>
              <td><label id="ID_LABEL_TABLE_CONF_FACTORY">Factory Reset</label></td>
              <td><input type="radio" name="ResetFactoryYes" value=0x01 onClick="ResetFactoryYesButton();"><label id="ID_LABEL_TABLE_CONF_FACTORY_YES">Yes</label></td>
              <td><input type="radio" name="ResetFactoryNo" value=0x00 CHECKED onClick="ResetFactoryNoButton();"><label id="ID_LABEL_TABLE_CONF_FACTORY_NO">No</label></td>
              </table>
            </tr>
            <tr>
                <table>
                    <td><input type="submit" id="ID_LABEL_TABLE_CONF_FACTORY_APPLY" value="Apply" align="MIDDLE"></td>
                </table>
            </tr>
              </table>
            </tr>
						</table>
					</div>
					</form>
				</div>

		</div> <!-- hold -->
		<div id="hold-bottom-line"></div>
	
	</div> <!-- center -->
	<div class="zp-portal-bottom-left">
		<div class="zp-portal-bottom-right">
			<div class="zp-portal-bottom-center"></div>
		</div>
	</div>
		
	<div id="footer">
   		<!-- <div id="copyright">2014 Ubee Interactive. All rights reserved.</div> -->
   		<div id="copyright">©2021 Ubee Interactive. All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->


</body></html>
