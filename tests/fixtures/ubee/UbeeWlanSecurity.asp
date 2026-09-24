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
<script>


var web_item_data_wireless_page_setup_jsonData =  ' { "wireless_2g_page_enable": 1, "wireless_5g_page_enable": 1 }'  ;
var web_item_data_wireless_page_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_page_setup_jsonData);


var web_item_data_wireless_setup_jsonData = ' { "wireless_2g_auth_mode": 4, "wireless_2g_sec_encrypt_type": 4, "wireless_2g_sec_wep_default_key": 1, "wireless_2g_sec_wep64_key1": "", "wireless_2g_sec_wep64_key2": "", "wireless_2g_sec_wep64_key3": "", "wireless_2g_sec_wep64_key4": "", "wireless_2g_sec_wep128_key1": "", "wireless_2g_sec_wep128_key2": "", "wireless_2g_sec_wep128_key3": "", "wireless_2g_sec_wep128_key4": "", "wireless_2g_sec_wpae_radius_ip1": "0.0.0.0", "wireless_2g_sec_wpae_radius_port": 1812, "wireless_2g_sec_wpae_radius_share_sec": "", "wireless_2g_sec_wpap_preshare_key": "testtesttest", "wireless_2g_wps_enable": 1, "wireless_2g_wps_mode": 0, "wireless_2g_wps_pin": "" } ' ;


var web_item_data_wireless_5g_setup_jsonData = ' { "wireless_5g_auth_mode": 4, "wireless_5g_sec_encrypt_type": 4, "wireless_5g_sec_wep_default_key": 1, "wireless_5g_sec_wep64_key1": "", "wireless_5g_sec_wep64_key2": "", "wireless_5g_sec_wep64_key3": "", "wireless_5g_sec_wep64_key4": "", "wireless_5g_sec_wep128_key1": "", "wireless_5g_sec_wep128_key2": "", "wireless_5g_sec_wep128_key3": "", "wireless_5g_sec_wep128_key4": "", "wireless_5g_sec_wpae_radius_ip1": "0.0.0.0", "wireless_5g_sec_wpae_radius_port": 1812, "wireless_5g_sec_wpae_radius_share_sec": "", "wireless_5g_sec_wpap_preshare_key": "testtesttest", "wireless_5g_wps_enable": 1, "wireless_5g_wps_mode": 0, "wireless_5g_wps_pin": "" } ' ;

var web_item_data_wireless_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_setup_jsonData);
var web_item_data_wireless_5g_setup_jsonObj = jQuery.parseJSON(web_item_data_wireless_5g_setup_jsonData);
 
var language_jsonData = ' { "web_language": 0 } ' ;
var language_jsonObj = jQuery.parseJSON(language_jsonData); 
 
function disablePages()
{
	if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable == 0)
	{
		$("div#DESCRIPTION_2G").hide();
		$("div#MAIN_PAGE_2G").hide();
	}
	
	if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable == 0)
	{
		$("div#DESCRIPTION_5G").hide();
		$("div#MAIN_PAGE_5G").hide();
	}
}

function ValidateIPaddress(ipaddress) {  
  if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)) {  
    return (true)  
  }  
  alert("You have entered an invalid IP address!")  
  return (false)  
}

function ubee_jscript_setup_web_wireless_security_items()
{
	 var auth_mode = web_item_data_wireless_setup_jsonObj.wireless_2g_auth_mode ;
	 var encrypt_type = web_item_data_wireless_setup_jsonObj.wireless_2g_sec_encrypt_type;
	
	//No security
	if( auth_mode == 0 && encrypt_type == 0)
	{
		$('#security_mode_dropdown_list').val(0);
	}
	else
	{
		var wpa_version = 0;
		
		//WEP Security 128 Bit
		if(auth_mode == 1 &&  encrypt_type == 1 )
		{
			$('#security_mode_dropdown_list').val(1);
		}
		//WEP Security 64 Bit
		else if(auth_mode == 1 &&  encrypt_type == 5 )
		{
			$('#security_mode_dropdown_list').val(4);
		}
		//WPA-PSK security
		else if(auth_mode == 2 || auth_mode == 3 || auth_mode == 4 )
		{

			 if(  auth_mode == 2)
			 {
				 wpa_version = 0;
			 }
			 else  if( auth_mode == 3)
			 {
				  wpa_version = 1;
			 }
			 else  if(  auth_mode == 4)
			 {
				  wpa_version = 2;
			 }
			 else
			 {
				  wpa_version = 0;
			 }
  			$('#security_mode_dropdown_list').val(2);
			$('#auth_mode_version_dropdown_list').val(wpa_version);

		}
		//WPA security
		else if(auth_mode == 5 || auth_mode == 6 || auth_mode == 7 )
		{

			 if(  auth_mode == 5)
			 {
				 wpa_version = 0;
			 }
			 else  if( auth_mode == 6)
			 {
				  wpa_version = 1;
			 }
			 else  if(  auth_mode == 7)
			 {
				  wpa_version = 2;
			 }
			 else
			 {
				  wpa_version = 0;
			 }
  			$('#security_mode_dropdown_list').val(3);
			$('#auth_mode_version_dropdown_list').val(wpa_version);

		}
		else
		{
			$('#security_mode_dropdown_list').val(0);
		}


		//tkip
		if( encrypt_type == 2)
		{
  			$('#encrypt_mode_dropdown_list').val(0);
		}
		//aes
		else if( encrypt_type == 3)
		{
  			$('#encrypt_mode_dropdown_list').val(1);

		}
		//tkip and aes mix mode
		else if( encrypt_type == 4)
		{
  			$('#encrypt_mode_dropdown_list').val(2);
		}
		else
		{
			$('#encrypt_mode_dropdown_list').val(0);
		}
	}

}   
  
