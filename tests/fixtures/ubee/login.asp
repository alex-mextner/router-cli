<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
<link rel="stylesheet" type="text/css" href="main.css" />
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
<title>Residential Gateway Login</title>

  <script>
  	function showTooltip(e,n) {
  		var scrollT = document.body.scrollTop;
			var x = e.clientX;
			var y = e.clientY;
			document.getElementById('tooltipcontent').innerHTML = document.getElementById('tt'+n).innerHTML;
			document.getElementById('tooltip').style.left = (x+10)+'px';
			document.getElementById('tooltip').style.top = ((y-20)+scrollT)+'px';
		}
		
		function hideTooltip() {
			var t = 	document.getElementById('tooltip');
			t.style.left = '-1000px';
			t.style.top = '-1000px';
		}
  </script>
  
</head>

<body>

  	<div class="zp-portalContainer">
  		<div class="zp-portalContainer-Style">
	  		<div id="zp-header">
	  			<img src="sm_generic_modemrouter_header.gif" BORDER=0 />
	  		</div>
	  		<div class="zp-portal-top-left">
					<div class="zp-portal-top-right">
						<div class="zp-portal-top-center"></div>
					</div>
				</div>
				<div class="zp-portal-center">
				  <div class="zp-contentholder">
				  					
						
								
								<h2 id="ID_H2_LOGIN_TITLE">Log in</h2>
								<form action=/goform/login method=POST name="login">
								<table class="inlogmodule" cellpadding="0" cellspacing="0" border="0">
									<tr>
										<td class="celltopleft" height="5" >
										</td>
										
										<td class="celltopright">
										</td>
									</tr>
									<tr>
										<td class="cell1">
											&#160;
										</td>
										
										<td class="cell2">
											<p style="width:220px">
												<label id="ID_LABEL_LOGIN_DESC">Please enter the username and password to login.</label></p>
										</td>
									</tr>
									<tr>
										<td class="cell1"><label id="ID_LABEL_LOGIN_USERNAME">Username</label></td>
										
										<td class="cell2">
											<input type="text" name="loginUsername" value="" class="invoer"/>
										</td>
									</tr>
									<tr>
										<td class="cell1">
											<span class="txt">
												<label id="ID_LABEL_LOGIN_PASSWORD">Password</label>
											</span>
										</td>
										
										<td class="cell2">
											<input type="password" name="loginPassword" value="" class="invoer"/>
										</td>
									</tr>
									<tr>
										<td class="cell1">
											
											
										</td>
										
										<td class="cell2">
											<!--<div class="zp-button">--><input type="submit" value="Login" id="ID_BUTTON_LOGIN"><!--</div>-->
										</td>
									</tr>
									
									<tr>
										<td class="cellbottomleft" height="5" ><div style="height:5px;width:100%;overflow:hidden;"/>
										</td>
										
										<td class="cellbottomright">
										</td>
									</tr>
								</table>
								</form>
							
						</div>
				</div>
				<div class="zp-portal-bottom-left">
					<div class="zp-portal-bottom-right">
						<div class="zp-portal-bottom-center"></div>
					</div>
				</div>
			</div>
			<div style="height:25px;width:100%;"/>
		</div>

</body>

</html>