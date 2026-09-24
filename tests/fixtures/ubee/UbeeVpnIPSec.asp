<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway  VPN -IPSec </title>
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





function CreateTunnel()
{
   window.document.UbeeVpnIPSec.TunnelAction.value = 1;
}

function DeleteTunnel()
{
   window.document.UbeeVpnIPSec.TunnelAction.value = 2;
}

function EditTunnel()
{
   window.document.UbeeVpnIPSec.TunnelAction.value = 3;
}

function HideAdvanced()
{
   window.document.UbeeVpnIPSec.TunnelAction.value = 4;
}

function ShowAdvanced()
{
   window.document.UbeeVpnIPSec.TunnelAction.value = 5;
}

function setControls()
{
	if(window.document.UbeeVpnIPSec.KeyManagement)
	{
        // if key generation is MANUAL, IKE negotiation mode and PFS should be grayed out
        if(window.document.UbeeVpnIPSec.KeyManagement.value == 1)
        {
           window.document.UbeeVpnIPSec.NegotiationMode.style.backgroundColor = '#DEDEDE';
           window.document.UbeeVpnIPSec.NegotiationMode.disabled = true;
        
           window.document.UbeeVpnIPSec.PerfectForwardSecrecy.style.backgroundColor = '#DEDEDE';
           window.document.UbeeVpnIPSec.PerfectForwardSecrecy.disabled = true;
           // since PFS is disabled, Phase 2 DH Group should be disabled, too
           window.document.UbeeVpnIPSec.Phase2DhGroup.style.backgroundColor = '#DEDEDE';
           window.document.UbeeVpnIPSec.Phase2DhGroup.disabled = true;
        }
        else
        {
           window.document.UbeeVpnIPSec.NegotiationMode.style.backgroundColor = '#FFFFFF';
           window.document.UbeeVpnIPSec.NegotiationMode.disabled = false;
           
           window.document.UbeeVpnIPSec.PerfectForwardSecrecy.style.backgroundColor = '#FFFFFF';
           window.document.UbeeVpnIPSec.PerfectForwardSecrecy.disabled = false;
        
           // If PFS is disabled, Phase 2 DH Group should be grayed out
           if(window.document.UbeeVpnIPSec.PerfectForwardSecrecy.value == 0)
           {
              window.document.UbeeVpnIPSec.Phase2DhGroup.style.backgroundColor = '#DEDEDE';
              window.document.UbeeVpnIPSec.Phase2DhGroup.disabled = true;
           }
           else
           {
              window.document.UbeeVpnIPSec.Phase2DhGroup.style.backgroundColor = '#FFFFFF';
              window.document.UbeeVpnIPSec.Phase2DhGroup.disabled = false;
           }
        }
    }

    if(window.document.UbeeVpnIPSec.LocalIdentityType.value == 0)
    {
       window.document.UbeeVpnIPSec.LocalIdentity.style.backgroundColor = '#DEDEDE';
       window.document.UbeeVpnIPSec.LocalIdentity.disabled = true;
    }
    else
    {
       window.document.UbeeVpnIPSec.LocalIdentity.style.backgroundColor = '#FFFFFF';
       window.document.UbeeVpnIPSec.LocalIdentity.disabled = false;
    }
    
    if(window.document.UbeeVpnIPSec.RemoteIdentityType.value == 0)
    {
       window.document.UbeeVpnIPSec.RemoteIdentity.style.backgroundColor = '#DEDEDE';
       window.document.UbeeVpnIPSec.RemoteIdentity.disabled = true;
    }
    else
    {
       window.document.UbeeVpnIPSec.RemoteIdentity.style.backgroundColor = '#FFFFFF';
       window.document.UbeeVpnIPSec.RemoteIdentity.disabled = false;
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
	<li><a href="UbeeSysInfo.asp" id="ID_A_CABLE_MODEM" >CableModem</a></li><li><a href="UbeeTelStatus.asp" id="ID_A_TELEPHOMY">Telephony</a></li><li><a class="current" href="UbeeLanSetup.asp" id="ID_A_GATEWAY" >Gateway</a></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="logout.asp" id="ID_A_LOGOUT">Logout</a></div></div></div></div></li> <font id="ID_LABEL_WEB_LANGUAGE"  color="#FFFFFF">&nbsp;&nbsp; |&nbsp;Language : </font><select id="ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE">
     </select>
   </ul>
</div>

			<div id="navigation-bottom-line"></div>
		
<div id="navigation_bar">
  <ul>
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN_BASIC_L3" >Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeVpnIPSec.asp"  id="ID_A_VPN_IPSEC_L3" >IPSec</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div> 
    
  </ul>
</div>

		<div id="main_page">
			<div class="description">
	   		<h1 id="ID_H1_VPN_IPSEC_TITLE" >IPSec</h1>
			<label id="ID_LABEL_VPN_IPSEC_DESC">This page allows configuration of IPSec tunnels.</label></div>
		 
	
	      <FORM name="UbeeVpnIPSec" action=/goform/UbeeVpnIPSec method=post>
    	    <TABLE>
        	  <TBODY> 
            	<td><p align="right"><label id="ID_LABEL_VPN_IPSEC_TUNNEL_ID">Tunnel</label></td>
		  	    <TD><input type="hidden" name="TunnelAction" value=0> 
        	      <SELECT onchange=submit(); name="TunnelNameDropDown"> 
		    	  <OPTION value=0 selected>Tunnel list is EMPTY.
	              </SELECT>
    	        </TD>
			    <TD> <input type="submit" value="Delete Tunnel" style="float: left" onClick="DeleteTunnel();" id="ID_BUTTON_DELETE_TUNNEL"></TD>
          </TR>
	      <tr>
		    <td>
            <p align="right"><label id="ID_LABEL_VPN_IPSEC_NAME">Name</label></td>
            <td> 
          <input name="TunnelName" size=32 maxlength=32 value="(null)"></td>
    	    <td>
            <input type="submit" value="Add New Tunnel" style="float: left" onClick="CreateTunnel();" id="ID_BUTTON_ADD_TUNNEL"></td></tr>
		<tr>
            <td align="right">&nbsp;</td>
            <td><select size="1" name="TunnelEnable">
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td><td>
            <input type="submit" value="Apply" style="float: left" onClick="EditTunnel();" id="ID_BUTTON_TUNNEL_APPLY"></td>
		</tr>

		    <tr>
            <td><b><label id="ID_LABEL_VPN_IPSEC_LOCOL_ENDPOINT_SETTINGS">Local endpoint settings</label></b></td>
            <td colspan="2">&nbsp; 
              </td>
            </tr>
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_LOCOL_ENDPOINT_ADDRESS_GROUP_TYPE">Address group type</label></td>
            <td colspan="2"> 
                <select size="1" name="LocalAddressGroupType" onChange="submit();">
                <option value=0 selected>IP subnet<option value=1 >Single IP address<option value=2 >IP address range
                </select></td>
		</tr>
        <tr><td width="225" align="right" height="23">Subnet</td><td width="442" height="23" colspan="2"><b>&nbsp;192&nbsp;.&nbsp;168&nbsp;.&nbsp;0&nbsp;.&nbsp;</b><input name="LocalSubnetAddress3" size=3 maxlength=3 value=0></td></tr><tr><td width="225" align="right" height="23">Mask</td><td width="442" height="23" colspan="2"><b>&nbsp;255&nbsp;.&nbsp;255&nbsp;.&nbsp;255&nbsp;.&nbsp;</b><input name="LocalSubnetMask3" size=3 maxlength=3 value=0></td></tr>
        <!-- need comments so that controls are automatically generated
             
             
             
             
             
             
             
             
             
             
             
             
             
        -->             
            <TR>
    		    <td>
                <p align="right"><label id="ID_LABEL_VPN_IPSEC_LOCOL_ENDPOINT_IDENTITY_TYPE">Identity type</label></td>
                <td colspan="2"> 
                  <select size="1" name="LocalIdentityType" onChange="submit();">
                  <option value=0 > Automatically use WAN IP address<option value=1 selected> IP address<option value=2 > Fully qualified domain name (FQDN)<option value=3 > Email address (USER FQDN)
                  </select></td>
            </tr>
            <tr>
		    <td>
            <p align="right"><label id="ID_LABEL_VPN_IPSEC_LOCOL_ENDPOINT_IDENTITY">Identity</label></td>
            <td colspan="2"> 
              <input name="LocalIdentity" type="text" size=32 maxlength=32 value=(null)></td>
		    </tr>
        <TR>
		    <td><b><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_SETTINGS">Remote endpoint settings</label></b></td>
            <td colspan="2">&nbsp; 
              </td>
		 </tr>
         <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_ADDRESS_GROUP_TYPE">Address group type</label></td>
            <td colspan="2"> 
                <select size="1" name="RemoteAddressGroupType" onChange="submit();">
                <option value=0 selected>IP subnet<option value=1 >Single IP address<option value=2 >IP address range
                </select></td>
         </tr>
            <tr><td width="225" align="right" height="23">Subnet</td><td width="442" height="23" colspan="2"><input name="RemoteSubnetAddress0" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetAddress1" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetAddress2" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetAddress3" size=3 maxlength=3 value=0></td></tr><tr><td width="225" align="right" height="23">Mask</td><td width="442" height="23" colspan="2"><input name="RemoteSubnetMask0" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetMask1" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetMask2" size=3 maxlength=3 value=0><b>.</b><input name="RemoteSubnetMask3" size=3 maxlength=3 value=0></td></tr>
            <!-- need comments so that controls are automatically generated
                 
                 
                 
                 
                 
                 
                 
                 
                 
                 
                 
                 
                 
            -->             
            <TR>
    		    <td>
                <p align="right"><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_IDENTITY_TYPE">Identity type</label></td>
                <td colspan="2"> 
                  <select size="1" name="RemoteIdentityType" onChange="submit();">
                  <option value=0 >Automatically use remote endpoint IP address<option value=1 selected>IP address<option value=2 >Fully qualified domain name (FQDN)<option value=3 >Email address (USER FQDN)
                  </select></td>
            </tr>
            <tr>
		    <td>
            <p align="right"><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_IDENTITY">Identity</label></td>
            <td colspan="2"> 
              <input name="RemoteIdentity" type="text" size=32 maxlength=32 value=(null)></td>
		    </tr>
            <tr>
		    <td>
            <p align="right"><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_NETWORK_ADDRESS_TYPE">Network address type</label></td>
            <td colspan="2"> 
              <select size="1" name="NetworkAddressType">
              <option value=0 selected>IP address<option value=1 >Fully qualified domain name (FQDN)
              </select></td>
		    </tr>
            <tr>
		    <td>
            <p align="right"><label id="ID_LABEL_VPN_IPSEC_REMOTE_ENDPOINT_REMOTE_ADDRESS">Remote Address</label></td>
            <td colspan="2"> 
              <input name="RemoteGatewayAddress" type="text" size=32 maxlength=32 value=0.0.0.0></td>
		    </tr>
		  
		  <tr>
            <td><b><label id="ID_LABEL_VPN_IPSEC_SETTINGS">IPsec settings</label></b></td>
            <td colspan="2">&nbsp;</td>
		  </tr>
		
		    <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PRESHARE_KEY">Pre-shared key</label></td>
            <td colspan="2"> 
            <input name="PresharedKey" type="text" size=32 maxlength=32 value=(null)></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_ONE_DH_GROUP">Phase 1 DH group</label></td>
            <td colspan="2"> <select size="1" name="Phase1DhGroup">
            <option value=0 selected>Group 1 (768 bits)<option value=1 >Group 2 (1024 bits)<option value=2 >Group 5 (1536 bits)
            </select></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_ONE_ENCRYPTION">Phase 1 encryption</label></td>
            <td colspan="2"> <select size="1" name="Phase1Encryption">
            <option value=1 >DES<option value=2 >3DES<option value=3 >AES-128<option value=4 >AES-192<option value=5 >AES-256
            </select></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_ONE_AUTH">Phase 1 authentication</label></td>
            <td colspan="2"> <select size="1" name="Phase1Authentication">
            <option value=1 >MD5<option value=2 >SHA-1
            </select></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_ONE_SA_LIFETIME">Phase 1 SA lifetime</label></td>
            <td colspan="2"> 
            <input name="Phase1SaLifetime" size=10 maxlength=32 value=0>seconds</td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_TWO_ENCRYPTION">Phase 2 encryption</label></td>
            <td colspan="2"> <select size="1" name="Phase2Encryption" onChange="submit();">
            <option value=1 >DES<option value=2 >3DES<option value=3 >AES-128<option value=4 >AES-192<option value=5 >AES-256
            </select></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_TWO_AUTH">Phase 2 authentication</label></td>
            <td colspan="2"> <select size="1" name="Phase2Authentication" onChange="submit();">
            <option value=1 >MD5<option value=2 >SHA-1
            </select></td>			
		    </tr>
            <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PHASE_TWO_SA_LIFETIME">Phase 2 SA lifetime</label></td>
            <td colspan="2"> 
            <input name="Phase2SaLifetime" size=10 maxlength=32 value=0>seconds</td>			
		    </tr>
		
		<tr>
            <td>&nbsp;</td>
            <td colspan="2">&nbsp; </td>			
		</tr>

	    <tr>
            <td>
		    <INPUT type=submit value="Show Advanced Settings" onClick="ShowAdvanced();"></td>
            <td colspan="2">&nbsp;</td>			
		    </tr>
		<!--
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_KEY_MGT">Key management</label></td>
            <td colspan="2"><select size="1" name="KeyManagement" onChange="submit();">
            <option value=0 selected>Auto (IKE)<option value=1 >Manual
            </select></td>
		</tr>
        
		
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_MANUAL_ENCRYPTION_KEY">Manual Encryption Key</label></td>
            <td colspan="2"> 
            <input name="ManualEncryptionKey" value="" ></td>			
        </tr>
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_MANUAL_AUTH_KEY">Manual Authentication Key</label></td>
            <td colspan="2"> 
            <input name="ManualAuthenticationKey" value="" ></td>			
        </tr>
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_INBOUND_SPI">Inbound SPI</label></td>
            <td colspan="2"> 
            <input name="ManualInboundSpi" size=10 maxlength=32 value=0></td>			
        </tr>
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_OUTBOUND_SPI">Outbound SPI</label></td>
            <td colspan="2"> 
            <input name="ManualOutboundSpi" size=10 maxlength=32 value=0></td>			
        </tr>
		
        
        <tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_IKE_NEGO_MODE">IKE negotiation mode</label></td>
            <td colspan="2"><select size="1" name="NegotiationMode" onChange="submit();">
            <option value=0 selected>Main<option value=1 >Aggressive
            </select></td>
		</tr>
		<tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_PFS">Perfect forward secrecy 
            (PFS)</label></td>
            <td colspan="2"><select size="1" name="PerfectForwardSecrecy" onChange="submit();">
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
		    <tr>
            <td align="right">Phase 2 DH group</td>
            <td colspan="2"> <select size="1" name="Phase2DhGroup">
            <option value=0 selected>Group 1 (768 bits)<option value=1 >Group 2 (1024 bits)<option value=2 >Group 5 (1536 bits)
            </select></td>			
		    </tr>
		<tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_RELAY_DETECTION">Replay detection</label></td>
            <td colspan="2"><select size="1" name="ReplayDetection">
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
		<tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_NETBIOS_BROADCAST_FORWARDING">NetBIOS broadcast 
            forwarding</label></td>
            <td colspan="2"><select size="1" name="NetbiosBroadcast">
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
		<tr>
            <td align="right"><label id="ID_LABEL_VPN_IPSEC_SETTINGS_DEAD_PEER_DETECTION">Dead peer detection</label></td>
            <td colspan="2"><select size="1" name="DeadPeerDetection">
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
		-->
<!-- hide for now            
		<tr>
            <td align="right">NAT traversal</td>
            <td colspan="2"><select size="1" name="NatTraversal" disabled>
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
		<tr>
            <td align="right">IP payload compression</td>
            <td colspan="2"><select size="1" name="IpPayloadCompression" disabled>
            <option value=0 selected>Disabled<option value=1 >Enabled
            </select></td>
		</tr>
-->
		<tr>
            <td>&nbsp;</td>
            <td colspan="2">&nbsp;</td>
		</tr>
		</TBODY>
        </TABLE>

      <TABLE>
        <TBODY>
        <TR>
          <TD align=middle colSpan=4>
		    <INPUT type=submit value=Apply onClick="EditTunnel();" id="ID_BUTTON_APPLY_IPSEC">
		  </TD>
		</TR>
		</TBODY>
      </TABLE>
  </FORM>
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
