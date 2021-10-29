var express = require('express');
var path = require('path');
var routes = require('./routes/routes.js');
var app = express();
var morgan = require('morgan')
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var session = require('express-session');

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }))
 
// parse application/json
app.use(bodyParser.json())

app.use(function(req, res, next) {
    res.setHeader("Cache-Control", "no-cache must-revalidate");
    next();
});

app.use(morgan('combined'));

app.use(cookieParser());
app.use(session({secret: 'secret'}));

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use('/', express.static(__dirname + "/public",{maxAge:1}));


app.get('/', routes.get_homepage);
app.get('/identity_search', routes.get_identity_search_page);
app.post('/searched_group', routes.searched_group);
app.get('/timeline', routes.get_timeline);
app.get('/metadata', routes.get_metadata);
app.get('/ppmi', routes.get_ppmi);

/* Run the server */

app.listen(8080);
console.log('Server running on port 8080. Now open http://localhost:8080/ in your browser!');