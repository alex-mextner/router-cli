<html>
<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 12.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Residential Gateway NAS Media Server</title>
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

<!-- hide me
function onLoadScript()
{
   setTimeout("window.location.reload();",10000);
}
function EnableButton()
{
        var the_box = window.document.UbeeNasMediaServer.MediaServerEnable;
        
        if (the_box.checked == true) {
                window.document.UbeeNasMediaServer.MediaServerDisable.checked = false;
        }
}

function DisableButton()
{
        var the_box = window.document.UbeeNasMediaServer.MediaServerDisable;
        
        if (the_box.checked == true) {
                window.document.UbeeNasMediaServer.MediaServerEnable.checked = false;
        }
}

function ScanAllButton()
{
        var the_box = window.document.UbeeNasMediaServer.MediaServerScanAll;
        
        if (the_box.checked == true) {
                window.document.UbeeNasMediaServer.MediaServerScanExt.checked = false;
        }
}

function ScanExtButton()
{
        var the_box = window.document.UbeeNasMediaServer.MediaServerScanExt;
        if (the_box.checked == true) {
                window.document.UbeeNasMediaServer.MediaServerScanAll.checked = false;
        }
}

function ScanNowButton()
{
    window.document.UbeeNasMediaServer.ScanNow.value = 1;
}

function ApplyBasicButton()
{
    window.document.UbeeNasMediaServer.ApplyActionBasic.value = 1;
}

function ApplyScanSettingsButton()
{
    window.document.UbeeNasMediaServer.ApplyActionScanSettings.value = 2;
    // copy the scan list options to a string to pass back
    appendStringFromList(window.document.UbeeNasMediaServer.scanVideoList, window.document.UbeeNasMediaServer.MediaServerNewSelectedList);
    appendStringFromList(window.document.UbeeNasMediaServer.scanAudioList, window.document.UbeeNasMediaServer.MediaServerNewSelectedList);
    appendStringFromList(window.document.UbeeNasMediaServer.scanImageList, window.document.UbeeNasMediaServer.MediaServerNewSelectedList);
    appendStringFromList(window.document.UbeeNasMediaServer.scanOtherList, window.document.UbeeNasMediaServer.MediaServerNewSelectedList);
}

//Functions for file type lists
function appendStringFromList(srcList, string)
{
  var len = 0;
  for( len = 0; len < srcList.options.length; len++ ) 
  {
    if ( srcList.options[ len ] != null )
    {
      string.value += srcList.options[ len ].value;
      string.value += ':';
    }
  }
}

function compText(a, b) 
{ 
  var retVal = 0;
  if (a.value > b.value) retVal = 1; 
  if (b.value > a.value) retVal = -1; 
//  alert('a=' + a.value + ' b=' + b.value + ' result=' + retVal);
  return retVal;
}

function moveBetweenLists( srcList, destList, moveAll ) 
{
  // Do nothing if nothing is selected
  if (  ( srcList.selectedIndex == -1 ) && ( moveAll == false )   )
  {
    return;
  }
  
  // Copy the destination list to an array
  destArray = new Array( destList.options.length );
  var len = 0;
  for( len = 0; len < destList.options.length; len++ ) 
  {
    if ( destList.options[ len ] != null )
    {
      destArray[ len ] = new Option( destList.options[ len ].text, destList.options[ len ].value, destList.options[ len ].defaultSelected, destList.options[ len ].selected );
    }
  }

  //Walk the source list and copy any selected items to the dest array
  for( var i = 0; i < srcList.options.length; i++ ) 
  { 
    if ( srcList.options[i] != null && ( srcList.options[i].selected == true || moveAll ) )
    {
       // Incorporate into new list
       destArray[ len ] = new Option( srcList.options[i].text, srcList.options[i].value, srcList.options[i].defaultSelected, srcList.options[i].selected );
       len++;
       //Remove from old list
       srcList.options[i]       = null;
       i--;

    }
  }

  // Sort the new dest array
  destArray.sort(compText);   
  
  // Copy the dest array back to the list
  for ( var j = 0; j < destArray.length; j++ ) 
  {
    if ( destArray[ j ] != null )
    {
      destList.options[ j ] = destArray[ j ];
    }
  }
} 

