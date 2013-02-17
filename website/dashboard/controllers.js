function ScheduleCtrl($xhr, $defer) {
  var self = this;

  var hourOffset = 0;
  // used for debugging
  var hourOffset = 9 - (new Date().getMinutes());

  self.response = null;
  self.currentTime = "--:--";
  self.eventBlocks = [];

  $xhr("GET", "schedule.json", function(code, response) {
    self.response = response;
    self.update();
  });

  // periodically update page
  self.update = function() {
    var now = new Date();
    // debug only
    if (1) {
      var hours = now.getMinutes() + hourOffset;
      var minutes = now.getSeconds();
      now.setDate(24);
      now.setMonth(1);
      now.setYear(2013);
      now.setHours(hours);
      now.setMinutes(minutes);
    }

    var hours = now.getHours();
    var minutes = now.getMinutes();
    if (minutes < 10) {
      minutes = "0" + minutes;
    }
    self.currentTime = hours + ":" + minutes;

    var nowMinus10 = now.getTime() / 1000 - 600; // now - 10 minutes in seconds

    // reset events
    self.eventBlocks = [];
    // group events by time
    var lastTime = "";
    var lastGroup = [];
    var groupCount = 0;
    angular.forEach(self.response.items, function(value, key) {
      if (value.timestamp < nowMinus10) {
        // past event, ignore it
      } else if (value.start != lastTime) {
        if (lastGroup.length > 0 && groupCount < 2) {
          self.eventBlocks.push({"start": lastTime, "events": lastGroup});
          groupCount += 1;
        };
        lastTime = value.start;
        lastGroup = [value];
      } else {
        lastGroup.push(value);
      }
    });
    if (lastGroup.length > 0 && groupCount < 2) {
      self.eventBlocks.push({"start": lastTime, "events": lastGroup});
    }

    $defer(self.update, 1000);
  }

  $defer(self.update, 1000);

}

//ScheduleCtrl.$inject = ['$xhr'];

