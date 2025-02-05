function lengthCheck() {
  var name = this.getAttribute('name');
  var value = this.getAttribute('value');
  console.log(value.length);
  if (value.length > 3) {
    console.log('Input ' + name + ' has to much text');
  }
}

var input = document.querySelectorAll('input');

for (var i = 0; i < input.length; i++) {
  input[i].addEventListener('keydown', lengthCheck);
}
