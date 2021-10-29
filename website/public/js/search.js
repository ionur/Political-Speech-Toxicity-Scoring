var Chart = require('chart.js');
var newIdentity = false
var years = ['1992', '1996','2000','2004','2008','2012','2016'];

function updateIdentityData(identity,freqs,similarity,lineChart,wordcloud,words_table,identity_table) {
	$('#searched_word').html(identity.charAt(0).toUpperCase() + identity.slice(1));

	//update chart
	json_data = getChartData(freqs, identity)
	lineChart.data.datasets[0].data = json_data.all;
	lineChart.data.datasets[1].data = json_data.dem;
	lineChart.data.datasets[2].data = json_data.rep;
	lineChart.update();

	//update wordcloud
	var wordcloud_data = similarity[identity]["overall"]["speeches_clean"]["freq"]["top_20_all"];
	wordcloud.series[0].update({ data: wordcloud_data}, true);

	//reset selectors
	newIdentity = true
	$("option[name='typ']:selected").prop("selected",false);
	$("input[name ='typ'][value='top_20_all']").prop("selected",true);
	$("option[name='yr']:selected").prop("selected",false);
	$("input[name ='yr'][value='overall']").prop("selected",true);
	$("option[name='mtd']:selected").prop("selected",false);
	$("input[name ='mtd'][value='freq]").prop("selected",true);
	$("option[name='prty']:selected").prop("selected",false);
	$("input[name ='prty'][value='both']").prop("selected",true);

	newIdentity = false
	words_table.clear().rows.add(similarity[identity]["overall"]["speeches_clean"]["freq"]["top_20_all"]).draw();
	identity_table.clear().rows.add(similarity[identity]["overall"]["speeches_clean"]["freq"]["top_10_similar"]).draw(); 
}

function getChartData(data, word) {
	var all= [];
	var dem = [];
	var rep =[];
	for(var i=0; i<years.length; i++) {
		all.push(data[years[i]]["All"][word]);
		dem.push(data[years[i]]["Democrat"][word]);
		rep.push(data[years[i]]["Republican"][word]);
		
	}
	return {all: all, dem: dem, rep:rep}
}

function wordcloudData(data) {
	sm = [];
	for(var i=0; i<data.length; i++) {
		sm.push({"name":data[i]["name"], "weight":data[i]["value"]})
	}
	return sm
}



