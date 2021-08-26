import React from 'react';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import Avatar from '@material-ui/core/Avatar';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Divider from '@material-ui/core/Divider';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';

import Room from './Room.js';
import TopBar from './TopBar.js';
import Fab from './Fab.js'
import './SideBar.css';

const useStyles = makeStyles(theme => ({
  roomList: {
    paddingTop: '10px'
  },
  sideBar: {
    backgroundColor: theme.palette.background.paper
  }
}));

export default function SideBar(props) {
  const classes = useStyles();

  const rooms = Object.values(props.rooms);
  return (
    <div className={`SideBar ${classes.sideBar}`}>
      <TopBar />
      <Divider />
      <List className={classes.roomList}>
        {rooms.map((room) => (
          <Room
          room={room}
          callback={props.selectCallback}
          selected={props.active===room.id}
          key={room.id}
          />
        ))}
      </List>
      <Fab />
    </div>
  )
}
