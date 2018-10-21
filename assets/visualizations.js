//date range
var d=new Date();
var startDate=document.getElementById('startDate');
var endDate=document.getElementById('endDate');
startDate.value=d.getFullYear().toString().padStart(4,0)+'-'+(''+(d.getMonth()+1)).padStart(2,0)+'-01';
endDate.value=d.getFullYear().toString().padStart(4,0)+'-'+((d.getMonth()+1)%12+1).toString().padStart(2,0)+'-01';

var goodColors=['255,50,50','50,150,250','255,150,50','255,100,255'];
var graphs=document.getElementsByClassName('graph');
function setDropDown(show){
  for(var i=0;i<graphs.length;i++){
    graphs[i].style.visibility='hidden';
    graphs[i].style.position='fixed';
  }
  graphs[show].style.position='';
  graphs[show].style.visibility='visible';
};//manages showing only the selected graph
setDropDown(0);
var typeOfRows=[
	{
	  company:2,
	  date:17,
	  donation:[22,23],
	  type:16
	},
	{
	  company:'Company / Organization Name',
	  date:'Donated On',
	  donation:['Weight (lbs)','Value (approximate $)'],
	  type:'Source Type'
	}
];
var rows={
  company:2,
  date:17,
  donation:[22,23],
  type:16
};//rows to expect what data from the CSV/JSON
var rows={
  company:'Company / Organization Name',
  date:'Donated On',
  donation:['Weight (lbs)','Value (approximate $)'],
  type:'Source Type'
};//rows to expect what data from the CSV/JSON
var donationTypes=['lb','$'];
var donationType=0;
var goals=[
  ['goal',100000,'rgba(0,200,0,0.1)'],
  ['minimal',50000,'rgba(255,0,0,0.1)']
];
var thisMonthData={};
var dataLoader = document.getElementById('dataLoader');
dataLoader.addEventListener('change', handleData, false);

var dataLoader2 = document.getElementById('dataLoader2');
dataLoader2.addEventListener('change', handleData2, false);
var allData=[false,false];//store the data for re-calculating graphs
function sortData(a,b){
  return(Date.parse(b[rows.date])-Date.parse(a[rows.date]));
};//sorting function by date

