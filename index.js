console.log('hi');

var inputEls = document.querySelectorAll('input');

for (var i = 0; i < inputEls.length; i++) {
  console.log(inputEls[i].getAttribute('name'));
}
