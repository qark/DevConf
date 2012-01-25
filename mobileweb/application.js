console.log("DEVCONF: initializing application");

// configuration
var localScheduleURL = "schedule.json";
var remoteScheduleURL = "http://m.devconf.cz/schedule.json";
var remoteScheduleTsURL = "http://m.devconf.cz/schedule-ts.json";

// initialize global variables
var schedule = null;
var currentEvent = null;

// remove record for debugging purposes
// localStorage.removeItem("schedule");

//
// Event handlers
//
$("#schedulePage").live('pageinit', function(event) {
  console.log("DEVCONF: #schedulePage pageinit event");
  // try local storage first
  if (localStorage) {
    console.log("DEVCONF: loading schedule from local storage");
    schedule = JSON.parse(localStorage.getItem("schedule"));
  }
  loadAndRenderSchedule();
  return false;
})

$("#eventDetailsPage").live('pagebeforecreate', function(event) {
  console.log("DEVCONF: #eventDetailsPage pageinit event");
  $("#content").html($("#contentTemplate").render(currentEvent));
  return false;
})

$("#twitterPage").live('pagebeforecreate', function(event) {
  console.log("DEVCONF: #twitterPage pageinit event");
  loadAndRenderTweets();
})

//
// General functions
//
function loadAndRenderSchedule() {
  $("#schedule-refresh").text("Refreshing...");
  if (schedule) {
    // check timestamp of remote schedule
    console.log("DEVCONF: Getting remote schedule timestamp from", remoteScheduleTsURL);
    $.getJSON(remoteScheduleTsURL, function(data) {
      console.log("DEVCONF: remote schedule timestamp", data)
      console.log("DEVCONF: local schedule timestamp ", schedule["timestamp"]);
      if (data > schedule["timestamp"]) {
        console.log("DEVCONF: remote schedule is newer, updating...");
        loadAndRenderScheduleCont(remoteScheduleURL);
      } else {
        console.log("DEVCONF: no need to update schedule");
        renderSchedule(schedule);
        $("#schedule-refresh").text("Refresh");
      }
    }).error(function(data, e) {
      console.warn("DEVCONF: Cannot load timestamp, trying local schedule", data, e);
      loadAndRenderScheduleCont(localScheduleURL);
    });
  } else {
    console.log("DEVCONF: no schedule in storage, loading from", remoteScheduleURL);
    loadAndRenderScheduleCont(remoteScheduleURL);
  }
}

function loadAndRenderScheduleCont(url) {
  console.log("DEVCONF: Loading schedule from", url);
  $.getJSON(url, function(data) {
    console.log("DEVCONF: loaded", url);
    schedule = data
    renderSchedule(schedule)
    if (localStorage) {
      console.log("DEVCONF: storing schedule to local storage");
      localStorage.setItem("schedule", JSON.stringify(schedule));
    }
  }).error(function(data) {
    console.warn("DEVCONF: Cannot load", url);
    $("#talkItems").text("Cannot load data...");
    $("#labItems").text("Cannot load data...");
    if (url != localScheduleURL) {
      // last attempt - load local schedule
      loadAndRenderScheduleCont(localScheduleURL);
    }
  }).complete(function () {
    $("#schedule-refresh").text("Refresh");
  });
}

function filterSchedule(items, type, date) {
  var count = 0;
  $.each(items, function(i, item) {
     var display = true;
     if (item["type"] != type) {
       display = false;
     }
     if (item["date"] != date) {
       display = false;
     }
     if (count > 1000) {
       display = false;
     }
     item["eventIndex"] = i;
     item["display"] = display;
     count++;
  });
}

function displayDetails(eventNum) {
  if (eventNum == null) {
    eventNum = 0;
  }
  console.log("DEFCONF: display details for", schedule["items"][eventNum]["topic"]);
  currentEvent = schedule["items"][eventNum];
  $.mobile.changePage("details.html");
}

function renderSchedule(schedule) {
  console.log("DEFCONF: rendering schedule");
  filterSchedule(schedule["items"], "talk", "2012-02-17");
  $("#talkItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  filterSchedule(schedule["items"], "lab", "2012-02-17");
  $("#labItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  // refresh views
  $("#eventList").listview("refresh");
  scheduleRendered = true;
}

function loadAndRenderTweets() {
  $("#twitter-refresh").text("Refreshing...");
  $.getJSON("http://search.twitter.com/search.json?q=%23devconf&callback=?", function(data) {
    console.log("DEVCONF: twitter data loaded");
    $("#tweets").replaceWith($("#tweetTemplate").render(data["results"]));
    $("#twitterList").listview("refresh");
  }).error(function(data) {
    console.warn("DEVCONF: Cannot load twitter data");
    $("#tweets").text("Cannot load data...");
  }).complete(function () {
    $("#twitter-refresh").text("Refresh");
  });
}