function handleData(e){
  rows=typeOfRows[0];
  var reader=new FileReader();
  reader.onload=function(event){
    csvFile=
    csv({
      output: "csv"
    })
    .fromString(atob(event.target.result.replace('data:application/vnd.ms-excel;base64,','')))
    .then(function(result){
      makeGraph(result);
    })
  }
  reader.readAsDataURL(e.target.files[0]);
};//converts csv to json for current month
function makeGraph(data){
  allData[0]=[];
  for(var i=0;i<data.length;i++){
    allData[0].push([]);
    for(var j=0;j<data[i].length;j++){
      allData[0][i][j]=data[i][j];
    }
  }
  /*graph*/
  var donors={};
  var graphs=[];
  data.sort(sortData);
  var dateRange=
      new Date(Date.parse(data[data.length-1][rows.date])).toString().split(' ').splice(0,4).join(' ')+' - '+
      new Date(Date.parse(data[0][rows.date])).toString().split(' ').splice(0,4).join(' ');//create the string for the date range
  for(var i=0,l=data.length;i<l;i++){
    //turn the donation amount strings into floats
    data[i][rows.donation[donationType]]=parseFloat(data[i][rows.donation[donationType]]);
    
    //create donors which figures out an individual donor's contribution over the month
    if(donors.hasOwnProperty(data[i][rows.company])){
      donors[data[i][rows.company]].gave+=data[i][rows.donation[donationType]];
    }
    else{
      donors[data[i][rows.company]]={gave:data[i][rows.donation[donationType]],type:data[i][rows.type]}
    }
  }
  
  var types={};
  for(var i in donors){
    if(types.hasOwnProperty(donors[i].type)){
      types[donors[i].type].gave+=donors[i].gave;
    }
    else{
      types[donors[i].type]={gave:donors[i].gave,total:0};
    }
  }
  var n=0;
  for(var i in types){
    types[i].id=graphs.length;
    var color=goodColors[n];
    n++;
    graphs.push({
      x:[],
      y:[],
      fill: 'tozeroy',
      type: 'scatter',
      name: i+' ('+donationTypes[donationType]+')',
      fillcolor:'rgba('+color+',0.6)',
      line:{
        color:'rgb('+color+')'
      }
    });
  }
  
  for(var i=data.length-1;i>=0;i--){
      for(var thisType in types){
        if(types[thisType].id<=types[data[i][rows.type]].id){
          types[thisType].total+=data[i][rows.donation[donationType]];
        }
      }
      if(i==0||data[i-1][rows.date]!==data[i][rows.date]){
        for(var thisType in types){
          graphs[types[thisType].id].x.push(data[i][rows.date]);
          graphs[types[thisType].id].y.push(types[thisType].total);
        }
      }
  }//add graph data
  
  for(var i=0;i<goals.length;i++){
    graphs.push({
      x:[data[0][rows.date],data[data.length-1][rows.date]],
      y:[goals[i][1],goals[i][1]],
      mode:'lines',
      fill: 'tozeroy',
      name:goals[i][0],
      fillcolor:goals[i][2],
      mode:'none'
    });
  }//add goal lines
  var layout = {
    xaxis: {fixedrange: true},
    yaxis: {fixedrange: true},
    title: 'Compound Food Donations from '+dateRange,
    height:700,
  };
  Plotly.newPlot('area',graphs,layout, {responsive: true});
  /*scatter donor graph*/
  var graphs=[];
  var donorIndexes=[];
  for(var donor in donors){
    graphs.push({
      x:[],
      y:[],
      mode: 'markers',
      name: donor+' ('+donationTypes[donationType]+')',
    });
    donorIndexes.push(donor);
  }
  for(var i=data.length-1;i>=0;i--){
	if(donorIndexes.indexOf(data[i][rows.company])>=0){
		graphs[donorIndexes.indexOf(data[i][rows.company])].x.push(data[i][rows.date]);
		graphs[donorIndexes.indexOf(data[i][rows.company])].y.push(data[i][rows.donation[donationType]]);
	}
  }
  var layout = {
    //xaxis: {fixedrange: true},
    //yaxis: {fixedrange: true},
    title: 'Donator Food Donations from '+dateRange,
    height:700,
  };
  Plotly.newPlot('scatter',graphs,layout, {responsive: true});
  /*pies*/
  var thePie = [{
    values: [],
    labels: [],
    type: 'pie',
  }];
  
  var total=0;
  for(var i in donors){
    total+=donors[i].gave;
  }
  var other=0;
  for(var i in donors){
    if(donors[i].gave<total/100){
      other+=donors[i].gave;
    }
    else{
      thePie[0].values.push(donors[i].gave);
      thePie[0].labels.push(i);
      thisMonthData[i]=donors[i].gave;
    }
  }
  thePie[0].values.push(other);
  thePie[0].labels.push('other');
  thisMonthData.other=other;
  layout={
    title: 'Food Donations from '+dateRange+' by Donator ('+donationTypes[donationType]+')',
    height:700,
  };
  Plotly.newPlot('pie', thePie,layout, {responsive: true});
  /*types*/
  var thePie2 = [{
    values: [],
    labels: [],
    type: 'pie'
  }];
  
  for(var i in types){
    thePie2[0].values.push(types[i].gave);
    thePie2[0].labels.push(i);
  }
  layout={
    title: 'Food Donations from '+dateRange+' by Donator Type ('+donationTypes[donationType]+')',
    height:700,
  };
  Plotly.newPlot('Dtypes', thePie2,layout, {responsive: true});
  /*bubble map*/
  var mapData=[{
    type:'scattermapbox',
    lat:[],
    lon:[],
    mode:'markers',
    marker: {
      size:14
    },
    text:['Montreal'],
  }];
  var layout = {
    autosize: true,
    hovermode:'closest',
    height:700,
    mapbox: {
      bearing:0,
      center: {
        lat:33.4483771,
        lon:-112.07403729999999
      },
      pitch:0,
      zoom:4
    },
  }
  Plotly.setPlotConfig({
    mapboxAccessToken: 'pk.eyJ1IjoiZXRwaW5hcmQiLCJhIjoiY2luMHIzdHE0MGFxNXVubTRxczZ2YmUxaCJ9.hwWZful0U2CQxit4ItNsiQ'
  })
  Plotly.plot('map', mapData, layout, {responsive: true})
};//makes the graphs relevent to the current month only

