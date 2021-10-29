//handles /homepage
var getHomepage = function(req, res) {
	res.render('search.ejs');
};

var searchedGroup = function(req, res) {
	res.render('search.ejs');
};

var getIdentitySearchPage = function(req, res) {
	res.render('search.ejs');
};

var getTimeline = function(req, res) {
	var data = [1992,1996,2000,2004,2008,2012,2016];
	res.render('timeline.ejs',{data:data});
};

var getMetadata = function(req, res) {
	res.render('metadata.ejs');
};

var getPPMI = function(req, res) {
	var data = [1992,1996,2000,2004,2008,2012,2016];
	res.render('ppmi.ejs',{data:data});
};



var routes = {
	get_identity_search_page:getIdentitySearchPage,
	get_homepage: getHomepage,
	get_timeline: getTimeline,
	searched_group: searchedGroup,
	get_metadata: getMetadata,
	get_ppmi:getPPMI
}

module.exports = routes;