function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}
</script>
</head>
<body onLoad="RadioButtonDevicesAll();RadioButtonDevicesApproved();RadioButtonDevicesNone();">
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
    <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasControl.asp" id="ID_A_NAS_CONTROL">NAS Control</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasStorageAdvSamba.asp" id="ID_A_NAS_STORAGE_ADVSAMBA">Samba</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeNasStorageAdvFtp.asp" id="ID_A_NAS_STORAGE_ADVFTP">FTP</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeNasMediaServer.asp" id="ID_A_MEDIA_SERVER">MediaServer</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
  </ul>
</div>
<div id="main_page">
  <div class="description">
    <h1 id="ID_H1_MEDIA_SERVER">Media Server</h1>
    <h3 id="ID_H3_MEDIA_SERVER_CONF">Configuration</h3>
    <label id="ID_LABEL_MEDIA_SERVER_DESC">This page controls configuration and scanning of the cable modem's media 
    server.</label>
  </div>
  

<div class="display_data">
<form action=/goform/UbeeNasMediaServer method=POST name="UbeeNasMediaServer">
<table width="100%">
<tr valign>
<th colspan="4" ><label id="ID_LABEL_MEDIA_SERVER_BASIC_SETTING"> Basic Settings </label></th>
</tr>
<td><label id="ID_LABEL_MEDIA_SERVER">Media Server</label></td>
<td><input type="radio" name="MediaServerEnable" value="0x0" CHECKED onClick="EnableButton();" ><label id="ID_LABEL_MEDIA_SERVER_ENABLE">Enabled</label></td>
<td ><input type="radio" name="MediaServerDisable" value="0x1"   onClick="DisableButton();" ><label id="ID_LABEL_MEDIA_SERVER_DISABLE">Disabled</label></td>
<td width="50%"><label id="ID_LABEL_MEDIA_SERVER_SCANNING_STATUS">Scanning Status: </label> READY</td>
</tr>
<tr valign>
<td><label id="ID_LABEL_MEDIA_SERVER_NAME">Media Server Name</label>&nbsp</td>
<td colspan="2"><b>
<input name=MediaServerName size=25 maxlength=25 value="EVW32C-0N-DMS" >
</b></td>
<td width="50%"></td></tr>

<td colspan=4 align=left><input type="Submit" id="ID_BUTTON_MEDIA_SETVER_APPLY" value="Apply Basic Settings" align="MIDDLE" onClick="ApplyBasicButton();">
                         <input type="hidden" name="ApplyActionBasic" value=></td>
                         

</table>
<br>
<table width="100%" border="0">
<th colspan="10"> <label id="ID_LABEL_MEDIA_SERVER_SCAN_SETTINGS">Scan Settings</label></th>
<tr valign>
  <td  rowspan="2">&nbsp;</td>
<td rowspan="2" colspan="2"><label id="ID_LABEL_MEDIA_SERVER_SCANNING_METHOD">Scanning Method</label> &nbsp</td>
<td colspan="4"><input type="radio" name="MediaServerScanAll" value="0x5" CHECKED onClick="ScanAllButton();" > <label id="ID_RADIO_MEDIA_SERVER_SCANALL">Scan All Files</label></td>
<td rowspan="2" colspan="3"></td>
</tr>
<tr>
<td colspan="4"><input type="radio" name="MediaServerScanExt" value="0x6"   onClick="ScanExtButton();" > <label id="ID_RADIO_MEDIA_SERVER_SCANFILES">Scan Files By Type</label></td>
</tr>
<tr valign>
<td colspan="10">&nbsp;</td>
</tr>
<tr>
  <td></td>
  <td  colspan="4"><label id="ID_LABEL_MEDIA_SERVER_AVAILABLE_FILES">Available File Types</label></td>
  <td></td>
  <td  colspan="4"><label id="ID_LABEL_MEDIA_SERVER_SELECT_FILES">Selected File Types</label></td>
