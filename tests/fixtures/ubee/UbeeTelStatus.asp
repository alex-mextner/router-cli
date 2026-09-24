<html>

<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway - Telephony: Status</title>
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
	console.log("no Hide Multilanguage");
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
	<li><a href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM" >CableModem</a></li><li><a class="current" href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY" >Telephony</a></li><li><a href="UbeeLanSetup.asp" id="ID_A_GATEWAY">Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li>
        <font id="ID_LABEL_WEB_LANGUAGE" color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
		
<div id="navigation_bar">
  <ul>
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeTelStatus.asp" id="ID_A_TEL_STATUS">Status</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_TEL_STATUS_TITLE" >Telephony Status</h1>
   <label id="ID_LABEL_TEL_STATUS_DESC">This page displays the MTA provisioning status and line status.</label>
  </div>
<table>
<tr bgcolor=#FF8C00><td colspan=2><b><label id="ID_TABLE_TEL_MTA_PROV_STATUS">MTA Provisioning Status</label></b></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_DHCP_STATUS">Telephony DHCP</label></td><td><label id="ID_LABEL_MTADHCP_COMPLETE">Completed</label></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_SEC_STATUS">Telephony Security</label></td><td><label id="ID_LABEL_MTASEC_DISABLED">Disabled</label></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_TFTP_STATUS">Telephony TFTP</label></td><td><label id="ID_LABEL_MTATFTP_COMPLETE">Completed</label></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_PROV_STATUS">Telephony Provisioning</label></td><td><label id="ID_LABEL_MTAPROV_COMPLETE">Completed</label></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_CALLSERVE">Register with Call Server</label></td><td>L1: <label id="ID_LABEL_MTAREG_OPERATIONAL">Operational</label>/ L2: <label id="ID_LABEL_MTAREG_DISCONN1">Disconnected</label></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_MTA_REGISTRATION">Registration Complete</label></td><td><label id="ID_LABEL_MTAPROVRESULT_PASSWARN">Pass With Warnings</label></td></tr>
</table>
<table>
<tr bgcolor=#FF8C00><td colspan=2><b><label id="ID_TABLE_LINE_STATUS">Line Status</label></b></td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_PORT_1_STATUS">Port 1 Status</label></td><td>On-hook</td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_PORT_2_STATUS">Port 2 Status</label></td><td>On-hook</td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_PORT_1_PHOEN_NUMBER">Port 1 Phone Number</label></td><td>[N/A]</td></tr>
<tr bgcolor="#CCCCCC"><td><label id="ID_TABLE_PORT_2_PHOEN_NUMBER">Port 2 Phone Number</label></td><td>[N/A]</td></tr>
</table><br><br><br><br><br><br><br><br><br><br>

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
