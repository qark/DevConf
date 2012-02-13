console.log("DEVCONF: initializing application");

// configuration
var localScheduleURL = "schedule.json";
var remoteScheduleURL = "http://m.devconf.cz/schedule.json";
var remoteScheduleTsURL = "http://m.devconf.cz/schedule-ts.json";

// initialize global variables
var schedule = null;
var currentEvent = null;
var scheduleDate = "2012-02-17";

// remove record for debugging purposes
// localStorage.removeItem("schedule");

//
// General functions
//
function loadAndRenderSchedule() {
  $("#schedule-refresh").text("Refreshing...");
  if (schedule) {
    // check timestamp of remote schedule
    console.log("DEVCONF: Getting remote schedule timestamp from", remoteScheduleTsURL);
    $.getJSON(remoteScheduleTsURL, function(data) {
      console.log("DEVCONF: remote schedule timestamp", data);
      console.log("DEVCONF: local schedule timestamp ", schedule["timestamp"]);
      if (data > schedule["timestamp"] || true) {
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
    schedule = data;
    renderSchedule(schedule);
    try {
      localStorage.setItem("schedule", JSON.stringify(schedule));
      console.log("DEVCONF: schedule stored to local storage");
    } catch(e) {}
  }).error(function(data) {
    console.warn("DEVCONF: Cannot load", url);
    $("#eventItems").text("Cannot load data...");
    if (url != localScheduleURL) {
      // last attempt - load local schedule
      loadAndRenderScheduleCont(localScheduleURL);
    }
  }).complete(function () {
    $("#schedule-refresh").text("Refresh");
    console.log("DEVCONF: Schedule finished");
  });
}

function filterSchedule(items, date) {
  var count = 0;
  var lastStart = "UNDEF";
  $.each(items, function(i, item) {
     var display = true;
     if (item["date"] != date) {
       display = false;
     }
     if (count > 1000) {
       display = false;
     }
     if (item["speaker"] == "N/A") {
       item["speaker"] = "";
     }
     if (item["description"] == "N/A") {
       item["description"] = "";
     }
     item["eventIndex"] = i;
     item["display"] = display;
     if (display) {
       item["showTime"] = item["start"] != lastStart;
       lastStart = item["start"];
       count = count + 1;
     } else {
       item["showTime"] = false;
     }
  });
}

function displaySchedule(date) {
  scheduleDate = date;
  console.log("DEFCONF: displaying schedule for", scheduleDate);
  $.mobile.changePage("schedule.html");
  return false;
}

function renderSchedule(schedule) {
  console.log("DEFCONF: rendering schedule for", scheduleDate);
  filterSchedule(schedule["items"], scheduleDate);
  $("#eventItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  // refresh views
  $("#eventList").listview("refresh");
}

function loadAndRenderTweets() {
  $("#twitter-refresh").text("Refreshing...");
  $.getJSON("http://search.twitter.com/search.json?q=%23devconf&rpp=10&callback=?", function(data) {
    console.log("DEVCONF: twitter data loaded");
    $("#tweets").replaceWith($("#tweetTemplate").render(data["results"]));
    $("#twitterList").listview("refresh");
  }).error(function(data) {
    console.warn("DEVCONF: Cannot load twitter data");
    $("#tweets").text("Cannot load data...");
  }).complete(function () {
    $("#twitter-refresh").text("Refresh");
  });
  return false;
}

//
// Event handlers
//
$("#schedulePage").live('pageshow', function(event) {
  console.log("DEVCONF: #schedulePage pageinit event");
  // try local storage first
  try {
    schedule = JSON.parse(localStorage.getItem("schedule"));
    console.log("DEVCONF: schedule loaded from local storage");
  } catch(e) {}
  loadAndRenderSchedule();
  return false;
});

$("#twitterPage").live('pageshow', function(event) {
  console.log("DEVCONF: #twitterPage pageinit event");
  loadAndRenderTweets();
  return false;
});