</tr>
<tr>
  <td width="5%">&nbsp;</td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_AVAILABLE_VIDEO">Video</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_AVAILABLE_AUDIO">Audio</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_AVAILABLE_IMAGE">Image</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_AVAILABLE_OTHER">Other</label></td>
  <td width="5%">&nbsp;</td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_SELECT_VIDEO">Video</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_SELECT_AUDIO">Audio</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_SELECT_IMAGE">Image</label></td>
  <td width="10%"><label id="ID_LABEL_MEDIA_SERVER_SELECT_OTHER">Other</label></td>
</tr>
<tr>  
  <td></td>
  <td  class="style1" >
    <select multiple size="36" style="width:90%"  name="sourceVideoList">
		<option value="3g2"> 3g2</option>
<option value="3gp2"> 3gp2</option>
<option value="asf"> asf</option>
<option value="avc"> avc</option>
<option value="avi"> avi</option>
<option value="bin"> bin</option>
<option value="divx"> divx</option>
<option value="dv"> dv</option>
<option value="flv"> flv</option>
<option value="hdmov"> hdmov</option>
<option value="iso"> iso</option>
<option value="m1v"> m1v</option>
<option value="m2t"> m2t</option>
<option value="m2ts"> m2ts</option>
<option value="m2v"> m2v</option>
<option value="m4p"> m4p</option>
<option value="m4v"> m4v</option>
<option value="mjpeg"> mjpeg</option>
<option value="mjpg"> mjpg</option>
<option value="mkv"> mkv</option>
<option value="mov"> mov</option>
<option value="mp2p"> mp2p</option>
<option value="mp2t"> mp2t</option>
<option value="mp2v"> mp2v</option>
<option value="mp4"> mp4</option>
<option value="mp4ps"> mp4ps</option>
<option value="mpe"> mpe</option>
<option value="mpeg"> mpeg</option>
<option value="mpeg2"> mpeg2</option>
<option value="mpeg4"> mpeg4</option>
<option value="mpg"> mpg</option>
<option value="mpg2"> mpg2</option>
<option value="mpg4"> mpg4</option>
<option value="ogm"> ogm</option>
<option value="qt"> qt</option>
<option value="rmv"> rmv</option>
<option value="rmvb"> rmvb</option>
<option value="rv"> rv</option>
<option value="ts"> ts</option>
<option value="tts"> tts</option>
<option value="vob"> vob</option>
<option value="wmv"> wmv</option>
    
	</select>
  </td>
  <td  class="style1" >
        <select multiple size="36" style="width:90%"  name="sourceAudioList">
		<option value="3gp"> 3gp</option>
<option value="aac"> aac</option>
<option value="ac3"> ac3</option>
<option value="aif"> aif</option>
<option value="aiff"> aiff</option>
<option value="at3p"> at3p</option>
<option value="au"> au</option>
<option value="cda"> cda</option>
<option value="dts"> dts</option>
<option value="flac"> flac</option>
<option value="l16"> l16</option>
<option value="lpcm"> lpcm</option>
<option value="m4a"> m4a</option>
<option value="mid"> mid</option>
<option value="mka"> mka</option>
<option value="mp1"> mp1</option>
<option value="mp2"> mp2</option>
<option value="mp3"> mp3</option>
<option value="mpc"> mpc</option>
<option value="ogg"> ogg</option>
<option value="pcm"> pcm</option>
<option value="ra"> ra</option>
<option value="ram"> ram</option>
<option value="rm"> rm</option>
<option value="rmi"> rmi</option>
<option value="snd"> snd</option>
<option value="wav"> wav</option>
<option value="wave"> wave</option>
<option value="wma"> wma</option>
    
	</select>
  </td>
  <td  class="style1" >
      <select multiple size="36" style="width:90%"  name="sourceImageList">
		<option value="bmp"> bmp</option>
