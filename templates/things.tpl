<html>
    <head>
        <link rel="stylesheet" type="text/css" href="/static/style.css">
    </head>
    <body>
        <p id='title'>Reddit just said:</p>
        <p id='message'>Hello!</p>

        <script type="text/javascript" src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
        <script type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min.js"></script>
        <script>
              var uri = 'http://{{host[0]}}:{{host[1]}}/reddit_stream'
              var socket = io.connect(uri);
              socket.on( 'connect', function() {
                    $("#message").text("Connected to: " + uri);
              } );

              socket.on( 'message', function(message) {
                  var messageElement = $("#message");
                  var messageClone = messageElement.clone(true);
                  messageClone.text(message);
                  messageElement.before(messageClone);
                  messageElement.remove()
              } );


              socket.on( 'disconnect', function() {
                    $("#message").text("disconnected :(");
              } );
        </script>

    <body>
<html>