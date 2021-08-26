import React from 'react';
import { Typography } from '@material-ui/core';
import { Divider } from '@material-ui/core';
import { makeStyles, withStyles } from '@material-ui/core/styles';
import {
  Switch,
  Route,
  Link,
  withRouter,
  useParams
} from "react-router-dom";

import './Chat.css';
import WS from '../../lib/websocket.js';
import api from '../../lib/api.ts';
import Button from '../Button.js';


const styles = theme => {
  return {
    messageFormMessage: {
      backgroundColor: theme.palette.background.paper
    },
    members: {
      backgroundColor: theme.palette.background.paper
    },
    messageFormText: {
      color: theme.palette.text.secondary
    },
    messageFormInput: {
      color: theme.palette.text.primary
    },
    message: {
      '&:hover': {
        backgroundColor: theme.palette.background.paper
      }
    },
    roomInfo: {
      order: 0,
      backgroundColor: theme.palette.background.paper,
      // justifyContent: 'flex-start'
    },
    roomTitle: {
      fontSize: '1.2rem',
      fontWeight: 600
    }
  }
};

const useStyles = makeStyles(styles);


function ChatListRoom() {
  return (
    <Button type="li" className="room-listing" onClick={() => {console.log('clicked')}}>
      {/* <div className="click-ripple"></div> */}
      <avatar-element className="room-avatar">EC</avatar-element>
      <div className="room-info">
        <p className="room-title">
          <span className="room-name">
          Example Chat
          </span>
          <span className="room-message-date">
            Mon
          </span>
        </p>
        <p className="room-subtitle">
          <span className="last-message">
            Previous message content...
          </span>
        </p>
      </div>
    </Button>
  )
}

function ChatList() {
  return (
    <div className="ChatList">
      <ul>
        <ChatListRoom />
        <ChatListRoom />
      </ul>
    </div>
  )
}

function Message(props) {
  const classes = useStyles();

  return (
    <div className={classes.message}>
      <span className="Message-author">
        {props.message.author.name}
      </span><br />
      <div className="Message-content">
        {props.message.content}
      </div>
    </div>
  );
}

class _MessageForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: ''};
    this.handleChange = this.handleChange.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  handleChange(event) {
    const value = event.target.innerHTML.replace(/<br\s*[\/]?>/gi, "\n");
    this.setState({value: value.trim()});

    if (!event.target.textContent.trim()) {
      event.target.textContent = event.target.placeholder;
    }
  }

  handleKeyPress(event) {
    if (event.which === 13 && !event.shiftKey) {
      event.preventDefault();
      this.handleSubmit(event);
    }
  }

  handleBlur(event) {
    const element = event.target;
    if (!element.textContent.trim().length) {
      element.textContent = '';
    }
  }

  handleSubmit(event) {
    console.log('A message was submitted: ' + this.state.value);
    event.target.textContent = '';
    if (!this.state.value) {
      return;
    }
    this.props.sendCallback(this.state.value);
    this.setState({value: ''});
  }

  render() {
    const classes = this.props.classes;

    return (
      <div className="MessageForm">
        <div className={`MessageForm-message ${classes.messageFormMessage}`}>
          <form className="MessageForm-form">
            <div
            className={`MessageForm-input ${classes.messageFormInput}`}
            aria-autocomplete="list"
            contentEditable="true"
            role="textbox"
            spellCheck="true"
            placeholder="Enter a message..."
            type="text"
            onInput={this.handleChange}
            onBlur={this.handleBlur}
            onKeyUp={this.handleChange}
            onKeyDown={this.handleKeyPress}
            onInput={this.handleInput}
            />
          </form>
        </div>
        <div className={`MessageForm-text ${classes.messageFormText}`}>
          <Typography>This is text that can appear below the message form.</Typography>
        </div>
      </div>
    );
  }
}


const MessageForm = withStyles(styles)(_MessageForm);


function RoomInfo(props) {
  const classes = useStyles();
  return (
    <div className={classes.roomInfo}>
      <Typography varient="h1" className={classes.roomTitle}>
        {props.room.name}
      </Typography>
    </div>
  );
}

class Chat extends React.Component {
  constructor(props) {
    super(props);
  }

  // componentDidUpdate() {
  //   const messagesDiv = document.querySelector('#Messages');
  //   messagesDiv.scrollTop = messagesDiv.scrollHeight - messagesDiv.clientHeight;
  // }

  render() {
    if (!this.props.room) {
      return <div className="Chat" />;
    }

    const classes = this.props.classes;

    return (
      <div className="Chat">
        <div className="MessageBox">
          <RoomInfo room={this.props.room}/>
          <div className="Messages-wrapper">
            <div className="Messages">
              <div id="Messages" className="Messages-inner">
                {this.props.messages.map((message) => (
                  <Message message={message} key={message.id} />
                ))}
              </div>
            </div>
          </div>
          <MessageForm sendCallback={this.handleSend}/>
        </div>
        <div className={`Members ${classes.members}`}>
          <p>This is the members list.</p>
        </div>
      </div>
    );
  }

  handleSend = content => {
    api.post(`/rooms/${this.props.room.id}/messages`, {
      content: content
    });
  }
}

export default withRouter(withStyles(styles)(Chat));