<option value="gif"> gif</option>
<option value="ico"> ico</option>
<option value="jpe"> jpe</option>
<option value="jpeg"> jpeg</option>
<option value="jpg"> jpg</option>
<option value="pcd"> pcd</option>
<option value="png"> png</option>
<option value="pnm"> pnm</option>
<option value="ppm"> ppm</option>
<option value="qtf"> qtf</option>
<option value="qti"> qti</option>
<option value="qtif"> qtif</option>
<option value="tif"> tif</option>
<option value="tiff"> tiff</option>
    
	</select>
  </td>
  <td  class="style1" >
      <select multiple size="36" style="width:90%"  name="sourceOtherList">
		<option value="asx"> asx</option>
<option value="bup"> bup</option>
<option value="dks"> dks</option>
<option value="idx"> idx</option>
<option value="m3u"> m3u</option>
<option value="mpl"> mpl</option>
<option value="pjs"> pjs</option>
<option value="pls"> pls</option>
<option value="psb"> psb</option>
<option value="scr"> scr</option>
<option value="ssa"> ssa</option>
<option value="stl"> stl</option>
<option value="sub"> sub</option>
<option value="vsf"> vsf</option>
<option value="zeg"> zeg</option>
    
	</select>
  </td>
  <td ></td>
  <td  class="style1" >
    <select multiple size="36" style="width:90%"  name="scanVideoList">
		    
    </select>
  </td>
  <td  class="style1" >
    <select multiple size="36" style="width:90%"  name="scanAudioList">
		    
    </select>
  </td>
  <td  class="style1" >
    <select multiple size="36" style="width:90%"  name="scanImageList">
		    
    </select>
  </td>
  <td  class="style1" >
    <select multiple size="36" style="width:90%"  name="scanOtherList">
		    
    </select>
  </td>
</tr>
<tr>
 <td ></td>
  <td class="style1" >
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_VIDEO_SELECT" onClick="moveBetweenLists( this.form.sourceVideoList,  this.form.scanVideoList, false )"  
    value="Selected    >">     <BR>
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_VIDEO_ALLVIDEO" onClick="moveBetweenLists( this.form.sourceVideoList,  this.form.scanVideoList, true  )"  
    value="All Video  >>">     <BR>
  </td>
  <td class="style1" >
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_AUDIO_SELECT" onClick="moveBetweenLists( this.form.sourceAudioList,  this.form.scanAudioList, false )"  
    value="Selected    >"><br>
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_AUDIO_ALLAUDIO" onClick="moveBetweenLists( this.form.sourceAudioList,  this.form.scanAudioList, true  )"  
    value="All Audio  >>"></td>
  <td class="style1" >
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_IMAGE_SELECT" onClick="moveBetweenLists( this.form.sourceImageList,  this.form.scanImageList, false )"  
    value="Selected    >"><br>
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_IMAGE_ALLIMAGE" onClick="moveBetweenLists( this.form.sourceImageList,  this.form.scanImageList, true  )"  
    value="All Image  >>"></td>
  <td class="style1" >
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_OTHER_SELECT" onClick="moveBetweenLists( this.form.sourceOtherList,  this.form.scanOtherList, false )"  
    value="Selected    >"><br>
    <input type="button" style="width:90%"  id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_OTHER_ALLOTHER" onClick="moveBetweenLists( this.form.sourceOtherList,  this.form.scanOtherList, true  )"  
    value="All Other  >>"></td>
    <td >    </td>
  <td class="style1" >
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_VIDEO_SELECT" onClick="moveBetweenLists( this.form.scanVideoList, this.form.sourceVideoList,  false )"  
    value="< Selected   ">     <BR>
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_VIDEO_ALLVIDEO" onClick="moveBetweenLists( this.form.scanVideoList, this.form.sourceVideoList,  true  )"  
    value="<< All Video ">     <BR>
  </td>
  <td class="style1" >
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_AUDIO_SELECT" onClick="moveBetweenLists( this.form.scanAudioList, this.form.sourceAudioList,  false )"  
    value="< Selected   ">     <BR>
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_AUDIO_ALLAUDIO" onClick="moveBetweenLists( this.form.scanAudioList, this.form.sourceAudioList,  true  )"  
    value="<< All Audio ">     <BR>
  </td>
  <td class="style1" >
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_IMAGE_SELECT" onClick="moveBetweenLists( this.form.scanImageList, this.form.sourceImageList,  false )"  
    value="< Selected   ">     <BR>
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_IMAGE_ALLIMAGE" onClick="moveBetweenLists( this.form.scanImageList, this.form.sourceImageList,  true  )"  
    value="<< All Image ">     <BR>
  </td>
  <td class="style1" >
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_OTHER_SELECT" onClick="moveBetweenLists( this.form.scanOtherList, this.form.sourceOtherList,  false )"  
    value="< Selected   ">     <BR>
    <input type="button" style="width:90%" id="ID_BUTTON_MEDIA_SERVER_SELECT_OTHER_ALLOTHER" onClick="moveBetweenLists( this.form.scanOtherList, this.form.sourceOtherList,  true  )"  
    value="<< All Other ">     <BR>
  </td>
