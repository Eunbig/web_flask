$(function() {
  var capsLockEnabled = null;
  document.msCapsLockWarningOff = true; // Set this to true to turn off default IE behavior. 
  var isCheckEnabled = document.msCapsLockWarningOff === undefined || document.msCapsLockWarningOff;

  var checkWarning = function() {
      if (capsLockEnabled) {
            $("#warning").show();
          } else {
                $("#warning").hide();
              }
    }

  if (isCheckEnabled) {
      $(document).keydown(function(e) {
            if (e.which == 20 && capsLockEnabled !== null) {
                    capsLockEnabled = !capsLockEnabled;
                    console.log("Keydown. CapsLock enabled: " + capsLockEnabled.toString());
                  } else if (e.which == 20) {
                          console.log("Keydown. Initial state not set.");
                        }
          });
  
      $(document).keypress(function(e) {
            var str = String.fromCharCode(e.which);
            if (!str || str.toLowerCase() === str.toUpperCase()) {
                  console.log("Keypress. Some control key pressed.");
                    return;
                  }
            capsLockEnabled = (str.toLowerCase() === str && e.shiftKey) || (str.toUpperCase() === str && !e.shiftKey);
            console.log("Keypress. CapsLock enabled: " + capsLockEnabled.toString());
          });
  
      $("#password").keyup(function(e) {
            checkWarning();
          });
  
      $("#password").on("focus", function(e) {
            checkWarning();
          });
  
      $("#password").on("blur", function(e) {
            console.log("Hiding warning")
            $("#warning").hide();
          });
    }

    console.log("Focusing username")
  $("#username").focus();
})
