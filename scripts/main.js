var pars = {};

function on_start_click() {
  $("#idstatusstr").html('Running');

  pars.rate = $("#idrate").val();
  pars.conn = $("#idconn").val();
  pars.lasturl = $("#idurl").val();

  if(typeof pars.urls === "undefined") {
    pars.urls = {};
  }

  pars.urls[$("#idurl").val()] = 0;

  var posting = $.ajax("/start", {
    data : JSON.stringify(pars),
    contentType : 'application/json',
    type : 'POST'});
 
  posting.done(function(data) {
  });

  posting.fail(function(data) {
    $("#idstatusstr").html('error calling /start');
  });
};

function on_stop_click() {
  $("#idstatusstr").html('Stopped');

  var pars = {};

  var posting = $.ajax("/stop", {
    data : JSON.stringify(pars),
    contentType : 'application/json',
    type : 'POST'});
 
  posting.done(function(data) {
  });

  posting.fail(function(data) {
    $("#idstatusstr").html('error calling /stop');
  });
};

function on_oldurl_click(val) {
  $("#idurl").val(val);
};

$(document).ready(function() {
  var jqxhr = $.get("/last", function(data) {
    $("#idrate").val(data.rate);
    $("#idconn").val(data.conn);
    $("#idurl").val(data.lasturl);

    if(typeof pars.urls === "undefined") {
      pars.urls = {};
    }

    $("#idoldurls").html('');
    for(var url in data.urls) {
      pars.urls[url] = 0;
      $("#idoldurls").append('<li onclick="on_oldurl_click(\'' + url + '\');"><a href="#">' + url + '</a></li>');
    }
  })
  .fail(function() {
    $("#idstatusstr").html('error calling /last');
  })
});

function on_status_timeout() {
  var jqxhr = $.get("/status", function(data) {
    if(data.running === true) {
      $("#idstatusstr").html('Running');
    } else {
      $("#idstatusstr").html('Stopped');
    }
  })
  .fail(function() {
    $("#idstatusstr").html('error calling /status');
  })
}

setInterval(on_status_timeout, 3000);