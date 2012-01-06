console.log("DEVCONF: initializing application");

var schedule = null;

$("#schedulePage").live('pageinit',function(event) {
  console.log("DEVCONF: #schedulePage pageinit event");
  $.getJSON("schedule.json", function(data) {
    console.log("DEVCONF: schedule.json loaded");
    schedule = data
    filterSchedule(schedule["items"], "talk", "2012-02-17");
    $("#talkItems").replaceWith($("#itemTemplate").render(schedule));
    filterSchedule(schedule["items"], "lab", "2012-02-17");
    $("#labItems").replaceWith($("#itemTemplate").render(schedule));
    // refresh views
    $("#eventList").listview("refresh");
  }).error(function(data) {
    console.warn("DEVCONF: Cannot load schedule.json");
    $("#talkItems").text("Cannot load data...");
    $("#labItems").text("Cannot load data...");
  });
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

     item["display"] = display;
  });
}

