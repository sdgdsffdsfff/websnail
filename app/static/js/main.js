function StringBuffer() {
	this.__strings__ = new Array();
}

StringBuffer.prototype.append = function (str) {
this.__strings__.push(str);
return this;    //方便链式操作
}

StringBuffer.prototype.toString = function () {
	return this.__strings__.join("");
}


function setCookie(name,value,time){
	var strsec = getsec(time);
	var exp = new Date();
	exp.setTime(exp.getTime() + strsec*1);
	document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
}

function getsec(str){
	var str1=str.substring(1,str.length)*1; 
	var str2=str.substring(0,1); 

	if (str2 == 's'){
		return str1*1000;
	}else if (str2 == 'h') {
		return str1*60*60*1000;
	}else if (str2 == 'd'){
		return str1*24*60*60*1000;
	}
}

function getCookie(name) {
	var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
	if(arr=document.cookie.match(reg)) return unescape(arr[2]);
	else return null;
}


function getRunningStatus() {
	var intervarid = window.setInterval(function() {
		var text = "进程启动中..."
		var progressdiv = document.getElementById("progressdiv");
		var progressbar = document.getElementById('progressbar');
		var runningresult = document.getElementById('runningresult');
		$.get('/getStatus',function(data) {
			if(data == "none") {
				var runhistory = getCookie("runhistory");
				if(runhistory){
					location.reload(true);
				}else{
					window.clearInterval(intervarid);
					console.log("no running job");
				}
			} else if(data == 'pause') {
				var runhistory = getCookie('runhistory');
				if(runhistory) {
					location.reload();
				}else {
					console.log('pause');
				}
			} else {
				setCookie("runhistory","yes","s7");
				var progress = JSON.parse(data);
				progressdiv.style.display = "";
				if(progress.hasOwnProperty('Time')) {
					text = "已运行时间(s)：{0}<br>平均响应时间(s)：{1}<br>吞吐量：{2}<br>错误数：{3}<br>线程数：{4}<br>".format(progress.Time,progress.average,progress.throught,progress.errors,progress.threads);
				} else {
					text = "总请求数：{0}<br>平均响应时间(s)：{1}<br>吞吐量：{2}<br>错误数：{3}<br>线程数：{4}<br>".format(progress.TotalRequest,progress.average,progress.throught,progress.errors,progress.threads);
				}
				if(progress.status == -1) {
					runningresult.innerHTML = progress.errorinfo;
					progressbar.style.display = "none";
					console.log(progress.errorinfo);
					window.clearInterval(intervarid);
				}else {
					if(progress.status != 1) {
						console.log(progress.progress);
						progressbar.style.width = progress.progress + "%";
						progressbar.innerHTML="已完成："+progress.progress+"%";
					} else {
						progressbar.style.width = "100%";
						progressbar.innerHTML="已完成：100%";
						console.log("job done.");
						window.clearInterval(intervarid);
						//location.reload();	
						location.reload(true);
					};
					runningresult.innerHTML = text;	
				}
			}
		});
	},3000);
}

String.prototype.format = function() {
	var args = arguments;
	return this.replace(/\{(\d+)\}/g,function(s,i){
		return args[i];
	});
}

function getdownloadstatus(id) {
	var content = document.getElementById("downstatus")
	$.get('/getdownloadstatus/'+id,function(data){
		var rep = JSON.parse(data);
		var existsStr = "";
		var failedStr = "";
		for(var i=0;i<rep.exists.length;i++) {
			existsStr = existsStr + rep.exists[i] + "<br>";
		}
		for(var i=0;i<rep.failed.length;i++) {
			failedStr = failedStr + rep.failed[i] + "<br>";
		}
		//alert(existsStr+failedStr+"\r\n");	
		var finalStr = "状态：<font color='red'>{0}</font>&nbsp&nbsp图片数量：{1}<br><br>失败url：({2})<br>{3}<br>已存在url：{4}<br>{5}".format(rep.status,rep.total_count,rep.failed_count,failedStr,rep.exists_count,existsStr);
		content.innerHTML = finalStr;
	});
}





