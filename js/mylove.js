(function($){
	$.fn.action=function(opts){
		//alert(123);
		//获取整个屏幕的宽度和高度
		var height_win=$(window).height();
		var width=$(window).width();
		//alert(width);
		var settings=$.extend({
			
		},opts||{});
		var back_img=settings.actionImg;
		for(var i=0;i<3;i++){
			var div=$("<div width='50' height='100'></div>");
			var y=(i*height_win)/3+200;
			for(var j=0;j<3;j++){
				var x=(j*width)/3+200;
				var img=$("<img class='img_back' src='"+back_img+"' width='50' height='100'/>");
				
				setInterval(function(){ $(".img_back").fadeOut(200).fadeIn(200);},6000);
				img.css({position: "absolute",'top':y,'left':x,'z-index':2}); 
				
				div.append(img).appendTo($(this));
				if(j==0||j==2){
					if(j==0){
						
						img.animate({left:(width/3+200) },3000,function(){
							$(this).animate({left:(10)},3000);
							
						});
						
					}else{						
						img.animate({left:width/3+200}, 3000,function(){
							$(this).animate({left:(10)},3000);
						});
					}
					
					
				}
			}

		}
		
	};
	
	
	
	
})(jQuery)