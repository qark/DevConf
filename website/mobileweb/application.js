console.log("RHEVENT: initializing application");

// configuration
var localScheduleURL = "schedule.json";
var remoteScheduleURL = "http://people.redhat.com/lsmid/devconf/mobileweb/schedule.json";
var remoteScheduleTsURL = "http://people.redhat.com/lsmid/devconf/mobileweb/schedule-ts.json";

// initialize global variables
var schedule = null;
var currentEvent = null;
var scheduleDate = "1970-01-01";

// remove record for debugging purposes
// localStorage.removeItem("schedule");

//
// General functions
//
function loadAndRenderSchedule() {
  $("#schedule-refresh").text("Refreshing...");
  if (schedule) {
    // check timestamp of remote schedule
    console.log("RHEVENT: Getting remote schedule timestamp from", remoteScheduleTsURL);
    $.getJSON(remoteScheduleTsURL, function(data) {
      console.log("RHEVENT: remote schedule timestamp", data);
      console.log("RHEVENT: local schedule timestamp ", schedule["timestamp"]);
      if (data > schedule["timestamp"] || true) {
        console.log("RHEVENT: remote schedule is newer, updating...");
        loadAndRenderScheduleCont(remoteScheduleURL);
      } else {
        console.log("RHEVENT: no need to update schedule");
        renderSchedule(schedule);
        $("#schedule-refresh").text("Refresh");
      }
    }).error(function(data, e) {
      console.warn("RHEVENT: Cannot load timestamp, trying local schedule", data, e);
      loadAndRenderScheduleCont(localScheduleURL);
    });
  } else {
    console.log("RHEVENT: no schedule in storage, loading from", remoteScheduleURL);
    loadAndRenderScheduleCont(remoteScheduleURL);
  }
}

function loadAndRenderScheduleCont(url) {
  console.log("RHEVENT: Loading schedule from", url);
  $.getJSON(url, function(data) {
    console.log("RHEVENT: loaded", url);
    schedule = data;
    renderSchedule(schedule);
    try {
      localStorage.setItem("schedule", JSON.stringify(schedule));
      console.log("RHEVENT: schedule stored to local storage");
    } catch(e) {}
  }).error(function(data) {
    console.warn("RHEVENT: Cannot load", url);
    $("#eventItems").text("Cannot load data...");
    if (url != localScheduleURL) {
      // last attempt - load local schedule
      loadAndRenderScheduleCont(localScheduleURL);
    }
  }).complete(function () {
    $("#schedule-refresh").text("Refresh");
    console.log("RHEVENT: Schedule finished");
  });
}

function filterSchedule(items, date) {
  var count = 0;
  var lastStart = "UNDEF";
  var now = new Date();
  // for debugging only
  // now.setDate(4);
  // now.setMonth(3);
  //
  var nowMinus10 = now.getTime() / 1000 - 600; // now - 10 minutes in seconds
  $.each(items, function(i, item) {
     var display = true;
     if (item["date"] != date) {
       display = false;
     }
     if (item["timestamp"] < nowMinus10) {
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
  console.log("RHEVENT: displaying schedule for", scheduleDate);
  $.mobile.changePage("schedule.html");
  return false;
}

function renderSchedule(schedule) {
  console.log("RHEVENT: rendering schedule for", scheduleDate);
  filterSchedule(schedule["items"], scheduleDate);
  $("#eventItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  // refresh views
  $("#eventList").listview("refresh");
}

function loadAndRenderTweets() {
  $("#twitter-refresh").text("Refreshing...");
  $.getJSON("http://search.twitter.com/search.json?q=%23devconf%20OR%20%40redhatcz&rpp=10&callback=?", function(data) {
    console.log("RHEVENT: twitter data loaded");
    $("#tweets").replaceWith($("#tweetTemplate").render(data["results"]));
    $("#twitterList").listview("refresh");
  }).error(function(data) {
    console.warn("RHEVENT: Cannot load twitter data");
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
  console.log("RHEVENT: #schedulePage pageinit event");
  // try local storage first
  try {
    schedule = JSON.parse(localStorage.getItem("schedule"));
    console.log("RHEVENT: schedule loaded from local storage");
  } catch(e) {}
  loadAndRenderSchedule();
  return false;
});

$("#twitterPage").live('pageshow', function(event) {
  console.log("RHEVENT: #twitterPage pageinit event");
  loadAndRenderTweets();
  return false;
});