function ubee_jscript_setup_web_wireless_security_5g_items()
{
	 var auth_mode = web_item_data_wireless_5g_setup_jsonObj.wireless_5g_auth_mode ;
	 var encrypt_type = web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_encrypt_type;
		
	//No security
	if( auth_mode == 0 && encrypt_type == 0)
	{
		$('#security_mode_dropdown_list_5g').val(0);
	}
	else
	{
		var wpa_version = 0;
		
		//WEP Security 128 Bit
		if(auth_mode == 1 &&  encrypt_type == 1 )
		{
			$('#security_mode_dropdown_list_5g').val(1);
		}
		//WEP Security 64 Bit
		else if(auth_mode == 1 &&  encrypt_type == 5 )
		{
			$('#security_mode_dropdown_list_5g').val(4);
		}
		//WPA-PSK security
		else if(auth_mode == 2 || auth_mode == 3 || auth_mode == 4 )
		{

			 if(  auth_mode == 2)
			 {
				 wpa_version = 0;
			 }
			 else  if( auth_mode == 3)
			 {
				  wpa_version = 1;
			 }
			 else  if(  auth_mode == 4)
			 {
				  wpa_version = 2;
			 }
			 else
			 {
				  wpa_version = 0;
			 }
  			$('#security_mode_dropdown_list_5g').val(2);
			$('#auth_mode_version_dropdown_list_5g').val(wpa_version);

		}
		//WPA security
		else if(auth_mode == 5 || auth_mode == 6 || auth_mode == 7 )
		{

			 if(  auth_mode == 5)
			 {
				 wpa_version = 0;
			 }
			 else  if( auth_mode == 6)
			 {
				  wpa_version = 1;
			 }
			 else  if(  auth_mode == 7)
			 {
				  wpa_version = 2;
			 }
			 else
			 {
				  wpa_version = 0;
			 }
  			$('#security_mode_dropdown_list_5g').val(3);
			$('#auth_mode_version_dropdown_list_5g').val(wpa_version);

		}
		else
		{
			$('#security_mode_dropdown_list_5g').val(0);
		}


		//tkip
		if( encrypt_type == 2)
		{
  			$('#encrypt_mode_dropdown_list_5g').val(0);
		}
		//aes
		else if( encrypt_type == 3)
		{
  			$('#encrypt_mode_dropdown_list_5g').val(1);

		}
		//tkip and aes mix mode
		else if( encrypt_type == 4)
		{
  			$('#encrypt_mode_dropdown_list_5g').val(2);
		}
		else
		{
			$('#encrypt_mode_dropdown_list_5g').val(0);
		}
	}

} 
 
