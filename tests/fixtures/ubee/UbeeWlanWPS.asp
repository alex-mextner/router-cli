<!DOCTYPE html>
<html>

<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-STORE">
<title>Residential Gateway Configuration: Wireless - Primary Network</title>

<script src="js/jquery-1.10.2.js"></script>
<script src="js/ubee_js_apis.js"> </script>
<script src="js/jquery_countdown.js"> </script>
<script>

var web_item_data_wireless_page_setup_jsonData =  ' { "wireless_2g_page_enable": 1, "wireless_5g_page_enable": 1 }'  ;

var web_item_data_wireless_setup_jsonData =  ' { "wireless_2g_enable": 0, "wireless_2g_ssid_broadcast": 1, "wireless_2g_wps_enable": 1, "wireless_2g_wps_mode": 0, "wireless_2g_wps_pin": "", "wireless_2g_wps_last_status": "WPS_IDLE" } ' ;

var web_item_data_wireless_setup_5g_jsonData =   ' { "wireless_5g_enable": 0, "wireless_5g_ssid_broadcast": 1, "wireless_5g_wps_enable": 1, "wireless_5g_wps_mode": 0, "wireless_5g_wps_pin": "", "wireless_5g_wps_last_status": "WPS_IDLE" } ' ;


var web_item_data_wireless_page_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_page_setup_jsonData);

var web_item_data_wireless_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_setup_jsonData);

var web_item_data_wireless_setup_5g_jsonObj = jQuery.parseJSON(web_item_data_wireless_setup_5g_jsonData);

var language_jsonData = ' { "web_language": 0 } ' ;


var language_jsonObj = jQuery.parseJSON(language_jsonData); 
 
 
function ubee_jscript_setup_web_wireless_items()
{
	
	if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0 &&
	   web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0 )
	{
		if( (web_item_data_wireless_setup_jsonObj.wireless_2g_wps_enable == 0 ||
			 web_item_data_wireless_setup_jsonObj.wireless_2g_enable == 0 ||
			 web_item_data_wireless_setup_jsonObj.wireless_2g_ssid_broadcast == 0) &&
			(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_enable == 0 ||
			 web_item_data_wireless_setup_5g_jsonObj.wireless_5g_enable == 0 ||
			 web_item_data_wireless_setup_5g_jsonObj.wireless_5g_ssid_broadcast == 0 ) )
			{
					ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 0);
			}
			else
			{
                if(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_enable != 0)
                {
                    ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 1);
                }
                else
                {
                    if(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_enable != 0)
                    {
                        ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 1);
                    }
                    else
                    {
                        ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 0);
                    }
                }
            }
    
    		if(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_mode == 1 )
    		{
    			$('#wps_mode_dropdown_list').val(1);
    		}
    		else
    		{
    			$('#wps_mode_dropdown_list').val(0);			
    		}
    		
    		$('#wps_client_pin_textbox').val(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_pin);
    		
    		
    		
    		if(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_mode == 1 )
    		{
    			$('#wps_mode_dropdown_list_5g').val(1);
    		}
    		else
    		{
    			$('#wps_mode_dropdown_list_5g').val(0);			
    		}
    		
    		$('#wps_client_pin_textbox_5g').val(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_pin);
	}
	else
	{
		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
		{			
			if( web_item_data_wireless_setup_jsonObj.wireless_2g_wps_enable == 0 ||
				web_item_data_wireless_setup_jsonObj.wireless_2g_enable == 0 ||
				web_item_data_wireless_setup_jsonObj.wireless_2g_ssid_broadcast == 0 )
			{
				ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 0);
			}

            if(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_enable != 0)
            {
                ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 1);
            }
			
			if(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_mode == 1 )
			{
				$('#wps_mode_dropdown_list').val(1);
			}
			else
			{
				$('#wps_mode_dropdown_list').val(0);			
			}
			
			$('#wps_client_pin_textbox').val(web_item_data_wireless_setup_jsonObj.wireless_2g_wps_pin);
			
		}
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
		{
			if( web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_enable == 0 ||
				web_item_data_wireless_setup_5g_jsonObj.wireless_5g_enable == 0 ||
				web_item_data_wireless_setup_5g_jsonObj.wireless_5g_ssid_broadcast == 0 )
			{
				ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 0);
			}

            if(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_enable != 0)
            {
                ubee_jscript_setup_input_radio($("input[name='wireless_wps_radio']"), 1);
            }
			
			if(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_mode == 1 )
			{
				$('#wps_mode_dropdown_list_5g').val(1);
			}
			else
			{
				$('#wps_mode_dropdown_list_5g').val(0);			
			}
			
			$('#wps_client_pin_textbox_5g').val(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_pin);
		
			//$('#wps_last_status_5g').val(web_item_data_wireless_setup_5g_jsonObj.wireless_5g_wps_last_status);
		}
	}
} 