function handleData2(e){
  rows=typeOfRows[0];
  var reader=new FileReader();
  reader.onload=function(event){
    csvFile=
    csv({
      output: "csv"
    })
    .fromString(atob(event.target.result.replace('data:application/vnd.ms-excel;base64,','')))
    .then(function(result){
      makeGraph2(result);
    })
  }
  reader.readAsDataURL(e.target.files[0]);
};//converts csv to json for last month
function makeGraph2(data){
  allData[1]=[];
  for(var i=0;i<data.length;i++){
    allData[1].push([]);
    for(var j=0;j<data[i].length;j++){
      allData[1][i][j]=data[i][j];
    }
  }
  var donors={};
  data.sort(sortData);
  for(var i=0,l=data.length;i<l;i++){
    data[i][rows.donation[donationType]]=parseFloat(data[i][rows.donation[donationType]]);
    
    if(donors.hasOwnProperty(data[i][rows.company])){
      donors[data[i][rows.company]].gave+=data[i][rows.donation[donationType]];
    }
    else{
      donors[data[i][rows.company]]={gave:data[i][rows.donation[donationType]]}
    }
  }
  var thisMonth = {
    x: [],
    y: [],
    name: 'current period ('+donationTypes[donationType]+')',
    type: 'bar'
  };
  var lastMonth = {
    x: [],
    y: [],
    name: 'last period ('+donationTypes[donationType]+')',
    type: 'bar'
  };
  
  var total=0;
  var donorNames=[];
  for(var i in donors){
    total+=donors[i].gave;
    donorNames.push([i,donors[i].gave]);
  }
  donorNames.sort((a,b)=>{return b[1]-a[1]});
  var other=0;
  for(var i=donorNames.length-1;i>=0;i--){
    var dn=donorNames[i][0];
    if(donors[dn].gave<total/100){
      other+=donors[dn].gave;
    }
    else{
      if(thisMonthData.hasOwnProperty(dn)){
        thisMonth.y.push(thisMonthData[dn]);
      }
      else{
        thisMonth.y.push(0);
      }
      thisMonth.x.push(dn);
      lastMonth.x.push(dn);
      lastMonth.y.push(donors[dn].gave);
    }
  }
  thisMonth.x.push('other');
  lastMonth.x.push('other');
  thisMonth.y.push(thisMonthData.other);
  lastMonth.y.push(other);

  var monthData = [lastMonth,thisMonth];
  var layout = {
    barmode: 'group',
    xaxis: {fixedrange: true},
    yaxis: {fixedrange: true},
    height:700,
  };
  Plotly.newPlot('monthCompare', monthData, layout, {responsive: true});
};//makes graphs using both last month and this month

function updateGraphs(Dtype){
  donationType=Dtype;
  if(allData[0]){
    makeGraph(allData[0]);
    if(allData[1]){
      makeGraph2(allData[1]);
    }
  }
};//updates graphs with selected donation type

function updateEverything(){
  //get new data based on new dates
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/data?start_date='+startDate.value+'&end_date='+endDate.value);
	xhr.onload = function(e) {
		console.log(e.target.response.replace(/NaN/g,'0'));
		if (xhr.status === 200) {
		  rows=typeOfRows[1];
		  allData[0]=JSON.parse(e.target.response.replace(/NaN/g,'0'));
		  makeGraph(allData[0]);
		  makeGraph2(allData[1]);	
		}
		else {
			alert('Request failed.  Returned status of ' + xhr.status);
		}
	};
	xhr.send();
};

startDate.addEventListener('change',updateEverything);
endDate.addEventListener('change',updateEverything);
updateEverything();