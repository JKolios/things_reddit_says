<html xmlns="http://www.w3.org/1999/html">
    <head>
        <link rel="stylesheet" type="text/css" href="/static/style.css">
    </head>
    <body>
        <p id='title'>Reddit just said:</p>
        <p class="fade_anim" id='message'>Hello!</p>
        <p id='metadata'>Just a moment.</p>
        <p id='permalink'><a href="http://www.reddit.com">If you see this, I messed up.</a></p>
        <div id="form_container">
            <label for="subreddit">Subreddit:</label>
            <input id="subreddit" type="text" name="subreddit" value="all">
            <button id="change_button">Submit</button>
        </div>

        <script type="text/javascript" src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
        <script type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min.js"></script>
        <script>

            var uri = 'http://{{host[0]}}:{{host[1]}}/reddit_stream'
            var socket = io.connect(uri);
            var frontend_id = null;
            var messageElement = $("#message");
            var metadataElement = $("#metadata");
            var permalinkElement = $("#permalink");

            function change_subreddit(subreddit){
                var emit_object = {'frontend_id': frontend_id, 'new_subreddit': subreddit}
                console.log('Changing to ' + subreddit);
                socket.emit('change_subreddit',emit_object);
            }

            messageElement.on('webkitAnimationEnd oanimationend msAnimationEnd animationend', function() {

                console.log('Sending get_next');
                socket.emit('get_next', frontend_id);

            });

            messageElement.click(function() {
                var paused = $(this).data('paused');
                if(paused) {

                    console.log('Resuming animation');
                    $(this).css("webkitAnimationPlayState", 'running');
                    permalinkElement.css('display', 'none');

                }else{
                    console.log('Pausing animation');
                    $(this).css("webkitAnimationPlayState", 'paused');
                    permalinkElement.css('display', 'block');

                }
                $(this).data("paused", !paused);
            });

            socket.on( 'connect', function() {

                $("#message").text("Connected to: " + uri);
            });

            socket.on('init_response', function(response) {
                console.log('Got frontend_id: '+ response)
                frontend_id = response;
            });

            socket.on( 'message', function(message) {

                console.log(message);
                var messageClone = messageElement.clone(true);
                messageElement.remove();
                messageClone.text(message['comment']);
                $('#title').after(messageClone);

                metadataElement.text("Posted by " + message['author_name'] + " to r/" + message['subreddit']);
                permalinkElement.find("a").text(message['permalink']);
                permalinkElement.find("a").prop('href', message['permalink'])
                messageElement = $("#message");

            });

            socket.on( 'exception', function(message) {

                messageElement.text(message);
                metadataElement.text("Sorry :(");

            });

            socket.on( 'disconnect', function() {

                messageElement.text("disconnected");
                metadataElement.text("Sorry :(");

            });

            $(document).ready(function() {
                $("#change_button").click(function() {
                    $(this).css("webkitAnimationPlayState", 'paused');
                    change_subreddit($('#subreddit').val());
                });
            });

        </script>
    <body>
<html>