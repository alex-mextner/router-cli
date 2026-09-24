<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css">
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway - CableModem: Provisioning </title>
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
							 <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeSysInfo.asp" id="ID_A_STATUS">Status</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeCmProvisioning.asp" id="ID_A_PROVISIONING">Provisioning</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementPassword.asp" id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
						</ul>

				</div>
			<!-- Navigator bar  -->

				<div id="main_page">  <!-- main_page  -->
					<div class="description">

						<h1 id="ID_H1_PROVISIONING_TITLE" >Provisioning</h1>
					<label id="ID_LABEL_CONNECTION_DESC">This page displays the cable modem provisioning information.</label>
					</div>
					<div class="table_data">
						<table>
						<tr bgcolor=#ce0000><th colspan=2><b><label id="ID_LABEL_TABLE_PROV_CABLEMODEM_STATUS">Modem Status</label></b></th></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_HW_INIT">HW Initial</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_DOWNSTREAM">Find Downstream</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE1">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_RANGING">Ranging</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE2">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_DHCP">DHCP</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE3">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_TOD">Time of Day</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE5">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_CM_CFG">Download CM Config File</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE4">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_REGISTRATION">Registration</label></td><td><label id="ID_LABEL_SYSTEM_GET_COMPLETE6">Completed</label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_EAE_STATUS">EAE status</label></td><td><label id="ID_LABEL_SYSTEM_GET_ENABLE">Enabled </label></td></tr>
						<tr bgcolor="#9999cc"><td><label id="ID_LABEL_TABLE_PROV_BPI_STATUS">BPI status</label></td><td><label id="ID_LABEL_SYSTEM_GET_ENABLE1">Enabled </label>/ <label id="ID_LABEL_SYSTEM_GET_BPI">BPI+</label></td></tr>
						</table>
					</div>
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
