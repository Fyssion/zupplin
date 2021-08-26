import React from 'react';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import Avatar from '@material-ui/core/Avatar';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Link from '@material-ui/core/Link';
import { Link as RouterLink, useRouteMatch, useParams } from 'react-router-dom';


const useAvatarStyles = makeStyles({
  root: {
    order: 0,
  },
  colorDefault: {
    background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);',
    color: 'white'
  }
})

const useStyles = makeStyles(theme => ({
  root: {
    padding: '10px',
    borderRadius: '7px',
  },
  roomWrapper: {
    display: 'flex',
    width: '350px',
    paddingTop: '3px',
    paddingBottom: '3px'
  },
  roomInfo: {
    order: 1,
    flexGrow: 1,
    margin: 0
  },
  lastMessage: props => ({
    color: theme.palette.text.secondary,
    visibility: props.room.last_message ? 'visible' : 'hidden'  // hide message if there is none
  }),
  roomMessageDate: {
    color: theme.palette.text.secondary,
  }
}));


export default function Room(props) {
  const { path, url } = useRouteMatch();

  const avatarClasses = useAvatarStyles();
  const classes = useStyles(props);

  // first letter of each word
  const firstStep = props.room.name.split(/\s/);
  const acronym = firstStep.reduce((response, word) => response += word.slice(0, 1), '');
  const icon = acronym.slice(0, 2);

  // last digit of ID for avatar color
  // const avatarColor = avatarColors[props.room.id % 10]

  const message = {}

  if (props.room.last_message) {
    message.content = props.room.last_message.content
  }

  return (
    <Link component={RouterLink} to={`${url}room/${props.room.id}`} color="inherit" underline="none">
      <ListItem
      button
      selected={props.selected}
      className={classes.root}
      onMouseDown={() => {props.callback(props.room.id)}}
      >
        <div className={classes.roomWrapper}>
          <ListItemAvatar>
            <Avatar classes={avatarClasses} color="primary">{icon}</Avatar>
          </ListItemAvatar>
          <ListItemText className={classes.roomInfo}>
              <Typography className="room-title">
                <Typography component="span" className="room-name" noWrap>
                {props.room.name}
                </Typography>
                <Typography component="span" className={`room-message-date ${classes.roomMessageDate}`}>
                  Mon
                </Typography>
              </Typography>
              <Typography className="room-subtitle">
                <Typography varient="p" className={`last-message ${classes.lastMessage}`} noWrap>
                  { message.content || 'none'}
                </Typography>
              </Typography>
          </ListItemText>
        </div>
      </ListItem>
    </Link>
  )
}