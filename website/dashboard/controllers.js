function ScheduleCtrl($xhr, $defer) {
    var self = this;
    var hourOffset = 0;
    var debug = 0;

    if (debug) {
        var hourOffset = 9 - (new Date().getMinutes());
    }

    var monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    self.response = null;
    self.currentTime = "--:--";
    self.eventBlocks = [];

    self.tweetBlocks = [];

    $xhr("GET", "schedule.json", function(code, response) {
        self.response = response;
        self.update();
    });

    // periodically update page
    self.update = function() {
        var now = new Date();

        // debug only
        if (debug) {
            var hours = now.getMinutes() + hourOffset;
            var minutes = now.getSeconds();

            now.setDate(7);
            now.setMonth(1);
            now.setYear(2014);
            now.setHours(hours);
            now.setMinutes(minutes);
        }

        var hours = now.getHours();
        var minutes = now.getMinutes();

        if (minutes < 10) {
            minutes = "0" + minutes;
        }

        self.currentTime = monthNames[now.getMonth()] + " " + now.getDate() + ", " + hours + ":" + minutes;

        var nowMinus10 = now.getTime() / 1000 - 600; // now - 10 minutes in seconds

        var nowPlus12H = now.getTime() / 1000 + 43200; // now + 12 hours in seconds

        // reset events
        self.eventBlocks = [];

        // group events by time
        var lastTime = "";
        var lastGroup = [];
        var groupCount = 0;

        angular.forEach(self.response.items, function(value, key) {
            if (value.timestamp < nowMinus10) {
                // past event, ignore it
            } else if (value.timestamp > nowPlus12H) {
               // too future event, ignore it
            } else if (value.start != lastTime) {
                if (lastGroup.length > 0 && groupCount < 3) {
                    self.eventBlocks.push({
                        "start": lastTime,
                        "events": lastGroup
                    });

                    groupCount += 1;
                }

                lastTime = value.start;
                lastGroup = [value];
            } else {
                lastGroup.push(value);
            }
        });

        if (lastGroup.length > 0 && groupCount < 3) {
            self.eventBlocks.push({
                "start": lastTime,
                "events": lastGroup
            });
        }

        $defer(self.update, 1000);
    }

    $defer(self.update, 1000);
}

// Twitter wall
var cb = new Codebird();

cb.setConsumerKey("az8fSMEk8vLfgV6jTtqeLA", "Ue774UHRqkKNGmnPVQDCqFvFXBqOOIJaDzIRwso");
cb.setToken("122488572-oDW67BugvGbi5ylneiBWKisKdxWAzT7r59tq21Dk", "OdctR7PfqxoJEZiCqR8dm09SaINqHohDX9vSojMxV7Dba");

var fetchTweets = function() {
    cb.__call(
        "search_tweets",
        "q=%23DevConfBrno&result_type=recent&count=10",
        function(response) {
            $('#tweets').empty();

            $.each(response.statuses, function(i, data) {
                var tweet = $(document.createElement('div'));

                tweet.html('' +
                    '<img src="' + data.user.profile_image_url + '" />' +
                    '<strong>' + data.user.name + ', ' + parseTwitterDate(data.created_at) + ':</strong> ' +
                    '<span>' + data.text + '</span>'
                ).addClass('tweet').attr('rel', data.created_at);

                $('#tweets').append(tweet);
            });
        },
        true
    );
}

// from http://widgets.twimg.com/j/1/widget.js
var K = function() {
    var a = navigator.userAgent;
    return {
        ie: a.match(/MSIE\s([^;]*)/)
    }
};

var parseTwitterDate = function(tdate) {
    var system_date = new Date(Date.parse(tdate)),
        user_date = new Date();

    if (K.ie) {
        system_date = Date.parse(tdate.replace(/( \+)/, ' UTC$1'))
    }

    var diff = Math.floor((user_date - system_date) / 1000);

    if (diff <= 1) {return "just now";}
    if (diff < 20) {return diff + " seconds ago";}
    if (diff < 40) {return "half a minute ago";}
    if (diff < 60) {return "less than a minute ago";}
    if (diff <= 90) {return "one minute ago";}
    if (diff <= 3540) {return Math.round(diff / 60) + "m ago";}
    if (diff <= 5400) {return "1h ago";}
    if (diff <= 86400) {return Math.round(diff / 3600) + "h ago";}
    if (diff <= 129600) {return "1d ago";}
    if (diff < 604800) {return Math.round(diff / 86400) + "d ago";}
    if (diff <= 777600) {return "1w ago";}

    return "on " + system_date;
}

// init
fetchTweets();

// set polling interval
setInterval(fetchTweets, 10000); // 10s
