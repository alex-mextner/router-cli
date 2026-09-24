<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway  Static Lease </title>
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

  function formSubmitCheck()
  {
      f = window.document.UbeeLanStaticLease;
      Zero = "00";

      for (i =1; i <=7; i++) {
          //alert("i:"+i+" ; j:"+j);
          if ( eval("f.tempClear0"+i+".checked") == true ) {
              eval("f.MacAddStaticLease0" + i + "MA0.value = Zero");
              eval("f.MacAddStaticLease0" + i + "MA1.value = Zero");
              eval("f.MacAddStaticLease0" + i + "MA2.value = Zero");
              eval("f.MacAddStaticLease0" + i + "MA3.value = Zero");
              eval("f.MacAddStaticLease0" + i + "MA4.value = Zero");
              eval("f.MacAddStaticLease0" + i + "MA5.value = Zero");
              eval("f.IpAddStaticLease" + i + "IPX.value = 0");
              eval("f.tempClear0" + i + ".checked = false");
          }
      }
      f.submit();
  }

function CheckIPRange(ipaddress)
{
    var myStartIP = document.getElementById("MY_POOL_START_IP").value;
    var myEndIP = document.getElementById("MY_POOL_END_IP").value;

    var inputIP = ipaddress.value;
    var inputIPArr = inputIP.split(".");
    var myStartIPArr = myStartIP.split(".");
    var myEndIPArr = myEndIP.split(".");

    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(inputIP)) {
        if( inputIPArr[0] == myStartIPArr[0] ) {
            if( inputIPArr[1] == myStartIPArr[1]) {
                if( inputIPArr[2] == myStartIPArr[2] ) {
                    if( inputIPArr[3] == myStartIPArr[3] ) {
                        alert("Warning - First IP address is not allow for static IP");
                        return (false);
                    }
                    
                    var num1 = Number(inputIPArr[3]);
                    var num2 = Number(myStartIPArr[3]);
                    var num3 = Number(myEndIPArr[3]);

                    if( (num1 > num2 ) && (num1 <= num3 ) ) {
                        return (true);
                    }

                    alert("Warning - The input IP address is not in the DHCP IP pool");
                    return (false);
                }
            }
        }

        alert("Warning - The input IP address is not under LAN subnet");
        return (false);
    }
    
    alert("Warning - You have entered an invalid IP address!")  
    return (false);    
}

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}

</script>
</head>

<body onLoad="onLoadScript()">
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
        <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN_SETUP" >Setup</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeLanDhcp.asp" id="ID_A_LAN_DHCP">DHCP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeLanStaticLease.asp"  id="ID_A_LAN_STATICLEASE" >Static Lease</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_HEADER_LAN_STATICLEASE_TITLE" >Static Lease</h1>
   <label id="ID_LABEL_LAN_STATICLEASE_DESC"> This page allows configuration of DHCP static lease.</label>
  </div>

