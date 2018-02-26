 var mycontext1, mycontext2,mycontext3,mycontext4,mycontext5,mycontext6,mycontext7,mycontext8,mycontext9;
 var x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6, y6,x7,y7,x8,y8,x9,y9;
 var dataY1,dataY2,dataY3,dataY4,dataY5,dataY6,dataY7,dataY8,dataY9;
 var width,height_win;
 //定义十张不同的雪景背景
  // 创建绘图对象,并且画出来   
 var img1,img2,img3,img4,img5,img6 ,img7 ,img8,img9;
$(function(){
	height_win=document.body.clientHeight;
	width=window.screen.width;
	var mycanvas=document.getElementById("can1");
	mycanvas.width=width;
	mycanvas.height=height_win;
   
	 mycontext1=mycanvas.getContext('2d');
	  mycontext2=mycanvas.getContext('2d');
	    mycontext3=mycanvas.getContext('2d');
	   mycontext4=mycanvas.getContext('2d');
	    mycontext5=mycanvas.getContext('2d');
	     mycontext6=mycanvas.getContext('2d');
	     mycontext7=mycanvas.getContext('2d');
	     mycontext8=mycanvas.getContext('2d');
	     mycontext9=mycanvas.getContext('2d');
    // 设置图像位置初始位置的变量 
     x1 = getPosition_x();
     y1 = getPosition_y();
    x2 = getPosition_x();
     y2 = getPosition_y();
     x3 = getPosition_x();
     y3 = getPosition_y();
     x4 = getPosition_x();
     y4 = getPosition_y();
     x5 = getPosition_x();
     y5 = getPosition_y();
     x6 = getPosition_x();
     y6 = getPosition_y();
     x7 = getPosition_x();
     y7 = getPosition_y();
     x8 = getPosition_x();
     y8 = getPosition_y();
     x9 = getPosition_x();
     y9 = getPosition_y();
     dataY1=getDataY();
     dataY2=getDataY();
     dataY3=getDataY();
     dataY4=getDataY();
     dataY5=getDataY();
     dataY6=getDataY();
     dataY7=getDataY();
     dataY8=getDataY();
     dataY9=getDataY();
    //定义十张不同的雪景背景
     // 创建绘图对象,并且画出来   
     img1 = new Image();
     img2 = new Image();
     img3 = new Image();
     img4 = new Image();
     img5 = new Image();
     img6 = new Image();
     img7 = new Image();
     img8 = new Image();
     img9 = new Image();
    
    img1.src=getXueColor();
    img2.src=getXueColor();
    img3.src=getXueColor();
    img4.src=getXueColor();
    img5.src=getXueColor();
    img6.src=getXueColor();
    img7.src=getXueColor();
    img8.src=getXueColor();
    img9.src=getXueColor();
    draw();
    window.setInterval(draw, 100);
});

function draw() {
	
	console.log("draw......");
	mycontext1.clearRect(0, 0, width, height_win);
     y1 += dataY1;
     y2 += dataY2;
     y3 += dataY3;
     y4 += dataY4;
     y5 += dataY5;
     y6 += dataY6;
     y7 += dataY7;
     y8 += dataY8;
     y9 += dataY9;
     //当雪景的
     if(y1>=height_win+50){
    	 x1 = getPosition_x();
    	 y1 = getPosition_y();
    	 dataY1=getDataY();
    	 img1.src=getXueColor();
     }
     if(y2>=height_win+50){
    	 x2 = getPosition_x();
    	 y2 = getPosition_y();
    	 dataY2=getDataY();
    	 img2.src=getXueColor();
     }
     if(y3>=height_win+50){
    	 x3 = getPosition_x();
    	 y3 = getPosition_y();
    	 dataY3=getDataY();
    	 img3.src=getXueColor();
     }
     if(y4>=height_win+50){
    	 x4 = getPosition_x();
    	 y4 = getPosition_y();
    	 dataY4=getDataY();
    	 img4.src=getXueColor();
     }
     if(y5>=height_win+50){
    	 x5 = getPosition_x();
    	 y5 = getPosition_y();
    	 dataY5=getDataY();
    	 img5.src=getXueColor();
     }
     if(y6>=height_win+50){
    	 x6 = getPosition_x();
    	 y6 = getPosition_y();
    	 dataY6=getDataY();
    	 img6.src=getXueColor();
     }
     if(y7>=height_win+50){
    	 x7 = getPosition_x();
    	 y7 = getPosition_y();
    	 dataY7=getDataY();
    	 img7.src=getXueColor();
     }
     if(y8>=height_win+50){
    	 x8 = getPosition_x();
    	 y8 = getPosition_y();
    	 dataY8=getDataY();
    	 img8.src=getXueColor();
     }
     if(y9>=height_win+50){
    	 x9 = getPosition_x();
    	 y9 = getPosition_y();
    	 dataY9=getDataY();
    	 img9.src=getXueColor();
     }
     mycontext1.drawImage(img1, x1, y1, 50, 50);
     mycontext2.drawImage(img2, x2, y2, 50, 50);
     mycontext3.drawImage(img3, x3, y3, 50, 50);
     mycontext4.drawImage(img4, x4, y4, 50, 50);
     mycontext5.drawImage(img5, x5, y5, 50, 50);
     mycontext6.drawImage(img6, x6, y6, 50, 50);
     mycontext7.drawImage(img7, x7, y7, 50, 50);
     mycontext8.drawImage(img8, x8, y8, 50, 50);
     mycontext9.drawImage(img9, x9, y9, 50, 50);
}

/**
 * 得到雪景的初始x的位置
 */
function getPosition_x(){
	//return Math.round(Math.random()*width);
	var max=Math.round(Math.random()*width);
	if(max>=width-50){
		max=width-50;
	}
	return max;
}
/**
 * 得到雪景的初始y的位置
 */
function getPosition_y(){
	return Math.round(Math.random()*(-50))-1;
}
/**
 * 得到一个雪景背景的随机数1-10
 * 这个是让有一个增加个数的设置
 */
function getXueCount(){
	return Math.round(Math.random()*10)+1;
}
/**
 * 产生一个4到11的随机数
 */
function getDataY(){
	return Math.round(Math.random()*8)+4;
}
/**
 * 得到一个是哪一个雪景图片
 * 1-9
 */
function getXueColor(){
	var where=Math.round(Math.random()*9)+1;
	//alert(where);
	var s;
	switch (where) {
	case 1:
		s="image/xue1.png";
		break;
	case 2:
		s="image/xue2.png";
		break;
	case 3:
		s="image/xue3.png";
		break;
	case 4:
		s="image/xue4.png";
		break;
	case 5:
		s="image/xue5.png";
		break;
	case 6:
		s="image/xue6.png";
		break;
	case 7:
		s="image/xue7.png";
		break;
	case 8:
		s="image/xue8.png";
		break;
	case 9:
		s="image/xue9.png";
		break;

	default:
		break;
	}
	return s;
}

