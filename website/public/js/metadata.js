var years = ['All', '1992','1996','2000','2004','2008','2012','2016']


$(document).ready(function() {
	fetch("data/politician_names.JSON")
	.then(res => res.json())
	.then(function(politicians) {
			fetch("data/metadata.JSON")
			.then(meta => meta.json())
			.then(function(metadata) {
				fetch("data/ner.JSON")
				.then(n => n.json())
				.then(function(ner) {
		
				var year_field_str = $('#year_buttons').html();

				// create radio buttons for years
				for(var i=0; i<years.length;i ++) {
					if(i%4 == 0) {
						if(i == 0) {
							year_field_str += "<p><label class='yr_bx'><input type=radio name = year value="+years[i] +" checked >"+ years[i]+"</label>";
						} else {
							year_field_str += "</p><p><label class='yr_bx'><input type=radio name = year value="+years[i] +" >"+ years[i]+"</label>";
						}
					} else {
						year_field_str += "<label class='yr_bx'><input type=radio name = year value="+years[i] +" >"+ years[i]+"</label>";
					}
				};
				year_field_str += "</p>";
				$('#year_buttons').html(year_field_str); 

				
				var politician_field_str = $('#politician_buttons').html();
				politician_field_str +="<div id='politician-box'>"
				politician_field_str += "<p><label class='pols'><input type='radio' name = 'politician' value='All' checked >All</label>";
				// create radio buttons for politicians
				for(var i=0; i<politicians.length;i ++) {
					var space_split_name = politicians[i].split(' ');
					var _name = space_split_name[0]+"_"+space_split_name[1];
					if(i == 0) {
						politician_field_str += "<label class='pols'><input type=radio name =politician value="+_name +">"+ politicians[i]+"</label>";
					}else{
						if((i+1)%4 == 0) {
							politician_field_str += "</p><p><label class='pols'><input type=radio name = politician value="+_name +" >"+ politicians[i]+"</label>";
						} else {
							politician_field_str += "<label class='pols'><input type=radio name =politician value="+_name +" >"+ politicians[i]+"</label>";
						}
					}
					
				};
				politician_field_str += "</p></div>";
				$('#politician_buttons').html(politician_field_str); 


				//if there's an onchange in parties, make all for politician. And vice versa
				$('#partyForm').change(function(){
					if($("input[name='party']:checked").val() != "All") {
						//uncheck current
						$("input[name='politician']:checked").prop("checked",false);
						//check current
						$("input[name ='politician'][value='All']").prop("checked",true);
					} 
		       
		        });


				$('#politicianForm').change(function(){
					if($("input[name='politician']:checked").val() != "All") {
						//uncheck current
						$("input[name='party']:checked").prop("checked",false);
						//check current
						$("input[name ='party'][value='All']").prop("checked",true);
					} 
		       
		        });

				var simple_info_table = $('#simple_info_table').DataTable({
			        data:metadata["metadata"]["info"],
			        columns: [
			            { data: 'Title' },
			            { data: 'Value' }
			          ],
			        paging: false,
			        searching: false,
			        ordering: false,
			        info:false
			    });

				var $dataSrc =  'all';



				var complex_info_table = $('#complex_info_table').DataTable({
					data:metadata["metadata"]['all']['info'],
			        
			        columns: [
			            { data: 'Title' },
			            { data: 'Value' }
			          ],
			        paging: false,
			        searching: false,
			        ordering: false,
			        info:false
			    });

				var top_words_table = $('#top_words_table').DataTable({
			        data:metadata["metadata"]['all']['top_words'],
			        columns: [
			            { data: 'Word' },
			            { data: 'Freq' }
			          ],
			        pageLength: 8,
			        lengthChange: false,
				    searching: false,
				    ordering: false,
				    info:false
			    });

				
			    var ner_table = $('#ner_table').DataTable({
			       	data:ner["overall"].slice(0,31),
			          columns: [
			            { data: 'Word' },
			            { data: 'Freq' }
			          ],
			        pageLength: 8,
			        lengthChange: false,
			        searching: false,
			        ordering: false,
			        info:false
			    });

			    function updateTables(selected_year,selected_party,selected_politician) {
			    	ner_data = {}
			    	new_data=metadata["metadata"]
			    	//if all
			    	if(selected_year== "All" && selected_party == "All" && selected_politician == "All") {
			    		new_data = new_data["all"]
			    		ner_data=ner["overall"].slice(0,50)

			    	//if just year
			    	} else if(selected_party == "All" && selected_politician == "All") {	
			    		new_data = new_data["years"][selected_year]
			    		ner_data = ner["year"][selected_year].slice(0,50)
			    	
					//if politician
			    	} else if (selected_party == "All") {
			    		new_data = new_data["politicians"][selected_politician][selected_year]
			    		if(selected_year== "All") {
							ner_data = ner["politician"][selected_politician].slice(0,50)
			    		} else{
			    			var search_yr_pl = selected_year+","+selected_politician
			    			if(ner["year, politican"][search_yr_pl]) {
			    				ner_data = ner["year, politican"][search_yr_pl].slice(0,50)
			    			} else{
			    				ner_data = {}
			    			}
			    			
			    		}
			    		
			    	//if party
			    	} else {
			    		new_data = new_data["parties"][selected_party][selected_year]
			    		if(selected_year== "All") {
							ner_data = ner["party"][selected_party].slice(0,50)
			    		} else{
			    			var search_yr_prty = selected_year+","+selected_party
			    			if(ner["year,party"][search_yr_prty]) {
			    				ner_data = ner["year,party"][search_yr_prty].slice(0,50)
			    			} else{
			    				ner_data = {}
			    			}
			    			
			    		}


			    	};
			    	top_words_table.clear().rows.add(new_data["top_words"]).draw();
			    	complex_info_table.clear().rows.add(new_data["info"]).draw();
			    	ner_table.clear().rows.add(ner_data).draw();

		        };

		        $('#search').click(function(){
		        	var selected_year = $("input[name='year']:checked").val();
		        	var selected_party = $("input[name='party']:checked").val();
		        	var selected_politician = $("input[name='politician']:checked").val();
		        	if (selected_politician != "All") {
		        		var _politician=$("input[name='politician']:checked").val().split("_");
		        		selected_politician = _politician[0]+" "+_politician[1];
		        	}
		        	updateTables(selected_year,selected_party,selected_politician);
		        });
		    });
		});
	});
});