function ubee_jscript_setup_input_radio(input_radio_obj, value)
{

	input_radio_obj.each(function() {
		if($(this).val() == value )
		{
			$(this).prop("checked","checked");
		}
		else
		{
			$(this).removeAttr("checked");	
		}
	});
}
 
 function wps_mode_div_callback(fad_enable)
{
	if ($("#wps_mode_dropdown_list option:selected").val() == "1" )
	{
		if( fad_enable == true)
		{
			($("div#wps_pin_div")).fadeIn("slow", function(){
			$(this).show()});
			setup_wps(1);
		}
		else
		{
			$("div#wps_pin_div").show();	
		}
	}
	else
	{
		if( fad_enable == true)
		{			
			($("div#wps_pin_div")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wps_pin_div").hide();
		}
	}
}
 
function wps_mode_5g_div_callback(fad_enable)
{
	if ($("#wps_mode_dropdown_list_5g option:selected").val() == "1" )
	{
		if( fad_enable == true)
		{
			($("div#wps_pin_div_5g")).fadeIn("slow", function(){
			$(this).show()});
			setup_wps(0);
		}
		else
		{
			$("div#wps_pin_div_5g").show();
		}
	}
	else
	{
		if( fad_enable == true)
		{			
			($("div#wps_pin_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wps_pin_div_5g").hide();
		}
	}
}
 


function wps_div_enable_callback(fad_enable)
{
	if ($("input#wireless_wps_disable_radio").is(":checked"))
	{
		if( fad_enable == true)
		{
			($("div#wps_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wps_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wps_div").hide();
			
			$("div#wps_div_5g").hide();
			

		}
		
	}
	else
	{
		if( fad_enable == true)
		{
			if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
			{		
				($("div#wps_div")).fadeIn("slow", function(){
				$(this).show()});
			}
			else
			{
				$("div#wps_div").hide();
			}
			
			if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
			{
				($("div#wps_div_5g")).fadeIn("slow", function(){
				$(this).show()});
			}
			else
			{
				$("div#wps_div_5g").hide();
			}
		}
		else
		{
			if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
			{
				$("div#wps_div").show();
			}
			else
			{
				$("div#wps_div").hide();
			}
			
			if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
			{
				$("div#wps_div_5g").show();
			}
			else
			{
				$("div#wps_div_5g").hide();
			}
			
		}
	}
	
	wps_mode_div_callback(fad_enable);
	wps_mode_5g_div_callback(fad_enable);
}



function wps_last_status_div_enable_callback(press, fad_enable)
{
	if (press == false)
	{
		if( fad_enable == true)
		{
			($("div#wps_last_status_div")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wps_last_status_div").hide();
		}
	}
	else
	{
		if( fad_enable == true)
		{
			($("div#wps_last_status_div")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wps_last_status_div").show();
		}
	}
}



function wps_last_status_div_enable_5g_callback(press, fad_enable)
{
	if (press == false)
	{
		if( fad_enable == true)
		{
			($("div#wps_last_status_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wps_last_status_div_5g").hide();
		}
	}
	else
	{
		if( fad_enable == true)
		{
			($("div#wps_last_status_div_5g")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wps_last_status_div_5g").show();
		}
	}
}


 function setup_wps(band)
 {
		var jsonObj = {};
		var wireless_wps_status;
		var wireless_wps_pin;

	 	if( band == 1)
		{
			wireless_wps_status = $("input[name='wireless_wps_radio']:checked").val();
			wireless_wps_mode =$('select#wps_mode_dropdown_list :selected').val();
			wireless_wps_pin =$('#wps_client_pin_textbox').val();
			
			if( wireless_wps_status != 0)
			{
				jsonObj['wireless_2g_wps_mode'] = wireless_wps_mode;
				if( wireless_wps_mode == 1)
				{
					jsonObj['wireless_2g_wps_pin'] = wireless_wps_pin;
				}
			}
		}
		else
		{

			wireless_wps_mode =$('select#wps_mode_dropdown_list_5g :selected').val();
			wireless_wps_pin = $('#wps_client_pin_textbox_5g').val();		
			wireless_wps_status = $("input[name='wireless_wps_radio']:checked").val();

			if( wireless_wps_status != 0)
			{
				jsonObj['wireless_5g_wps_mode'] = wireless_wps_mode;
				if( wireless_wps_mode == 1)
				{
					jsonObj['wireless_5g_wps_pin'] = wireless_wps_pin;
				}
			}
		}

		$.ajax({
			url: '/goform/ubee_post',
			type: 'POST',
			data: JSON.stringify(jsonObj),
			contentType: 'application/json; charset=utf-8',
			dataType: 'json',
			async: false,
			success: function() {
				alert("OK");
			}
		});	 
  }

  function disable5gBtn() {
       document.getElementById("ID_BUTTON_WPS_CONNECT_5G").disabled = true;
  }
  

  function undisable5gBtn() {
       document.getElementById("ID_BUTTON_WPS_CONNECT_5G").disabled = false;
  }

  function disable2gBtn() {
       document.getElementById("ID_BUTTON_WPS_CONNECT_2G").disabled = true;
  }
  

  function undisable2gBtn() {
       document.getElementById("ID_BUTTON_WPS_CONNECT_2G").disabled = false;
  }


 
$(function() {
	
	if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
	{
		wps_last_status_div_enable_5g_callback(false, false);
	}
	
	if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
	{
	  wps_last_status_div_enable_callback(false, false);
        }


	ubee_jscript_setup_web_wireless_items(); 
	wps_div_enable_callback(false);

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

	$( "input[name=wireless_wps_radio]" ).click(function(){
		
		var wireless_wps_status = $("input[name='wireless_wps_radio']:checked").val();
		var jsonObj = {};
		

		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0 )
		{			
			jsonObj['wireless_2g_wps_enable'] = wireless_wps_status;	
		}		

		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0 )
		{
			jsonObj['wireless_5g_wps_enable'] = wireless_wps_status;
		}
		
		$.ajax({
			url: '/goform/ubee_post',
			type: 'POST',
			data: JSON.stringify(jsonObj),
			contentType: 'application/json; charset=utf-8',
			dataType: 'json',
			async: false,
		success: function(msg) {
			alert("OK");
			}
		});	
		location.reload();
		
		
	});


     $("button#ID_BUTTON_APPLY_WPS_2G").click(function() {

		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable == 0)
		{
			return;
		}
	
  		setup_wps(1);
     });

	$("button#ID_BUTTON_APPLY_WPS_5G").click(function() {
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable == 0)
		{
			return;
		}
		setup_wps(0);  
    });

		 
	 $("button#ID_BUTTON_WPS_CONNECT_2G").click(function() {
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable == 0)
		{
			return;
		}
		
		var jsonObj = {};
		var wireless_wps_mode =$('select#wps_mode_dropdown_list_2g :selected').val();
		 
        disable5gBtn();

		jsonObj['wireless_2g_wps_mode'] = wireless_wps_mode;
		 
		jsonObj['wireless_2g_wps_trigger'] = 1;			
				
			$.ajax({
			url: '/goform/ubee_post',
			type: 'POST',
			data: JSON.stringify(jsonObj),
			contentType: 'application/json; charset=utf-8',
			dataType: 'json',
			async: false,
			success: function(msg) {
				alert("OK");
			}
		});
		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
		{			
		wps_last_status_div_enable_callback(true, true);	
		}
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
		{			
		wps_last_status_div_enable_5g_callback(false, true);				
		}

	 });
	 

	$("button#ID_BUTTON_WPS_CONNECT_5G").click(function() {
	
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable == 0)
		{
			return;
		}
	
	
		var jsonObj = {};
		var wireless_wps_mode =$('select#wps_mode_dropdown_list_5g :selected').val();
		
		disable2gBtn();

		jsonObj['wireless_5g_wps_trigger'] = 1;	
		jsonObj['wireless_5g_wps_mode'] = wireless_wps_mode;
		 					
			$.ajax({
			url: '/goform/ubee_post',
			type: 'POST',
			data: JSON.stringify(jsonObj),
			contentType: 'application/json; charset=utf-8',
			dataType: 'json',
			async: false,
			success: function(msg) {
				alert("OK");
			}
		});			
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
		{			
			wps_last_status_div_enable_callback(false, true);	
		}
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
		{		
			wps_last_status_div_enable_5g_callback(true, true);	
		}

	 }); 
	 

  	 $('#countdown').countdown({
		  date: +(new Date),
		  render: function(data) {
		  },
		  onEnd: function() { 
					get_update_info_data_async();
		  }
		}).on("click", function() {
			//do nothing
	 });
		function get_update_info_data_async()
		{
		        var jsonObj = { wireless_5g_wps_last_status : "unknow", wireless_2g_wps_last_status : "unknow"};
	
			$.ajax({
				url: '/goform/ubee_get_async',
				type: 'POST',
				data: JSON.stringify(jsonObj),
				contentType: 'application/json; charset=utf-8',
				dataType: 'json',
				error: function()
				{
				},
				success:function(msg){
					network_status_item = msg ;
					//alert(JSON.stringify(network_status_item));
					$('#countdown').removeClass('ended').data('countdown').update(+(new Date) + 4000).start();
					wireless_info_json_obj = jQuery.parseJSON (JSON.stringify(network_status_item));

					
					if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
					{
						$('#wps_last_status_5g').html(wireless_info_json_obj.wireless_5g_wps_last_status);

						if(wireless_info_json_obj.wireless_5g_wps_last_status == 'WPS_IDLE' || wireless_info_json_obj.wireless_5g_wps_last_status == 'WPS_TIMEOUT' || wireless_info_json_obj.wireless_5g_wps_last_status == 'WPS_MSG_ERR' ){
							undisable2gBtn();
							wps_last_status_div_enable_callback(false, true);
						}
						
						if(wireless_info_json_obj.wireless_5g_wps_last_status == 'WPS_OK' ){
							undisable2gBtn();
						}
						
						
					}

					if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
					{
						$('#wps_last_status_2g').html(wireless_info_json_obj.wireless_2g_wps_last_status);
					
						if(wireless_info_json_obj.wireless_2g_wps_last_status == 'WPS_IDLE' || wireless_info_json_obj.wireless_2g_wps_last_status == 'WPS_TIMEOUT' || wireless_info_json_obj.wireless_2g_wps_last_status == 'WPS_MSG_ERR' ){
							undisable5gBtn();
							wps_last_status_div_enable_5g_callback(false, true);
											 
						}
						
						if(wireless_info_json_obj.wireless_2g_wps_last_status == 'WPS_OK' ){
							undisable5gBtn();
						}

						
					}
               },
			});	
		}	


	 	$( "select[name=wps_mode_dropdown_list]" ).change(function(){
		
			if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
			{
				wps_mode_div_callback(true);
			}
		});	 
	 
	 	$( "select[name=wps_mode_dropdown_list_5g]" ).change(function(){
			
			if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
			{
				wps_mode_5g_div_callback(true);
			}
		});
  });
	
  function MultiLanguage_Hide()
{
	document.getElementById("ID_LABEL_WEB_LANGUAGE").style.display = "none";
	document.getElementById("ID_DROPDOWNLIST_SELECTOR_WEB_LANGUAGE").style.display = "none";
}

$( document ).ready(function() {
   
});
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
<table width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td width="17%" align="left" valign="top"><div id="navigation_bar">
      <ul>
            <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanBasic.asp" id="ID_A_BASIC">Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanSecurity.asp" id="ID_A_SECURITY" >Security</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeWlanWPS.asp" id="ID_A_WPS" >WPS</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanAccessControl.asp"  id="ID_A_ACL">Access Control</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>

      </ul>
    </div></td>
    <td width="83%" valign="top"><div id="main_page2">
      <div class="description">
        <h1  id="ID_H1_WPS_TITLE_2G" >WPS Enable</h1>
      </div>
      <table width="100%" border="0" cellspacing="0" cellpadding="0" class="ui-state-hover">
        <tr>
          <td><table width="100%" border="0" cellpadding="2" cellspacing="0">
            <tr>
              <td><input type="radio" id="wireless_wps_disable_radio" name="wireless_wps_radio" value="0" />
                <label for="wireless_wps_disable_radio" id="ID_LABEL_WPS_OFF_2G">OFF</label>
                <input type="radio" id="wireless_wps_enable_radio" name="wireless_wps_radio" value="1" />
                <label for="wireless_wps_enable_radio" id="ID_LABEL_WPS_ON_2G">ON</label>                </td>
              </tr>
            <tr>
              <td><div id="wps_div">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" class="ui-state-hover">
                  <tr>
                    <td><table width="100%" border="0" cellpadding="2" cellspacing="0">
                      <tr>
                        <td width="100%"><hr /></td>
                      </tr>
                      <tr>
                        <td><table width="100%" border="0" cellspacing="0" cellpadding="2">
                          <tr>
                            <td colspan="2"><h2 id="ID_H2_WPS_TITLE_2G" >WPS 2.4G setup</h2></td>
                          </tr>
                          <tr>
                            <td width="14%"><label id="ID_LABEL_WPS_MODE_2G">WPS Mode</label></td>
                            <td width="86%"><select name="wps_mode_dropdown_list"  id="wps_mode_dropdown_list">
                              <option value="1">PIN</option>
                              <option value="0" id="wps_mode_dropdown_list_option_pin">PBC</option>
                            </select></td>
                          </tr>
                        </table>
                          <div id="wps_pin_div">
                            <table width="100%" border="0" cellspacing="0" cellpadding="2">
                              <tr>
                                <td width="14%"><label id="ID_LABEL_WPS_CLIENT_PIN_2G"> WPS Client Pin</label></td>
                                <td width="86%" ><input name="wps_client_pin_textbox" type="password" id="wps_client_pin_textbox" title="Please enter the wps client pin." size="9" maxlength="8" />
                                  <label id="ID_LABEL_WPS_CLIENT_PIN_DESC_2G">(Please Apply Pin code before connect)</label></td>
                              </tr>
                            </table>
                          </div>
                          <table width="100%" border="0" cellspacing="0" cellpadding="2">
                            <tr>
                              <td width="14%"><label id="ID_LABEL_WPS_TRIGGER_2G
">WPS Trigger</label></td>
                              <td width="86%" ><button  id="ID_BUTTON_WPS_CONNECT_2G">Connect</button></td>
                            </tr>
                          </table>
                          <div id="wps_last_status_div">
                            <table width="100%" border="0" cellspacing="0" cellpadding="2">
                              <tr>
                                <td width="15%">Last Status:</td>
                                <td width="85%" ><label id="wps_last_status_2g"></label></td>
                              </tr>
                            </table>
                          </div></td>
                      </tr>
                    </table></td>
                  </tr>
                  <tr>
                    <td align="left"><button id="ID_BUTTON_APPLY_WPS_2G">Apply</button></td>
                  </tr>
                </table>
              </div></td>
            </tr>
            <tr>
              <td><div id="wps_div_5g">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" class="ui-state-hover">
                  <tr>
                    <td><table width="100%" border="0" cellpadding="2" cellspacing="0">
                      <tr>
                        <td width="100%"><hr /></td>
                      </tr>
                      <tr>
                        <td><table width="100%" border="0" cellspacing="0" cellpadding="2">
                          <tr>
                            <td colspan="2"><h2 id="ID_H2_WPS_TITLE_5G">WPS 5G setup</h2></td>
                          </tr>
                          <tr>
                            <td width="15%"><label id="ID_LABEL_WPS_MODE_5G">WPS Mode</label></td>
                            <td width="85%"><select name="wps_mode_dropdown_list_5g" id="wps_mode_dropdown_list_5g">
                              <option value="1" id="wps_mode_dropdown_list_option_pbc_5g">PIN</option>
                              <option value="0" id="wps_mode_dropdown_list_option_pin_5g">PBC</option>
                            </select></td>
                          </tr>
                        </table>
                          <div id="wps_pin_div_5g">
                            <table width="100%" border="0" cellspacing="0" cellpadding="2">
                              <tr>
                                <td width="15%"><label id="ID_LABEL_WPS_CLIENT_PIN_5G">WPS Client Pin</label></td>
                                <td width="85%" ><input name="wps_client_pin_textbox_5g" type="password" id="wps_client_pin_textbox_5g" title="Please enter the wps client pin." size="9" maxlength="8" />
                                  <label id="ID_LABEL_WPS_CLIENT_PIN_DESC_5G"> (Please Apply Pin code before connect)</label></td>
                              </tr>
                            </table>
                          </div>
                          <table width="100%" border="0" cellspacing="0" cellpadding="2">
                            <tr>
                              <td width="15%"><label id="ID_LABEL_WPS_TRIGGER_5G">WPS Trigger</label></td>
                              <td width="85%" ><button id="ID_BUTTON_WPS_CONNECT_5G">Connect</button></td>
                            </tr>
                          </table>
                          <div id="wps_last_status_div_5g">
                            <table width="100%" border="0" cellspacing="0" cellpadding="2">
                              <tr>
                                <td width="15%">Last Status:</td>
                                <td width="85%" ><label id="wps_last_status_5g"></label></td>
                              </tr>
                            </table>
                          </div></td>
                      </tr>
                    </table></td>
                  </tr>
                  <tr>
                    <td align="left"><button id="ID_BUTTON_APPLY_WPS_5G">Apply</button></td>
                  </tr>
                </table>
              </div></td>
            </tr>
          </table></td>
        </tr>
        <tr>
          <td align="left"></td>
        </tr>
      </table>
    </div></td>
  </tr>
</table>
			<div id="navigation-bottom-line"></div>
    	  </div> 
<!-- hold -->

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
<div id="countdown" ></div>
</body>

</html>
