// var data=[["employer"],["patient"],["family"],["presidential"]];
var defaultYear = "1992";
$(document).ready(function() {
	fetch("data/us_them.JSON")
	.then(res => res.json())
	.then(function(groups) {
		//initialize the timeline
		var timelines = $('.cd-horizontal-timeline'),
    		eventsMinDistance = 120;

  		(timelines.length > 0) && initTimeline(timelines);


  		//this part is for data tables

		data = groups[defaultYear];

		var dem_us = $('#dem-us').DataTable({
	    data: data["Democrat"]["us"],
        columns: [
            { title: "Us" }
        ],
        pageLength: 5,
        lengthChange: false,
	    searching: false,
	    ordering: false,
	    info:false
		});
		var dem_them = $('#dem-them').DataTable({
		    data: data["Democrat"]["not us"],
	        columns: [
	            { title: "Them" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});
		var dem_american = $('#dem-american').DataTable({
		    data: data["Democrat"]["american"],
	        columns: [
	            { title: "American" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});
		var dem_non_american = $('#dem-non-american').DataTable({
		    data: data["Democrat"]["not american"],
	        columns: [
	            { title: "Non-American" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});

			var rep_us = $('#rep-us').DataTable({
		    data: data["Republican"]["us"],
	        columns: [
	            { title: "Us" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});
		var rep_them = $('#rep-them').DataTable({
		    data: data["Republican"]["not us"],
	        columns: [
	            { title: "Them" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});
		var rep_american = $('#rep-american').DataTable({
		    data: data["Republican"]["american"],
	        columns: [
	            { title: "American" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});
		var rep_non_american = $('#rep-non-american').DataTable({
		    data: data["Republican"]["not american"],
	        columns: [
	            { title: "Non-American" }
	        ],
	        pageLength: 5,
	        lengthChange: false,
	        lengthChange: false,
		    searching: false,
		    ordering: false,
		    info:false
		});


		///this part is for the timeline



		function initTimeline(timelines) {
		    timelines.each(function(){
		      var timeline = $(this),
		        timelineComponents = {};
		      //cache timeline components 
		      timelineComponents['timelineWrapper'] = timeline.find('.events-wrapper');
		      timelineComponents['eventsWrapper'] = timelineComponents['timelineWrapper'].children('.events');
		      timelineComponents['fillingLine'] = timelineComponents['eventsWrapper'].children('.filling-line');
		      timelineComponents['timelineEvents'] = timelineComponents['eventsWrapper'].find('a');
		      timelineComponents['timelineDates'] = parseDate(timelineComponents['timelineEvents']);
		      timelineComponents['eventsMinLapse'] = minLapse(timelineComponents['timelineDates']);
		      timelineComponents['timelineNavigation'] = timeline.find('.cd-timeline-navigation');
		      timelineComponents['eventsContent'] = timeline.find('.events-content');
		      //assign a left postion to the single events along the timeline
		      setDatePosition(timelineComponents, eventsMinDistance);
		      //assign a width to the timeline
		      var timelineTotWidth = setTimelineWidth(timelineComponents, eventsMinDistance);
		      //the timeline has been initialize - show it
		      timeline.addClass('loaded');
		      
		      //detect click on the a single event - show new event content
		      timelineComponents['eventsWrapper'].on('click', 'a', function(event){
		        event.preventDefault();
		        timelineComponents['timelineEvents'].removeClass('selected');
		        $(this).addClass('selected');
		        //updateOlderEvents($(this));
		        updateFilling($(this), timelineComponents['fillingLine'], timelineTotWidth);
		        //change tables
		        updateVisibleContent($(this));
		      });
		    });
		 }

		function updateVisibleContent(event) {
		    var eventDate = event.data('date').split('/')[2];
		    //update data
			data = groups[eventDate];

		    //update all the tables
		    dem_us.clear().rows.add(data["Democrat"]["us"]).draw();
			dem_them.clear().rows.add(data["Democrat"]["not us"]).draw(); 
			dem_american.clear().rows.add(data["Democrat"]["american"]).draw();
			dem_non_american.clear().rows.add(data["Democrat"]["not american"]).draw(); 
			rep_us.clear().rows.add(data["Republican"]["us"]).draw();
			rep_them.clear().rows.add(data["Republican"]["not us"]).draw(); 
			rep_american.clear().rows.add(data["Republican"]["american"]).draw();
			rep_non_american.clear().rows.add(data["Republican"]["not american"]).draw(); 
		}





		function setDatePosition(timelineComponents, min) {
    		for (i = 0; i < timelineComponents['timelineDates'].length; i++) { 
        		var distance = daydiff(timelineComponents['timelineDates'][0], timelineComponents['timelineDates'][i]),
          		distanceNorm = Math.round(distance/timelineComponents['eventsMinLapse'])+1;
        		timelineComponents['timelineEvents'].eq(i).css('left', distanceNorm*min+'px');
    		}
  		}


  		function daydiff(first, second) {
      		return Math.round((second-first));
  		}

  		function minLapse(dates) {
    		//determine the minimum distance among events
    		var dateDistances = [];
    		for (i = 1; i < dates.length; i++) { 
       			var distance = daydiff(dates[i-1], dates[i]);
        		dateDistances.push(distance);
    		}
    		return Math.min.apply(null, dateDistances);
  		}

  		//based on http://stackoverflow.com/questions/542938/how-do-i-get-the-number-of-days-between-two-dates-in-javascript
  		function parseDate(events) {
		    var dateArrays = [];
		    events.each(function(){
		      var singleDate = $(this),
		        dateComp = singleDate.data('date').split('T');
		      if( dateComp.length > 1 ) { //both DD/MM/YEAR and time are provided
		        var dayComp = dateComp[0].split('/'),
		          timeComp = dateComp[1].split(':');
		      } else if( dateComp[0].indexOf(':') >=0 ) { //only time is provide
		        var dayComp = ["2000", "0", "0"],
		          timeComp = dateComp[0].split(':');
		      } else { //only DD/MM/YEAR
		        var dayComp = dateComp[0].split('/'),
		          timeComp = ["0", "0"];
		      }
		      var newDate = new Date(dayComp[2], dayComp[1]-1, dayComp[0], timeComp[0], timeComp[1]);
		      dateArrays.push(newDate);
		    });
		    return dateArrays;
		}

  		function setTimelineWidth(timelineComponents, width) {
    		var timeSpan = daydiff(timelineComponents['timelineDates'][0], timelineComponents['timelineDates'][timelineComponents['timelineDates'].length-1]),
      			timeSpanNorm = timeSpan/timelineComponents['eventsMinLapse'],
      			timeSpanNorm = Math.round(timeSpanNorm) + 10,
      			totalWidth = timeSpanNorm*width;
      			totalWidth = 1000;
    		timelineComponents['eventsWrapper'].css('width', totalWidth+'px');
    		updateFilling(timelineComponents['eventsWrapper'].find('a.selected'), timelineComponents['fillingLine'], totalWidth);
    		updateTimelinePosition('next', timelineComponents['eventsWrapper'].find('a.selected'), timelineComponents);
  
    		return totalWidth;
  		}

  		function updateFilling(selectedEvent, filling, totWidth) {
    		//change .filling-line length according to the selected event
    		var eventStyle = window.getComputedStyle(selectedEvent.get(0), null),
			    eventLeft = eventStyle.getPropertyValue("left"),
			    eventWidth = eventStyle.getPropertyValue("width");
   				eventLeft = Number(eventLeft.replace('px', '')) + Number(eventWidth.replace('px', ''))/2;
    		var scaleValue = eventLeft/totWidth;
    		setTransformValue(filling.get(0), 'scaleX', scaleValue);
  		}

  		function updateTimelinePosition(string, event, timelineComponents) {
    		//translate timeline to the left/right according to the position of the selected event
    		var eventStyle = window.getComputedStyle(event.get(0), null),
      			eventLeft = Number(eventStyle.getPropertyValue("left").replace('px', '')),
      			timelineWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', '')),
      			timelineTotWidth = Number(timelineComponents['eventsWrapper'].css('width').replace('px', ''));
   			var timelineTranslate = getTranslateValue(timelineComponents['eventsWrapper']);

        	if( (string == 'next' && eventLeft > timelineWidth - timelineTranslate) || (string == 'prev' && eventLeft < - timelineTranslate) ) {
          		translateTimeline(timelineComponents, - eventLeft + timelineWidth/2, timelineWidth - timelineTotWidth);
        	}
  		}

		function translateTimeline(timelineComponents, value, totWidth) {
		    var eventsWrapper = timelineComponents['eventsWrapper'].get(0);
		    	value = (value > 0) ? 0 : value; //only negative translate value
		    	value = ( !(typeof totWidth === 'undefined') &&  value < totWidth ) ? totWidth : value; //do not translate more than timeline width
		    setTransformValue(eventsWrapper, 'translateX', value+'px');
		    //update navigation arrows visibility
		    (value == 0 ) ? timelineComponents['timelineNavigation'].find('.prev').addClass('inactive') : timelineComponents['timelineNavigation'].find('.prev').removeClass('inactive');
		    (value == totWidth ) ? timelineComponents['timelineNavigation'].find('.next').addClass('inactive') : timelineComponents['timelineNavigation'].find('.next').removeClass('inactive');
		}

		function setTransformValue(element, property, value) {
    		element.style["-webkit-transform"] = property+"("+value+")";
		    element.style["-moz-transform"] = property+"("+value+")";
		    element.style["-ms-transform"] = property+"("+value+")";
		    element.style["-o-transform"] = property+"("+value+")";
		    element.style["transform"] = property+"("+value+")";
  		}


  		function getTranslateValue(timeline) {
    		var timelineStyle = window.getComputedStyle(timeline.get(0), null),
      			timelineTranslate = timelineStyle.getPropertyValue("-webkit-transform") ||
	            timelineStyle.getPropertyValue("-moz-transform") ||
	            timelineStyle.getPropertyValue("-ms-transform") ||
	            timelineStyle.getPropertyValue("-o-transform") ||
	            timelineStyle.getPropertyValue("transform");

	        if( timelineTranslate.indexOf('(') >=0 ) {
	            var timelineTranslate = timelineTranslate.split('(')[1];
	        	  	timelineTranslate = timelineTranslate.split(')')[0];
	        	  	timelineTranslate = timelineTranslate.split(',');
	            var translateValue = timelineTranslate[4];
	        } else {
	          	var translateValue = 0;
	        }

        	return Number(translateValue);
  		}

	});
});