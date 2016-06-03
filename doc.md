# websocket messages
## from server
### your_turn
Message with no payload to indicate that it's the recipient's turn to play.

### server message
Message with some information for the client.

### px2client
Message with a point as payload.

## from client
### im_done
Message with no payload to indicate that the client ended its turn.

### px2server
Message with a point as payload.

### register
Message with the battleroom as payload to register the websocket in the server battleroom.