<form action=/goform/UbeeLanStaticLease method=POST name="UbeeLanStaticLease">

                <table>
                  <tr>
                    <td><b><label id="ID_LABEL_LAN_STATICLEASE_PRIVATE">IP Lease Range: </label>192.168.0.11 -- 192.168.0.254<b></td>
                  </tr>
                </table>

                <br>
                <table align="left" bgcolor="#EFEFEF" bordercolor="#999999" border="1" cellpadding="0" cellspacing="0" height="350" rules="groups" width="85%">
                  <tr valign="top">
                    <td align="center" class="field" nowrap><label id="ID_LABEL_STATICLEASE_INDEX">Index</label></font></td>
                    <td align="center" class="field" nowrap><label id="ID_LABEL_STATICLEASE_MAC">MAC Address</label></td>
                    <td align="center" class="field" nowrap><label id="ID_LABEL_STATICLEASE_IP">IP Address</label></td>
                    <td align="center" class="field" nowrap><label id="ID_LABEL_STATICLEASE_CLEAR">Clear</label></td>
                  </tr>
                  <!-- Static lease Entry 1 -->
                  <tr>
                    <td align="center">1.</td>
                    <td align="left">
                      <input name="MacAddStaticLease01MA0" size="1" maxlength="2" value=02>
                      <b>:</b>
                      <input name="MacAddStaticLease01MA1" size="1" maxlength="2" value=00>
                      <b>:</b>
                      <input name="MacAddStaticLease01MA2" size="1" maxlength="2" value=00>
                      <b>:</b>
                      <input name="MacAddStaticLease01MA3" size="1" maxlength="2" value=00>
                      <b>:</b>
                      <input name="MacAddStaticLease01MA4" size="1" maxlength="2" value=01>
                      <b>:</b>
                      <input name="MacAddStaticLease01MA5" size="1" maxlength="2" value=01>
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease1IPX size=16 maxlength=15 value=192.168.0.39 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear01">
                    </td>
                  </tr>
                  <!-- Static lease Entry 2 -->
                  <tr>
                    <td align="center">2.</td>
                    <td align="left">
                      <input name="MacAddStaticLease02MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease02MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease02MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease02MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease02MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease02MA5" size="1" maxlength="2" value=02 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease2IPX size=16 maxlength=15 value=192.168.0.52 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear02" onClick="ShowStatusMsg(msg1000,0);">
                    </td>
                  </tr>
                  <!-- Static lease Entry 3 -->
                  <tr>
                    <td align="center">3.</td>
                    <td align="left">
                      <input name="MacAddStaticLease03MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease03MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease03MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease03MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease03MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease03MA5" size="1" maxlength="2" value=03 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease3IPX size=16 maxlength=15 value=192.168.0.66 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear03">
                    </td>
                  </tr>
                  <!-- Static lease Entry 4 -->
                  <tr>
                    <td align="center">4.</td>
                    <td align="left">
                      <input name="MacAddStaticLease04MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease04MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease04MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease04MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease04MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease04MA5" size="1" maxlength="2" value=04 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease4IPX size=16 maxlength=15 value=192.168.0.11 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear04" >
                    </td>
                  </tr>
                  <!-- Static lease Entry 5 -->
                  <tr>
                    <td align="center">5.</td>
                    <td align="left">
                      <input name="MacAddStaticLease05MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease05MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease05MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease05MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease05MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease05MA5" size="1" maxlength="2" value=05 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease5IPX size=16 maxlength=15 value=192.168.0.26 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear05" >
                    </td>
                  </tr>
                  <!-- Static lease Entry 6 -->
                  <tr valign="top">
                    <td align="center">6.</td>
                    <td align="left">
                      <input name="MacAddStaticLease06MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease06MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease06MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease06MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease06MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease06MA5" size="1" maxlength="2" value=06 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease6IPX size=16 maxlength=15 value=192.168.0.27 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear06" >
                    </td>
                  </tr>
                  <!-- Static lease Entry 7 -->
                  <tr valign="top">
                    <td align="center">7.</td>
                    <td align="left">
                      <input name="MacAddStaticLease07MA0" size="1" maxlength="2" value=02 >
                      <b>:</b>
                      <input name="MacAddStaticLease07MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease07MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease07MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease07MA4" size="1" maxlength="2" value=01 >
                      <b>:</b>
                      <input name="MacAddStaticLease07MA5" size="1" maxlength="2" value=07 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease7IPX size=16 maxlength=15 value=192.168.0.12 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear07" >
                    </td>
                  </tr>
                  <!-- Static lease Entry 8 -->
                  <tr valign="top">
                    <td align="center">8.</td>
                    <td align="left">
                      <input name="MacAddStaticLease08MA0" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease08MA1" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease08MA2" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease08MA3" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease08MA4" size="1" maxlength="2" value=00 >
                      <b>:</b>
                      <input name="MacAddStaticLease08MA5" size="1" maxlength="2" value=00 >
                    </td>
  <td align="center"><input type="text" name=IpAddStaticLease8IPX size=16 maxlength=15 value=0.0.0.0 onchange="CheckIPRange(this);"></td>

                    <td align="center">
                      <input type="checkbox" name="tempClear08" >
                    </td>
                  </tr>
            <td height="10" colspan="4" align="center">
              <input type="Button" value="Apply" align="MIDDLE" onClick="formSubmitCheck();"id="ID_BUTTON_STATICLEASE_APPLY">
            </td>
          </tr>
        </table>
        <input type="hidden" id="MY_POOL_START_IP" name="MY_POOL_START_IP" value="192.168.0.10">
        <input type="hidden" id="MY_POOL_END_IP" name="MY_POOL_END_IP" value="192.168.0.254">
        <input type="hidden" name="StaticLeaseStatusFlag" value="0">
        <br>
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
