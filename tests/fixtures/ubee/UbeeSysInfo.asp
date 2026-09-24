<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway - CableModem: System Information </title>
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
                     <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
				   </ul>
				</div>

				<div id="navigation-bottom-line"></div>
				<div id="navigation_bar">
				  <ul>
						 <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeSysInfo.asp" id="ID_A_STATUS">Status</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeSysInfo.asp" id="ID_A_SYSTEM_INFORMATION" >System Information</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeConnection.asp" id="ID_A_SYSTEM_CONNECTION" >Connection</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeConfiguration.asp" id="ID_A_SYSTEM_CONFIGURATION" >Configuration</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeCmProvisioning.asp" id="ID_A_PROVISIONING">Provisioning</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementPassword.asp" id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
				  </ul>
				</div>
				<div id="main_page">
					<div class="description">
						<h1 id="ID_H1_SYSTEM_INFORMATION_TITLE" >System Information</h1>
						<label id="ID_LABEL_SYSTEM_INFORMATION_DESC"> This page displays the system information.</label>
					</div>
					<div class="table_data">
						<table>

							<tr><th colspan=2><b><label id="ID_LABEL_TABLE_INFORMATION">Information</label></b></th></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_VENDOR">Vendor</label></td><td>Ubee Interactive Corp.</td></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_MODEL">Model</label></td><td>EVW32C-0N</td></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_HARDWARE_VERSION">Hardware Version</label></td><td>3.34.1</td></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_FIRMWARE_VERSION">Firmware Version</label></td><td>2.4.1015-SIP</td></tr>
					 		<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_BOOT_VERSION">Boot Version</label></td><td>1.0.03</td></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_CABLE_MODEM_SERIAL_NUMBER">Cable Modem Serial Number</label></td><td>EVW32C0N00000000</td></tr>
							<tr bgcolor="#cccccc"><td><label id="ID_LABEL_TABLE_CABLE_MODEM_MAC_ADDRESS">Cable Modem MAC Address</label></td><td>02:00:00:00:01:1b</td></tr>
						</table><br><br>

						<table>
						<tr bgcolor=#ce0000><th colspan=2><b><label id="ID_LABEL_TABLE_STATUS">Status</label></b></th></tr>

						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_DOCSIS_MODE">DOCSIS mode</label></td><td>DOCSIS 3.0</td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_NETWORK_ACCESS">Network Access</label></td><td>Allowed</td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_SYSTEM_UP_TIME">System Up Time</label></td><td>94 days 01h:25m:22s</td></tr>
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