function ubee_jscript_setup_web_wireless_items()
{
	if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable != 0)
	{
		ubee_jscript_setup_web_wireless_security_items();
		var auth_mode_2g = web_item_data_wireless_setup_jsonObj.wireless_2g_auth_mode ;
		var encrypt_type_2g = web_item_data_wireless_setup_jsonObj.wireless_2g_sec_encrypt_type;
		
		$('#radius_ip').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wpae_radius_ip1);
		$('#radius_port').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wpae_radius_port);
		$('#radius_share_secret_textbox').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wpae_radius_share_sec);
		
		$('#wpa_preshare_key').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wpap_preshare_key);
		
		$('#default_key_dropdown_list').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep_default_key);
		if(auth_mode_2g == 1 &&  encrypt_type_2g == 5 )
		{
			$('#wep_key1').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key1);
			$('#wep_key2').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key2);
			$('#wep_key3').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key3);
			$('#wep_key4').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key4);		
	
		}
		else
		{
			$('#wep_key1').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key1);
			$('#wep_key2').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key2);
			$('#wep_key3').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key3);
			$('#wep_key4').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key4);		
		}	
			
	}

	if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable != 0)
	{
	
		ubee_jscript_setup_web_wireless_security_5g_items();
		
		var auth_mode_5g = web_item_data_wireless_5g_setup_jsonObj.wireless_5g_auth_mode ;
		var encrypt_type_5g = web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_encrypt_type;
			
		$('#radius_ip_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wpae_radius_ip1);
		$('#radius_port_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wpae_radius_port);
		$('#radius_share_secret_textbox_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wpae_radius_share_sec);
		
		$('#wpa_preshare_key_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wpap_preshare_key);
		
		$('#default_key_dropdown_list_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep_default_key);
		if(auth_mode_5g == 1 &&  encrypt_type_5g == 5 )
		{
			$('#wep_key1_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key1);
			$('#wep_key2_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key2);
			$('#wep_key3_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key3);
			$('#wep_key4_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key4);		
		}
		else
		{
			$('#wep_key1_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key1);
			$('#wep_key2_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key2);
			$('#wep_key3_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key3);
			$('#wep_key4_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key4);		
		
		}
	}
}

function wireless_security_mode_div_callback(fad_enable)
{
	if ($("#security_mode_dropdown_list option:selected").val() == "0" )
	{
		if( fad_enable == true)
		{
			($("div#wpa_e_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wep_security_div")).fadeIn("slow", function(){
			$(this).hide()});
			
			($("div#wpa_security_div")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wpa_e_security_div").hide();
			
			$("div#wpa_p_security_div").hide();
			
			$("div#wep_security_div").hide();
			
			$("div#wpa_security_div").hide();		
		}
		

	}
	else if ($("#security_mode_dropdown_list option:selected").val() == "1" || 
	$("#security_mode_dropdown_list option:selected").val() == "4" )
	{
		if( fad_enable == true)
		{
			($("div#wpa_e_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wep_security_div")).fadeIn("slow", function(){
			$(this).show()});
			
			($("div#wpa_security_div")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wpa_e_security_div").hide();
			
			$("div#wpa_p_security_div").hide();
			
			$("div#wep_security_div").show();
			
			$("div#wpa_security_div").hide();		
		}
		
		var wps_type = $("#security_mode_dropdown_list option:selected").val();
		
		if( wps_type == "4"  )
		{
			$('#wep_key1').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key1);
			$('#wep_key2').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key2);
			$('#wep_key3').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key3);
			$('#wep_key4').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep64_key4);			
		}
		else
		{
			$('#wep_key1').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key1);
			$('#wep_key2').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key2);
			$('#wep_key3').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key3);
			$('#wep_key4').val(web_item_data_wireless_setup_jsonObj.wireless_2g_sec_wep128_key4);		
		}
		

	}
	else if ($("#security_mode_dropdown_list option:selected").val() == "2" )
	{
		if( fad_enable == true)
		{
			($("div#wep_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_e_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div")).fadeIn("slow", function(){
			$(this).show()});
			
			($("div#wpa_security_div")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wep_security_div").hide();
			
			$("div#wpa_e_security_div").hide();
			
			$("div#wpa_p_security_div").show();
			
			$("div#wpa_security_div").show();
		}
	}
	else
	{
		if( fad_enable == true)
		{
			($("div#wep_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_e_security_div")).fadeIn("slow", function(){
			$(this).show()});	
			
			($("div#wpa_security_div")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wep_security_div").hide();
			
			$("div#wpa_p_security_div").hide();
			
			$("div#wpa_e_security_div").show();	
			
			$("div#wpa_security_div").show();
		}

	}
}
	

function wireless_security_mode_div_callback_5g(fad_enable)
{
	if ($("#security_mode_dropdown_list_5g option:selected").val() == "0" )
	{
		if( fad_enable == true)
		{
			($("div#wpa_e_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wep_security_div_5g")).fadeIn("slow", function(){
			$(this).hide()});
			
			($("div#wpa_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wpa_e_security_div_5g").hide();
			
			$("div#wpa_p_security_div_5g").hide();
			
			$("div#wep_security_div_5g").hide();
			
			$("div#wpa_security_div_5g").hide();		
		}
		

	}
	else if ($("#security_mode_dropdown_list_5g option:selected").val() == "1" || 
	  $("#security_mode_dropdown_list_5g option:selected").val() == "4"  )
	{
		if( fad_enable == true)
		{
			($("div#wpa_e_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wep_security_div_5g")).fadeIn("slow", function(){
			$(this).show()});
			
			($("div#wpa_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
		}
		else
		{
			$("div#wpa_e_security_div_5g").hide();
			
			$("div#wpa_p_security_div_5g").hide();
			
			$("div#wep_security_div_5g").show();
			
			$("div#wpa_security_div_5g").hide();		
		}
		
			
		var wps_type = $("#security_mode_dropdown_list_5g option:selected").val();
		
		if( wps_type == "4"  )
		{
			$('#wep_key1_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key1);
			$('#wep_key2_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key2);
			$('#wep_key3_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key3);
			$('#wep_key4_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep64_key4);		
		}
		else
		{
			$('#wep_key1_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key1);
			$('#wep_key2_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key2);
			$('#wep_key3_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key3);
			$('#wep_key4_5g').val(web_item_data_wireless_5g_setup_jsonObj.wireless_5g_sec_wep128_key4);		
		
		}
		

	}
	else if ($("#security_mode_dropdown_list_5g option:selected").val() == "2" )
	{
		if( fad_enable == true)
		{
			($("div#wep_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_e_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div_5g")).fadeIn("slow", function(){
			$(this).show()});
			
			($("div#wpa_security_div_5g")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wep_security_div_5g").hide();
			
			$("div#wpa_e_security_div_5g").hide();
			
			$("div#wpa_p_security_div_5g").show();
			
			$("div#wpa_security_div_5g").show();
		}
	}
	else
	{
		if( fad_enable == true)
		{
			($("div#wep_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_p_security_div_5g")).fadeOut("slow", function(){
			$(this).hide()});
			
			($("div#wpa_e_security_div_5g")).fadeIn("slow", function(){
			$(this).show()});	
			
			($("div#wpa_security_div_5g")).fadeIn("slow", function(){
			$(this).show()});
		}
		else
		{
			$("div#wep_security_div_5g").hide();
			
			$("div#wpa_p_security_div_5g").hide();
			
			$("div#wpa_e_security_div_5g").show();	
			
			$("div#wpa_security_div_5g").show();
		}

	}
	
}


	
	

 
 $(function() {
	
	disablePages();
	ubee_jscript_setup_web_wireless_items(); 
	wireless_security_mode_div_callback(false);
	wireless_security_mode_div_callback_5g(false);	
	

	$("input#wpa_preshare_key_5g" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key1_5g" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key2_5g" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	$("input#wep_key3_5g" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key4_5g" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	
	$("input#wpa_preshare_key" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key1" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key2" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	$("input#wep_key3" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
	
	$("input#wep_key4" )
	  .mouseover(function() {
		$(this).attr("type","text");
	  })
	  .mouseout(function() {
		$(this).attr("type","password");
	});
			
				
if ( !ubee_multi_language_control() )
{
	MultiLanguage_Hide();
}
else 
{
	//  var page = document.location.href.match(/[^\/]+$/)[0].split(".")[0];
	    var pathArray = window.location.pathname.split( '?' );
		    var page = pathArray[0].split(".")[0].replace(/\//g,'');
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
	$("button#ID_BUTTON_CANCEL_SECURITY_2G").click(function() {
		
		location.reload();
	 }); 

	$("button#ID_BUTTON_CANCEL_SECURITY_5G").click(function() {
		
		location.reload();
	 }); 
	 
	
	$("button#ID_BUTTON_APPLY_SECURITY_2G").click(function() {
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_2g_page_enable == 0)
		{
			return;
		}
		
		var jsonObj = {};
		var security_mode = parseInt( $('#security_mode_dropdown_list option:selected').val());
		var wpa_version = parseInt($('#auth_mode_version_dropdown_list option:selected').val());
		var encrypt_mode =  parseInt($('#encrypt_mode_dropdown_list option:selected').val());
		var radius_ip = $('#radius_ip').val();
		var radius_port = parseInt($('#radius_port').val());
		var radius_key = $('#radius_share_secret_textbox').val();
		var wpa_psk_key = $('#wpa_preshare_key').val();
		var default_wep_key_id = parseInt($('#default_key_dropdown_list').val());
		var wep_key1 = $('#wep_key1').val();
		var wep_key2 = $('#wep_key2').val();
		var wep_key3 = $('#wep_key3').val();
		var wep_key4 = $('#wep_key4').val();
		


			//No security
			if( security_mode == 0 )
			{
				jsonObj['wireless_2g_auth_mode'] = 0;
				jsonObj['wireless_2g_sec_encrypt_type'] = 0;
	
			}
			//WEP 128 bit
			else if ( security_mode == 1 )
			{
				jsonObj['wireless_2g_auth_mode'] = 1;
				jsonObj['wireless_2g_sec_encrypt_type'] = 1;	
				jsonObj['wireless_2g_sec_wep_default_key'] = default_wep_key_id;			
				
				if( default_wep_key_id == 1)
				{
					if( wep_key1.length != 13)
					{
						alert("WEP key 1 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 2)
				{
					if( wep_key2.length != 13)
					{
						alert("WEP key 2 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 3)
				{
					if( wep_key3.length != 13)
					{
						alert("WEP key 3 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 4)
				{
					if( wep_key4.length != 13)
					{
						alert("WEP key 4 length must be 13 ASCII");
						return;	
					}
				}		
				
				jsonObj['wireless_2g_sec_wep128_key1'] = wep_key1;			
				jsonObj['wireless_2g_sec_wep128_key2'] = wep_key2;			
				jsonObj['wireless_2g_sec_wep128_key3'] = wep_key3;			
				jsonObj['wireless_2g_sec_wep128_key4'] = wep_key4;			

			}
			//WEP 64 bit
			else if ( security_mode == 4 )
			{
				jsonObj['wireless_2g_auth_mode'] = 1;
				jsonObj['wireless_2g_sec_encrypt_type'] = 5;	
				jsonObj['wireless_2g_sec_wep_default_key'] = default_wep_key_id;			
				
				if( default_wep_key_id == 1)
				{
					if( wep_key1.length != 5)
					{
						alert("WEP key 1 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 2)
				{
					if( wep_key2.length != 5)
					{
						alert("WEP key 2 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 3)
				{
					if( wep_key3.length != 5)
					{
						alert("WEP key 3 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 4)
				{
					if( wep_key4.length != 5)
					{
						alert("WEP key 4 length must be 5 ASCII");
						return;	
					}
				}		
				
				jsonObj['wireless_2g_sec_wep64_key1'] = wep_key1;			
				jsonObj['wireless_2g_sec_wep64_key2'] = wep_key2;			
				jsonObj['wireless_2g_sec_wep64_key3'] = wep_key3;			
				jsonObj['wireless_2g_sec_wep64_key4'] = wep_key4;			

			}
			//WPA-P
			else if ( security_mode == 2 )
			{

				if( wpa_version == 0)
				{
					jsonObj['wireless_2g_auth_mode'] = 2;
	
				}
				else if(wpa_version == 1)
				{
					jsonObj['wireless_2g_auth_mode'] = 3;
	
				}
				else
				{
					jsonObj['wireless_2g_auth_mode'] = 4;
					
				}

				if( encrypt_mode == 0)
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 2;			
	
				}
				else if(encrypt_mode == 1)
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 3;			
	
				}
				else
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 4;			
					
				}

				if( wpa_psk_key.length < 8)
				{
					alert("length of WPA preshare key must larger than 8");
					return;
				}
				
				jsonObj['wireless_2g_sec_wpap_preshare_key'] = wpa_psk_key;


			}
			//WPA-E
			else if ( security_mode == 3 )
			{
			    if( ValidateIPaddress(radius_ip) == false )
			    {
			        return;
			    }
			    
				if( wpa_version == 0)
				{
					jsonObj['wireless_2g_auth_mode'] = 5;
	
				}
				else if(wpa_version == 1)
				{
					jsonObj['wireless_2g_auth_mode'] = 6;
	
				}
				else
				{
					jsonObj['wireless_2g_auth_mode'] = 7;
					
				}

				if( encrypt_mode == 0)
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 2;			
	
				}
				else if(encrypt_mode == 1)
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 3;			
	
				}
				else
				{
					jsonObj['wireless_2g_sec_encrypt_type'] = 4;			
					
				}	
				
				jsonObj['wireless_2g_sec_wpae_radius_ip1'] = radius_ip;
				jsonObj['wireless_2g_sec_wpae_radius_port'] = radius_port;
				jsonObj['wireless_2g_sec_wpae_radius_share_sec'] = radius_key;
				
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

	 }); 
	 

$("button#ID_BUTTON_APPLY_SECURITY_5G").click(function() {
		
		if(web_item_data_wireless_page_setup_jsonObj.wireless_5g_page_enable == 0)
		{
			return;
		}
		
		
		var jsonObj = {};
		var security_mode = parseInt( $('#security_mode_dropdown_list_5g option:selected').val());
		var wpa_version = parseInt($('#auth_mode_version_dropdown_list_5g option:selected').val());
		var encrypt_mode =  parseInt($('#encrypt_mode_dropdown_list_5g option:selected').val());
		var radius_ip = $('#radius_ip_5g').val();
		var radius_port = parseInt($('#radius_port_5g').val());
		var radius_key = $('#radius_share_secret_textbox_5g').val();
		var wpa_psk_key = $('#wpa_preshare_key_5g').val();
		var default_wep_key_id = parseInt($('#default_key_dropdown_list_5g').val());
		var wep_key1 = $('#wep_key1_5g').val();
		var wep_key2 = $('#wep_key2_5g').val();
		var wep_key3 = $('#wep_key3_5g').val();
		var wep_key4 = $('#wep_key4_5g').val();
		


			//No security
			if( security_mode == 0 )
			{
				jsonObj['wireless_5g_auth_mode'] = 0;
				jsonObj['wireless_5g_sec_encrypt_type'] = 0;
	
			}
			//WEP 128
			else if ( security_mode == 1 )
			{
				jsonObj['wireless_5g_auth_mode'] = 1;
				jsonObj['wireless_5g_sec_encrypt_type'] = 1;	
				jsonObj['wireless_5g_sec_wep_default_key'] = default_wep_key_id;			
				
				if( default_wep_key_id == 1)
				{
					if( wep_key1.length != 13)
					{
						alert("WEP key 1 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 2)
				{
					if( wep_key2.length != 13)
					{
						alert("WEP key 2 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 3)
				{
					if( wep_key3.length != 13)
					{
						alert("WEP key 3 length must be 13 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 4)
				{
					if( wep_key4.length != 13)
					{
						alert("WEP key 4 length must be 13 ASCII");
						return;	
					}
				}		
				
				jsonObj['wireless_5g_sec_wep128_key1'] = wep_key1;			
				jsonObj['wireless_5g_sec_wep128_key2'] = wep_key2;			
				jsonObj['wireless_5g_sec_wep128_key3'] = wep_key3;			
				jsonObj['wireless_5g_sec_wep128_key4'] = wep_key4;			

			}
			//WEP 64
			else if ( security_mode == 4 )
			{
				jsonObj['wireless_5g_auth_mode'] = 1;
				jsonObj['wireless_5g_sec_encrypt_type'] = 5;	
				jsonObj['wireless_5g_sec_wep_default_key'] = default_wep_key_id;			
				
				if( default_wep_key_id == 1)
				{
					if( wep_key1.length != 5)
					{
						alert("WEP key 1 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 2)
				{
					if( wep_key2.length != 5)
					{
						alert("WEP key 2 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 3)
				{
					if( wep_key3.length != 5)
					{
						alert("WEP key 3 length must be 5 ASCII");
						return;	
					}
				}
				else if( default_wep_key_id == 4)
				{
					if( wep_key4.length != 5)
					{
						alert("WEP key 4 length must be 5 ASCII");
						return;	
					}
				}		
				
				jsonObj['wireless_5g_sec_wep64_key1'] = wep_key1;			
				jsonObj['wireless_5g_sec_wep64_key2'] = wep_key2;			
				jsonObj['wireless_5g_sec_wep64_key3'] = wep_key3;			
				jsonObj['wireless_5g_sec_wep64_key4'] = wep_key4;			

			}
			//WPA-P
			else if ( security_mode == 2 )
			{

				if( wpa_version == 0)
				{
					jsonObj['wireless_5g_auth_mode'] = 2;
	
				}
				else if(wpa_version == 1)
				{
					jsonObj['wireless_5g_auth_mode'] = 3;
	
				}
				else
				{
					jsonObj['wireless_5g_auth_mode'] = 4;
					
				}

				if( encrypt_mode == 0)
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 2;			
	
				}
				else if(encrypt_mode == 1)
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 3;			
	
				}
				else
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 4;			
					
				}

				if( wpa_psk_key.length < 8)
				{
					alert("length of WPA preshare key must larger than 8");
					return;
				}
				
				jsonObj['wireless_5g_sec_wpap_preshare_key'] = wpa_psk_key;


			}
			//WPA-E
			else if ( security_mode == 3 )
			{
			    if( ValidateIPaddress(radius_ip) == false )
			    {
			        return;
			    }

				if( wpa_version == 0)
				{
					jsonObj['wireless_5g_auth_mode'] = 5;
	
				}
				else if(wpa_version == 1)
				{
					jsonObj['wireless_5g_auth_mode'] = 6;
	
				}
				else
				{
					jsonObj['wireless_5g_auth_mode'] = 7;
					
				}

				if( encrypt_mode == 0)
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 2;			
	
				}
				else if(encrypt_mode == 1)
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 3;			
	
				}
				else
				{
					jsonObj['wireless_5g_sec_encrypt_type'] = 4;			
					
				}	
				
				jsonObj['wireless_5g_sec_wpae_radius_ip1'] = radius_ip;
				jsonObj['wireless_5g_sec_wpae_radius_port'] = radius_port;
				jsonObj['wireless_5g_sec_wpae_radius_share_sec'] = radius_key;
				
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

	 }); 

	 
	 $( "select#security_mode_dropdown_list" ).change(function(){
			wireless_security_mode_div_callback(true);
	 });
	 
	 $( "select#security_mode_dropdown_list_5g" ).change(function(){
			wireless_security_mode_div_callback_5g(true);
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

			<div id="navigation-bottom-line"></div>
			<table width="100%" border="0" cellspacing="0" cellpadding="0">
			  <tr>
			    <td width="17%" align="left" valign="top"><div id="navigation_bar">
			      <ul>
			            <li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanBasic.asp" id="ID_A_BASIC">Basic</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeWlanSecurity.asp" id="ID_A_SECURITY" >Security</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanWPS.asp" id="ID_A_WPS">WPS</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeWlanAccessControl.asp"  id="ID_A_ACL">Access Control</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div>
		          </ul>
		        </div></td>
			    <td width="83%" valign="top" ><div id="main_page2" >
			      <div class="description"  id="DESCRIPTION_2G">
			        <h1 id="ID_H1_HEADER_WIRELESS_SECURITY_TITLE_2G" >Wireless 2.4G Security</h1>
			        <label id="ID_LABEL_WIRELESS_SECURITY_DESC_2G" >This page allows configuration of the 2.4G wireless security settings.</label>
		          </div>
                  <div  id="MAIN_PAGE_2G">
			      <table width="100%" border="0" cellspacing="1" cellpadding="2">
			        <tr>
			          <td width="100%"><div id="wirless_enable_div">
			            <table width="100%" border="0" cellspacing="1" cellpadding="2">
			              <tr>
			                <td width="100%"><table width="100%" border="0" cellspacing="0" cellpadding="0">
			                  <tr>
			                    <td width="21%"><label id="ID_LABEL_WIRELESS_SECURITY_MODE_2G">Security Mode</label></td>
			                    <td width="79%"><select name="security_mode_dropdown_list" id="security_mode_dropdown_list">
			                      <option value="0"  >Disable</option>
			                      <option value="2" selected="selected" >WPA Personal</option>
			                      <option value="3" >WPA Enterprise</option>
			                      </select></td>
			                    </tr>
			                  <tr>
			                    <td colspan="2"><div id="wpa_security_div" >
			                      <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                        <tr>
			                          <td width="21%"><label id="ID_LABEL_WPA_VERSION_2G"> WPA version</label></td>
			                          <td width="79%"><select name="auth_mode_version_dropdown_list" id="auth_mode_version_dropdown_list">
			                            <option value="1">Version 2</option>
			                            <option value="2">v1/v2 Mix</option>
			                            </select></td>
			                          </tr>
			                        <tr>
			                          <td width="21%"><label id="ID_LABEL_ENCRYPT_TYPE_2G">Encrypt Type</label></td>
			                          <td><select name="encrypt_mode_dropdown_list"  id="encrypt_mode_dropdown_list">
			                            <option value="1">AES</option>
			                            <option value="2">Auto</option>
			                            </select></td>
			                          </tr>
			                        <tr>
			                          <td colspan="2"><div id="wpa_e_security_div" >
			                            <table width="100%" border="0" cellspacing="0" cellpadding="2">
			                              <tr>
			                                <td width="21%"><label id="ID_LABEL_RADIUS_SERVER_IP_2G">Radius Server IP</label></td>
			                                <td width="79%" ><input type="text" id="radius_ip" title="Please enter the Radius IP." size="20" maxlength="17" /></td>
			                                </tr>
			                              <tr>
			                                <td><label id="ID_LABEL_RADIUS_SERVER_PORT_2G">Radius Port</label></td>
			                                <td><input type="text" id="radius_port"  size="6" maxlength="5" /></td>
			                                </tr>
			                              <tr>
			                                <td><label id="ID_LABEL_RADIUS_SERVER_SHARE_SECRET_2G">Radius Share Secret</label></td>
			                                <td><input type="password"  id="radius_share_secret_textbox" title="Please enter the share secret." size="32" maxlength="64" /></td>
			                                </tr>
			                              </table>
			                            </div>
			                            <div id="wpa_p_security_div" >
			                              <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                                <tr>
			                                  <td width="21%"><label id="ID_LABEL_WPA_PRESHARE_KEY_2G">Pre-Share Key</label></td>
			                                  <td width="79%" ><input type="password" id="wpa_preshare_key" title="Please preshare key." size="32" maxlength="64" /></td>
			                                  </tr>
			                                </table>
			                              </div></td>
			                          </tr>
			                        </table>
			                      </div>
			                      <div id="wep_security_div">
			                        <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                          <tr>
			                            <td width="21%"><label id="ID_LABEL_WEP_DEFAULT_KEY_2G">Default Key</label></td>
			                            <td width="79%" ><select name="default_key_dropdown_list" id="default_key_dropdown_list">
			                              <option value="1">1</option>
			                              <option value="2">2</option>
			                              <option value="3">3</option>
			                              <option value="4">4</option>
			                              </select></td>
			                            </tr>
			                          <tr>
			                            <td><label id="ID_LABEL_WEP_KEY1_2G">WEP Key 1</label></td>
			                            <td><input  type="password" id="wep_key1" title="Please enter the WEP Key1" size="28" maxlength="24" /></td>
			                            </tr>
			                          <tr>
			                            <td><label id="ID_LABEL_WEP_KEY1_2G">WEP Key 2</label></td>
			                            <td><input name="wep_key2" type="password" id="wep_key2" title="Please enter the WEP Key3" size="28" maxlength="24" /></td>
			                            </tr>
			                          <tr>
			                            <td><label id-"ID_LABEL_WEP_KEY3_2G">WEP Key 3</label> </td>
			                            <td><input name="wep_key3" type="password" id="wep_key3" title="Please enter the WEP Key3" size="28" maxlength="24" /></td>
			                            </tr>
			                          <tr>
			                            <td><label id-"ID_LABEL_WEP_KEY4_2G">WEP Key 4</label></td>
			                            <td><input name="wep_key4" type="password" id="wep_key4" title="Please enter the WEP Key4" size="28" maxlength="24" /></td>
			                            </tr>
			                          </table>
			                        </div></td>
			                    </tr>
			                  </table></td>
		                  </tr>
		                </table>
			            </div></td>
		            </tr>
			        <tr>
			          <td ><button id="ID_BUTTON_APPLY_SECURITY_2G">Apply</button>
                      <button id="ID_BUTTON_CANCEL_SECURITY_2G">Cancel</button></td>
		            </tr>
		          </table>
                  </div>
			      <div class="description"  id="DESCRIPTION_5G">
			        <h1 id="ID_H1_HEADER_WIRELESS_SECURITY_TITLE_5G">Wireless 5G Security </h1>
		          <label id="ID_LABEL_WIRELESS_SECURITY_DESC_5G"> This page allows configuration of the 5G wireless security settings.</label></div>
   			      <div id="MAIN_PAGE_5G">
                  <table width="100%" border="0" cellspacing="1" cellpadding="2">
			        <tr>
			          <td width="100%"><table width="100%" border="0" cellspacing="1" cellpadding="2">
			            <tr>
			              <td width="100%"><table width="100%" border="0" cellspacing="0" cellpadding="0">
			                <tr>
			                  <td width="21%"><label id="ID_LABEL_WIRELESS_SECURITY_MODE_5G">Security Mode</label></td>
			                  <td width="79%"><select name="security_mode_dropdown_list_5g" id="security_mode_dropdown_list_5g">
			                    <option value="0"  >Disable</option>
			                    <option value="2" >WPA Personal</option>
			                    <option value="3" >WPA Enterprise</option>
			                    </select></td>
			                  </tr>
			                <tr>
			                  <td colspan="2"><div id="wpa_security_div_5g" >
			                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                      <tr>
			                        <td width="21%"><label id="ID_LABEL_WPA_VERSION_5G">WPA version</label></td>
			                        <td width="79%"><select name="auth_mode_version_dropdown_list_5g" id="auth_mode_version_dropdown_list_5g">
			                          <option value="1">Version 2</option>
			                          <option value="2">v1/v2 Mix</option>
			                          </select></td>
			                        </tr>
			                      <tr>
			                        <td width="21%"><label id="ID_LABEL_ENCRYPT_TYPE_5G">Encrypt Type</label></td>
			                        <td><select name="encrypt_mode_dropdown_list_5g"  id="encrypt_mode_dropdown_list_5g">
			                          <option value="1">AES</option>
			                          <option value="2">Auto</option>
			                          </select></td>
			                        </tr>
			                      <tr>
			                        <td colspan="2"><div id="wpa_e_security_div_5g" >
			                          <table width="100%" border="0" cellspacing="0" cellpadding="2">
			                            <tr>
			                              <td width="21%"><label id="ID_LABEL_RADIUS_SERVER_IP_5G">Radius Server IP</label></td>
			                              <td width="79%" ><input type="text" id="radius_ip_5g" title="Please enter the Radius IP." size="20" maxlength="17" /></td>
			                              </tr>
			                            <tr>
			                              <td><label id="ID_LABEL_RADIUS_SERVER_PORT_5G">Radius Port</label></td>
			                              <td><input type="text" id="radius_port_5g"  size="6" maxlength="5" /></td>
			                              </tr>
			                            <tr>
			                              <td><label id="ID_LABEL_RADIUS_SERVER_SHARE_SECRET_5G">Radius Share Secret</label></td>
			                              <td><input type="password"  id="radius_share_secret_textbox_5g" title="Please enter the share secret." size="32" maxlength="64" /></td>
			                              </tr>
			                            </table>
			                          </div>
			                          <div id="wpa_p_security_div_5g" >
			                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                              <tr>
			                                <td width="21%"><label id="ID_LABEL_WPA_PRESHARE_KEY_5G">Pre-Share Key</label></td>
			                                <td width="79%" ><input type="password" id="wpa_preshare_key_5g" title="Please preshare key." size="32" maxlength="64" /></td>
			                                </tr>
			                              </table>
			                            </div></td>
			                        </tr>
			                      </table>
			                    </div>
			                    <div id="wep_security_div_5g">
			                      <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                        <tr>
			                          <td width="21%"><label id="D_LABEL_WEP_DEFAULT_KEY_5G">Default Key</label></td>
			                          <td width="79%" ><select name="default_key_dropdown_list_5g" id="default_key_dropdown_list_5g">
			                            <option value="1">1</option>
			                            <option value="2">2</option>
			                            <option value="3">3</option>
			                            <option value="4">4</option>
			                            </select></td>
			                          </tr>
			                        <tr>
			                          <td><label id="ID_LABEL_WEP_KEY1_5G">WEP Key 1</label></td>
			                          <td><input  type="password" id="wep_key1_5g" title="Please enter the WEP Key1" size="28" maxlength="24" /></td>
			                          </tr>
			                        <tr>
			                          <td><label id="ID_LABEL_WEP_KEY2_5G">WEP Key 2</label></td>
			                          <td><input name="password" type="password" id="wep_key2_5g" title="Please enter the WEP Key3" size="28" maxlength="24" /></td>
			                          </tr>
			                        <tr>
			                          <td><label id="ID_LABEL_WEP_KEY3_5G">WEP Key 3</label></td>
			                          <td><input name="wep_key" type="password" id="wep_key3_5g" title="Please enter the WEP Key3" size="28" maxlength="24" /></td>
			                          </tr>
			                        <tr>
			                          <td><label id="ID_LABEL_WEP_KEY4_5G">WEP Key 4</label></td>
			                          <td><input name="wep_key" type="password" id="wep_key4_5g" title="Please enter the WEP Key4" size="28" maxlength="24" /></td>
			                          </tr>
			                        </table>
			                      </div></td>
			                  </tr>
			                </table></td>
		                </tr>
			            </table></td>
		            </tr>
			        <tr>
			          <td ><button id="ID_BUTTON_APPLY_SECURITY_5G">Apply</button>
                      <button id="ID_BUTTON_CANCEL_SECURITY_5G">Cancel</button></td>
		            </tr>
		          </table>
                  </div>
		        </div></td>
		      </tr>
			  </table>
			<table width="100%" border="0" cellspacing="0" cellpadding="2">
            <tr>
              <td width="25"></td>
            </tr>
            </table>


</div> <!-- hold -->

	<div id=hold-bottom-line></div>
	
</div> <!-- center -->
		<div class="zp-portal-bottom-left">
			<div class="zp-portal-bottom-right">
				<div class="zp-portal-bottom-center"></div>
			</div>
		</div>
		
	<div id=footer>
   		<div id="copyright">&copy;2021 Ubee Interactive. All rights reserved.</div>
 	</div>
 	
</div> <!-- style -->
</div> <!-- container -->
</body>

</html>
