console = {
  log: function (x) {
    call_python('log', x);
  },
};

document = {
  querySelectorAll: function (s) {
    handles = call_python('querySelectorAll', s);
    return handles.map(function (h) {
      return new Node(h);
    });
  },
};

function Node(handle) {
  this.handle = handle;
}

Node.prototype.getAttribute = function (attr) {
  return call_python('getAttribute', this.handle, attr);
};

var LISTENERS = {};

Node.prototype.addEventListener = function (type, listener) {
  if (!LISTENERS[this.handle]) {
    LISTENERS[this.handle] = {};
  }
  var dict = LISTENERS[this.handle];
  if (!dict[type]) {
    dict[type] = [];
  }
  var list = dict[type];
  list.push(listener);
};

Node.prototype.dispatchEvent = function (evt) {
  var type = evt.type;
  var handle = this.handle;
  var list = (LISTENERS[handle] && LISTENERS[handle][type]) || [];
  for (var i = 0; i < list.length; i++) {
    list[i].call(this, evt);
  }
  return evt.do_default;
};

Object.defineProperty(Node.prototype, 'innerHTML', {
  set: function (s) {
    call_python('innerHTML_set', this.handle, s.toString());
  },
});

function Event(type) {
  this.type = type;
  this.do_default = true;
}

Event.prototype.preventDefault = function () {
  this.do_default = false;
};

function XMLHttpRequest() {}

XMLHttpRequest.prototype.open = function (method, url, is_async) {
  if (is_async) {
    throw Error('Asyncchronous requests is not supported');
  }
  this.method = method;
  this.url = url;
};

XMLHttpRequest.prototype.send = function (body) {
  this.responseText = call_python(
    'XMLHttpRequest_send',
    this.method,
    this.url,
    body
  );
};

SET_TIMEOUT_REQUEST = {};

function __runSetTimeout(handle) {
  var callback = SET_TIMEOUT_REQUEST[handle];
  callback();
}

function setTimeout(callback, time_delta) {
  var handle = Object.keys(SET_TIMEOUT_REQUEST).length;
  SET_TIMEOUT_REQUEST[handle] = callback;
  call_python('setTimeout', handle, time_delta);
}
