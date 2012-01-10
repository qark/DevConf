console.log("DEVCONF: initializing application");

var schedule = null;
var currentEvent = null

if (localStorage) {
  console.log("DEVCONF: loading schedule from local storage");
  localStorage.getItem("schedule");
}

$("#schedulePage").live('pageinit', function(event) {
  console.log("DEVCONF: #schedulePage pageinit event");
  // try local storage first
  if (localStorage) {
    console.log("DEVCONF: loading schedule from local storage");
    schedule = JSON.parse(localStorage.getItem("schedule"));
  }
  if (schedule == null) {
    $.getJSON("schedule.json", function(data) {
      console.log("DEVCONF: schedule.json loaded");
      schedule = data
      renderSchedule(schedule)
      if (localStorage) {
        console.log("DEVCONF: storing schedule to local storage");
        localStorage.setItem("schedule", JSON.stringify(schedule));
      }
    }).error(function(data) {
      console.warn("DEVCONF: Cannot load schedule.json");
      $("#talkItems").text("Cannot load data...");
      $("#labItems").text("Cannot load data...");
    });
  } else {
    renderSchedule(schedule)
  }
  return false;
})

$("#eventDetailsPage").live('pagebeforecreate', function(event) {
  console.log("DEVCONF: #eventDetailsPage pageinit event");
  $("#content").html($("#contentTemplate").render(currentEvent));
  return false;
})

function filterSchedule(items, type, date) {
  $.each(items, function(i, item) {
     var display = true;
     if (item["type"] != type) {
       display = false;
     }
     if (item["date"] != date) {
       display = false;
     }
     item["eventIndex"] = i;
     item["display"] = display;
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
  filterSchedule(schedule["items"], "talk", "2012-02-17");
  $("#talkItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  filterSchedule(schedule["items"], "lab", "2012-02-17");
  $("#labItems").replaceWith($("#itemTemplate").render(schedule["items"]));
  // refresh views
  $("#eventList").listview("refresh");
}
