$(document).ready(function() {
    // Initialize variables
    var $messages = $('.chat-messages');
    var $input = $('.chat-input input');
    var $submit = $('.chat_submit');
    var $chatContainer = $('.chat-container');
    var session_id = '';
    $messages.children().each(function() {
        $(this).addClass('chat-message');
    });

    // Initialize SocketIO connection
    var socket = io.connect('https://' + document.domain + ':' + location.port);

    // Function to send message to Flask-SocketIO app
    function sendMessage(message) {
        console.log("message: " + message )
        socket.emit('message', {'question': message});
    }

    // Function to display message
    function displayMessage(message, isUser) {
        var $message = $('<div>').addClass('chat-message round');
        var $messageText = $('<p>').html(message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1">$1</a>'));

        $message.append($messageText);
        if (isUser) {
            $message.addClass('user');
        } else {
            $message.addClass('bot')
        }
        if ($messages) {
            $messages.append($message);
            if ($messages[0]) {
                $messages.animate({scrollTop: $messages[0].scrollHeight}, 300);
            }
        } else {
            $('.chat-container').append($message);
            $('.chat-container').animate({scrollTop: 0}, 300);
        }
    }


    socket.on('response', function(data) {
        console.log("Received response: " + data.response)
        var response = data.response;
        displayMessage(response, false);
    });


    // Send message on submit
    $submit.click(function(event) {
        event.preventDefault();
        var message = $input.val().trim();
        console.log("Submit clicked: " + message)
        if (message !== '') {
            displayMessage(message, true);
            sendMessage(message);
            $input.val('');
        }
    });

    // Send message on enter key press
    $input.keydown(function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            $submit.click();
        }
    });

    // Initial message
    displayMessage('Ask me anything');

    // Function to minimize widget
    function minimizeWidget() {
        $chatContainer.toggleClass('minimized');
        if ($chatContainer.hasClass('minimized')) {
            $chatContainer.find('.chat-header h4').hide();
            $chatContainer.find('.chat-input').hide();
            $chatContainer.find('.chat-body').hide();
            $chatContainer.find('.chat-header i.fa-close').removeClass('fa-close').addClass('fa-comment');
        } else {
            $chatContainer.find('.chat-header h4').show();
            $chatContainer.find('.chat-input').show();
            $chatContainer.find('.chat-body').show();
            $chatContainer.find('.chat-header i.fa-comment').removeClass('fa-comment').addClass('fa-close');
        }
    }

// Minimize widget on close button click
    $('.chat-close').click(function() {
        minimizeWidget();
    });

});
