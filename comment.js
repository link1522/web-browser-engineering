var strong = document.querySelectorAll('strong')[0];

function lengthCheck() {
  var value = this.getAttribute('value');
  if (value.length > 3) {
    strong.innerHTML = 'Comment too long!';
  }
}

var input = document.querySelectorAll('input');
for (var i = 0; i < input.length; i++) {
  input[i].addEventListener('keydown', lengthCheck);
}
