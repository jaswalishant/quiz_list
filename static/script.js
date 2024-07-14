let minutes = 5;
let seconds = minutes * 60;
timer = document.getElementsByClassName("timer")[0];

// function for timer
setInterval(function () {
  min = Math.floor(seconds / 60);
  sec = seconds % 60;
  sec = sec < 10 ? "0" + sec : sec;
  min = min < 10 ? "0" + min : min;
  timer.innerHTML = `${min}:${sec}`;
  seconds--;
}, 1000);

setTimeout(() => {
  document.getElementById("submit").submit();
  alert("Time is up");
}, seconds * 1000);