</tr>
<tr>
	<td></td>
  <td class="style1" colspan="4" >
    <input type="button" style="width:90%" 
    id="ID_BUTTON_MEDIA_SERVER_AVAILABLE_ADDALL" onClick="moveBetweenLists(this.form.sourceVideoList, this.form.scanVideoList, true);moveBetweenLists(this.form.sourceAudioList, this.form.scanAudioList, true);moveBetweenLists(this.form.sourceImageList, this.form.scanImageList, true);moveBetweenLists(this.form.sourceOtherList, this.form.scanOtherList, true)"  
    value="Add All Types >>>">
    </td>
	<td></td>
  <td class="style1" colspan="4" >
    <input type="button" style="width:90%" 
    id="ID_BUTTON_MEDIA_SERVER_SELECT_REMOVEALL" onClick="moveBetweenLists(this.form.scanVideoList, this.form.sourceVideoList, true);moveBetweenLists(this.form.scanAudioList, this.form.sourceAudioList, true);moveBetweenLists(this.form.scanImageList, this.form.sourceImageList, true);moveBetweenLists(this.form.scanOtherList, this.form.sourceOtherList, true)"  
    value="<<< Remove All Types">
    </td>
</tr>
<tr><td colspan="10">&nbsp;</td></tr>
<tr valign>
	<td valign colspan="10">
		<input type="checkbox" name="MediaServerScheduledScanEnabled" value="0x17"  ><label id="ID_LABEL_MEDIA_SERVER_ENABLE_SCANNING">Enable scheduled scanning every</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		<!--webbot bot="Validation" s-data-type="Integer" s-number-separators="," i-maximum-length="6" -->
		<input type="text" name=MediaServerScheduledScanInterval size=6 maxlength=5 value="0"> <label id="ID_LABEL_MEDIA_SERVER_ENABLE_SCANNING_MINUTE"> minutes</label>
    </td>
</tr>

<tr><td colspan="10">&nbsp;</td></tr>
<tr>
<td colspan=10 align=left><input type="Submit" id="ID_BUTTON_MEDIA_SERVER_APPLY_SCAN" value="Apply Scan Settings" align="MIDDLE" onClick="ApplyScanSettingsButton();">
                         <input type="hidden" name="MediaServerNewSelectedList" value=></td>
                         <input type="hidden" name="ApplyActionScanSettings" value=>
     
</tr><td colspan="10"></td><tr>
<td colspan="10"><input type="Submit" id="ID_LABEL_MEDIA_SERVER_SCAN_NOW" value="Scan Now" align="MIDDLE" onClick="ScanNowButton();">
    <input type="hidden" name="ScanNow" value=>

</td>
</table>
<br>
</form>

</div>
<div id=footer></div>
<div id="copyright">�2021 Ubee Interactive. All rights reserved.</div>

</body>

</html>
