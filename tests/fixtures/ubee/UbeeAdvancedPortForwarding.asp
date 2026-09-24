<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway Advanced Port Forwarding</title>
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


function createEntry(value)
{
	
    window.document.UbeeAdvancedPortForwarding.PortForwardingCreateRemove.value = value;
    window.document.UbeeAdvancedPortForwarding.submit();
}
function removeAllEntries()
{
	
    window.document.UbeeAdvancedPortForwarding.PortForwardingCreateRemove.value = 4;
    window.document.UbeeAdvancedPortForwarding.submit();
}
function removeEntry(entry)
{
	
    window.document.UbeeAdvancedPortForwarding.PortForwardingCreateRemove.value = 3;
    window.document.UbeeAdvancedPortForwarding.PortForwardingTable.value = entry;
    window.document.UbeeAdvancedPortForwarding.submit();
}
function editEntry(entry)
{
	
    window.document.UbeeAdvancedPortForwarding.PortForwardingCreateRemove.value = 0;
    window.document.UbeeAdvancedPortForwarding.PortForwardingTable.value = entry;
    window.document.UbeeAdvancedPortForwarding.submit();
}
function applyCommitForwarding(value)
{
    if (value != 1) //Press Cancel button, don't check, Albert
    {
       if (!(/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalIp.value)))
        {
            alert("Local IP is a invalid IP address."+window.document.UbeeAdvancedPortForwarding.PortForwardingLocalIp.value);
            return false;
        }
       if (!(/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(window.document.UbeeAdvancedPortForwarding.PortForwardingExtIp.value)))
        {
            alert("External IP is a invalid IP address."+window.document.UbeeAdvancedPortForwarding.PortForwardingExtIp.value);
            return false;
        }

        //Check port range is in between 1 ~ 65535, Albert
    	if ((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10) <= 0)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) <= 0)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) <= 0)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value,10) <= 0)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10) > 65535)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) > 65535)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) > 65535)
         || (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value,10) > 65535))
        {
            cleanPort();
            alert("The port range must be in between 1 ~ 65535.");
            return false;
        }

        //Close 22 and 23 port, Albert
        if (((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10) <= 22) && (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) >=22))
        || ((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10) <= 23) && (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) >=23)))
        {
            cleanPort();
            alert("The Local start port range can't be included between 22 and 23.");
            return false;
        }
        if (((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) <= 22) && (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value,10) >=22))
        || ((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) <= 23) && (parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value,10) >=23)))
        {
            cleanPort();
            alert("The External port range can't be included between 22 and 23.");
            return false;
        }
    }

    window.document.UbeeAdvancedPortForwarding.PortForwardingApply.value = value;
    window.document.UbeeAdvancedPortForwarding.submit();
}



function vendorCheck()
{
	
    if((window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value.length>0)&&(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value.length>0)&&(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value.length>0))
    {
	
        if ((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) - parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10)) <= (65535-parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10)))
        {
            window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value = parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) + parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) - parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10);
	
        }
        else
        {
            alert("The ending port address must be less than 65535.");
      		return false;
        }
    }
    return true;
}

function cleanPort()
{
    window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value = 0;
    window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value = 0;
    window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value = 0;
    window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value = 0;
}
function vendorCheckPortRange()
{
    if((window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value.length>0)&&(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value.length>0)&&(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value.length>0))
    {
        if ((parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) - parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10)) <= (65535-parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10)))
        {
            window.document.UbeeAdvancedPortForwarding.PortForwardingExtEndPort.value = parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingExtStartPort.value,10) + parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalEndPort.value,10) - parseInt(window.document.UbeeAdvancedPortForwarding.PortForwardingLocalStartPort.value,10);
        }
        else
        {
            alert("The ending port address must be less than 65535.");
      		return false;
        }
    }
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
			   
			        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvConnectedDevicesList.asp"  id="ID_A_CONNECTED_DEVICES_LIST">Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		          </ul>
		       
			  </div>
			<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_ADVANCED_PORT_FORWARDING_TITLE">Advanced Port Forwarding</h1>
    <label id="ID_LABEL_ADVANCED_PORT_FORWARDING_DESC">This allows for incoming requests on specific port numbers to reach web servers, FTP servers, mail servers, etc. so they can be accessible from the public internet. A table of commonly used port numbers is also provided.</label>
  </div>

<form action=/goform/UbeeAdvancedPortForwarding method=POST name="UbeeAdvancedPortForwarding">

<table><tr><td><table>
<tr>
<td>
<input type="submit" onclick="createEntry(1);" value="Create IPv4" align="left" id="ID_BUTTON_CREATE_IPV4_PORT_FORWARDING" >
<input type="hidden" value="0" name="PortForwardingCreateRemove">
</td>
</tr>
<tr><td>&nbsp;</td></tr>










</table>

<div class="table_data table_data12">
<table>
<tr><th colspan=3><label id="ID_LABEL_LOCAL">Local</label></th><th colspan=3><label id="ID_LABEL_EXTERNAL">External</label></th></tr>
<tr><th><label id="ID_LABEL_LOCAL_IP_ADDRESS">IP Address</label></th><th><label id="ID_LABEL_LOCAL_START_PORT">Start Port</label></th><th><label id="ID_LABEL_LOCAL_END_PORT">End Port</label></th><th><label id="ID_LABEL_EXRTERNAL_IP_ADDRESS">IP Address</label></th><th><label id="ID_LABEL_EXRTERNAL_START_PORT">Start Port</label></th><th><label id="ID_LABEL_EXRTERNAL_END_PORT">End Port</label></th><th><label id="ID_LABEL_PROTOCOL">Protocol</label></th><th><label id="ID_LABEL_LOCAL_DESCRIPTION">Description</label></th><th><label id="ID_LABEL_ENABLE">Enabled</label></th>
<th>&nbsp;</th>
<th><input type="submit" onclick="removeAllEntries();" value="Remove All" align="left" id="ID_BUTTON_REMOVE_ALL"></th>
<td><input type="hidden" value="0" name="PortForwardingTable"></td>
<tr><td>192.168.0.200</td><td>8080</td><td>8080</td><td>0.0.0.0</td><td>18080</td><td>18080</td><td>TCP</td><td>test</td><td>Yes</td>
<td><input type="submit" onclick="editEntry(0)" value="Edit" align="left" id="ID_BUTTON_EDIT_PORT_FORWARDING"></td>
<td><input type="submit" onclick="removeEntry(0)" value="Remove" align="left" id="ID_BUTTON_REMOVE_PORT_FORWARDING" ></td>
</tr>
</table>
</div>
</td>
<td><img border="0" src="port_map.gif" /></td>
</tr></table>



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
