import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import {
  Switch,
  Route,
  Link,
  withRouter,
  useParams
} from "react-router-dom";

import './Home.css';
import WS from '../lib/websocket.js';
import api from '../lib/api.ts';
import SideBar from './sidebar/SideBar.js';
import Chat from './chat/Chat.js';


function Loading() {
  return (
    <div className="Loading">
      <div className="Loading-progress-bar">
        <CircularProgress />
        <Typography varient="h1">Connecting</Typography>
      </div>
    </div>
  )
}


class Home extends React.Component {
  constructor(props) {
    super(props);

    const token = localStorage.getItem('token')
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    const url = api.defaults.baseURL.replace(/^https?:\/\//, '')
    console.log(url);

    this.state = {
        loggedIn: false,
        redirect: false,
        token: token,
        websocket: new WS(`ws://${url}/websocket/connect`),
        me: null,
        selectedRoom: null
    };
  }

  render() {
    if (!this.state.loggedIn || !this.state.me) {
      return <Loading />;
    }

    let messages = [];

    if (this.state.selectedRoom) {
      messages = this.state.me.rooms[this.state.selectedRoom].messages;
    }

    if (!messages) {
      messages = [];
    }

    console.log('rendering...');
    console.log(this.state.me);

    return(
      <div className="Home">
        <SideBar
          rooms={this.state.me.rooms}
          active={this.state.selectedRoom}
          selectCallback={this.roomSelectCallback}
        />

        <Switch>
          <Route path={`${this.props.match.path}room/:roomID`}>
          <Chat
            room={this.state.me.rooms[this.state.selectedRoom]}
            messages={messages}
          />
          </Route>
          <Route path={this.props.match.path}></Route>
        </Switch>
      </div>
    );
  }

  componentDidMount() {
    this.initialLoad();
    this.state.websocket.connect(this.state.token);

    this.state.websocket.onConnect = () => {
      this.setState({loggedIn: true});
    }

    this.state.websocket.onDispatch = (event, data) => {
      this.handleDispatch(event, data);
    }

    this.state.websocket.onDisconnect = () => {
      this.setState({loggedIn: false});
      // TODO: add actual reconnect logic
      this.state.websocket.connect(this.state.token);
    }
  }

  initialLoad() {
    api.get('/users/me')
    .then(response => {
      this.setState({me: response.data});
    })
    .catch(error => {
      if (error.response) {
        console.log(error.response)
        if (error.response.status===401) {
          localStorage.removeItem('token');
          this.props.logout();
          // this.setState({redirect: true});
        }
      }
    });
  }

  roomSelectCallback = roomID => {
    console.log(roomID);
    this.setState({selectedRoom: roomID});
  }

  onMessage(message) {
    console.log(`Message recieved: ${message.author.name}: ${message.content}`)
    this.setState((state, props) => {
      const me = JSON.parse(JSON.stringify(state.me));
      console.log(me);
      if (!me.rooms[message.room_id].messages) {
        me.rooms[message.room_id].messages = [];
      }
      me.rooms[message.room_id].messages.push(message);
      return {me: me};
    });
  }

  handleDispatch(event, data) {
    if (event === 'MESSAGE') {
      this.onMessage(data);
    }
  }
}

export default withRouter(Home);