$(document).ready(function() {
	fetch("data/seeds.JSON")
	.then(seed => seed.json())
	.then(function(identities) {
		var defaultIdentity = "american";

		fetch("data/freqs.JSON")
		.then(fr => fr.json())
		.then(function(freqs) {
			fetch("data/similarity_data.JSON")
			.then(sim => sim.json())
			.then(function(similarity) {
				default_chart_data = getChartData(freqs, defaultIdentity);
				console.log(similarity)
		    	var ctx = document.getElementById('lineChart').getContext('2d');
				var lineChart = new Chart(ctx, {
					  type: 'line',
					  options: {
					  	maintainAspectRatio: false,
					  	legend:{
					  		fullWidth:false
					  	},
				        scales: {
				            yAxes: [{
				                ticks: {
				                    beginAtZero: true,
				                }
				            }]
				        }
				      },
					  data: {
					    labels: years,
					    datasets: [{
					      label: 'Overall',
					      data: default_chart_data.all,
					      backgroundColor: "rgb(123,157,111)",
					      borderColor: "rgb(123,157,111)",
					      fill: false
					    }, {
					      label: 'Democrats',
					      data: default_chart_data.dem,
					      backgroundColor: "rgb(0,0,255)",
					      borderColor: "rgb(0,0,255)",
					      fill: false
					    },{
					      label: 'Republicans',
					      data: default_chart_data.rep,
					      backgroundColor: "rgb(255,0,0)",
					      borderColor: "rgb(255,0,0)",
					      fill: false
					    }]
					  }
				});
				var archimedeanSpiral = function archimedeanSpiral(t) {
				    t *= 0.1;
				    return {
				        x: t * Math.cos(t),
				        y: t * Math.sin(t)
				    };
				};
				var randomPlacement = function randomPlacement(point, options) {
				  var field = options.field,
				    r = options.rotation;
				  return {
				    x: getRandomPosition(field.width) - (field.width / 2),
				    y: getRandomPosition(field.height) - (field.height / 2),
				   rotation: getRotation(r.orientations, r.from, r.to)
				  };
				};
				// Include this snippet after loading Highcharts and before Highcharts.chart is executed.
				Highcharts.seriesTypes.wordcloud.prototype.deriveFontSize = function (relativeWeight) {
				   var maxFontSize = 25;
				  // Will return a fontSize between 0px and 25px.
				  return Math.floor(maxFontSize * relativeWeight);
				};
				Highcharts.seriesTypes.wordcloud.prototype.placementStrategy.random= randomPlacement;
				Highcharts.seriesTypes.wordcloud.prototype.spirals.archimedean = archimedeanSpiral;
				default_wordcloud_data = similarity[defaultIdentity]["overall"]["speeches_clean"]["freq"]["top_20_all"];
				var wordcloud = Highcharts.chart('wordCloud', {
					chart: {
		      			backgroundColor: '#f8f8f8'
					},
				    series: [{
				        type: 'wordcloud',
				        data: default_wordcloud_data,
				        name: 'Occurrences',
				        spiral: 'archimedean'
				    }],
				    title: {
				        text: ''
				    },
				    credits: {
				    	enabled: false
				    }
				});
				

				var $year = "overall";
				var $party = "speeches_clean";
				var $method = "freq";
				var $type = "top_20_all";



				default_similarity_data = similarity[defaultIdentity][$year][$party][$method]["top_10_similar"];
				default_words_data = similarity[defaultIdentity][$year][$party][$method][$type];
				

				var words_table = $('#words_table').DataTable({
			    	data:default_words_data,
			        columns: [
			           { data: 'name' },
			           { data: 'weight' }
			        ],
			        pageLength: 5,
			        lengthChange: false,
				    searching: false,
				    ordering: false,
				    info:false
			    });

				var identity_table = $('#identity_table').DataTable({
					data:default_similarity_data,
			        columns: [
			            { data: 'name' },
				        { data: 'weight' }
			        ],
			        pageLength: 5,
			        lengthChange: false,
				    searching: false,
				    ordering: false,
				    info:false
			    });



				$('#autocomplete').autocomplete({
				    lookup: identities,
				    lookupLimit:8,
				    onSelect: function (suggestion) {
				        $('#autocomplete').autocomplete().clear();
				        defaultIdentity = suggestion.value;
				        updateIdentityData(suggestion.value,freqs,similarity,lineChart,wordcloud,words_table,identity_table);
				        $('#autocomplete').val("");
				    }
				});

				$('#type_selector').change(function(){
					if(!newIdentity) {
						$type= $("#type_selector :selected").val();
						console.log(defaultIdentity)
						console.log($year,' ',$party,' ',$method,' ',$type)
						new_data = similarity[defaultIdentity][$year][$party][$method][$type];
						if(new_data) {
							words_table.clear().rows.add(new_data).draw();
						}else{
							words_table.clear();
						}					
						//words_table.ajax.reload(null, false);
					}
					
				});

				$('#method_selector').change(function(){
					if(!newIdentity) {
						$method= $("#method_selector :selected").val();
						console.log(defaultIdentity)
						console.log($year,' ',$party,' ',$method,' ',$type)
						new_data = similarity[defaultIdentity][$year][$party][$method][$type];
						if($method=="ppmi") {
							$("#type_selector").prop('disabled', true);
						}else{
							$("#type_selector").prop('disabled', false);
						}
						if(new_data) {
							words_table.clear().rows.add(new_data).draw();
						}else{
							words_table.clear();
						}
					}
				});


				$('#year_selector').change(function(){
					if(!newIdentity) {
						$year_selector = $("#year_selector :selected").val();
						$party_selector = $("#party_selector :selected").val();

						if($year_selector == "overall" && $party_selector =="both") {
							$year = "overall";
							$party = "speeches_clean";
						}else if($year_selector == "overall") {
							$year = "per_party";
							$party = $party_selector;

						}else if($party_selector =="both") {
							$year = "per_year";
							$party = $year_selector;
						}else if($party_selector =="democrats") {
							$year = "combined";
							$party = $year_selector+"_Democrat";
						}else{
							$year = "combined";
							$party = $year_selector+"_Republican";
						}  
						console.log(defaultIdentity)
						console.log($year,' ',$party,' ',$method,' ',$type)
						
						if(similarity[defaultIdentity][$year][$party]) {
							words_table.clear().rows.add(similarity[defaultIdentity][$year][$party][$method][$type]).draw();
						}else{
							words_table.clear().draw();
						}
					}
				});

				$('#party_selector').change(function(){
					if(!newIdentity) {
						$year_selector = $("#year_selector :selected").val();
						$party_selector = $("#party_selector :selected").val();
						if($year_selector == "overall" && $party_selector =="both") {
							$year = "overall";
							$party = "speeches_clean";
						}else if($year_selector == "overall") {
							$year = "per_party";
							$party = $party_selector;

						}else if($party_selector =="both") {
							$year = "per_year";
							$party = $year_selector;
						}else if($party_selector =="democrats") {
							$year = "combined";
							$party = $year_selector+"_Democrat";
						}else{
							$year = "combined";
							$party = $year_selector+"_Republican";
						}  
						console.log(similarity[defaultIdentity])
						console.log(defaultIdentity)
						console.log($year,' ',$party,' ',$method,' ',$type)

						if(similarity[defaultIdentity][$year][$party]) {
							words_table.clear().rows.add(similarity[defaultIdentity][$year][$party][$method][$type]).draw();
						}else{
							console.log('here')
							words_table.clear().draw();
						}
						
					}
				});


				//this is for the identity similarity selector
				var $year2 = "overall";
				var $party2 = "speeches_clean";
				var $method2 = "freq"
				var $type2 ="top_10_similar"
				
				$('#year_selector_2').change(function(){
					if(!newIdentity) {
						$year_selector2 = $("#year_selector_2 :selected").val();
						$party_selector2 = $("#party_selector_2 :selected").val();

						if($year_selector2 == "overall" && $party_selector2 =="both") {
							$year2 = "overall";
							$party2 = "speeches_clean";
						}else if($year_selector2 == "overall") {
							$year2 = "per_party";
							$party2 = $party_selector2;

						}else if($party_selector2 =="both") {
							$year2 = "per_year";
							$party2 = $year_selector2;
						}else if($party_selector2 =="democrats") {
							$year2 = "combined";
							$party2 = $year_selector2+"_Democrat";
						}else{
							$year2 = "combined";
							$party2 = $year_selector2+"_Republican";
						}  
						console.log(defaultIdentity)
						console.log($year2,' ',$party2,' ',$method2,' ',$type2)
						if(similarity[defaultIdentity][$year2][$party2]) {
							identity_table.clear().rows.add(similarity[defaultIdentity][$year2][$party2][$method2][$type2]).draw();
						}else{
							identity_table.clear().draw();
						}
					}
				});

				$('#party_selector_2').change(function(){
					if(!newIdentity) {
						$year_selector2 = $("#year_selector_2 :selected").val();
						$party_selector2 = $("#party_selector_2 :selected").val();

						if($year_selector2 == "overall" && $party_selector2 =="both") {
							$year2 = "overall";
							$party2 = "speeches_clean";
						}else if($year_selector2 == "overall") {
							$year2 = "per_party";
							$party2 = $party_selector2;

						}else if($party_selector2 =="both") {
							$year2 = "per_year";
							$party2 = $year_selector2;
						}else if($party_selector2 =="democrats") {
							$year2 = "combined";
							$party2 = $year_selector2+"_Democrat";
						}else{
							$year2 = "combined";
							$party2 = $year_selector2+"_Republican";
						}  
						console.log(defaultIdentity)
						console.log($year2,' ',$party2,' ',$method2,' ',$type2)
						if(similarity[defaultIdentity][$year2][$party2]) {
							identity_table.clear().rows.add(similarity[defaultIdentity][$year2][$party2][$method2][$type2]).draw();
						}else{
							identity_table.clear().draw();
						}
						
					}
				});



			});

		});
	});
});





