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


const useStyles = makeStyles(theme => ({
  root: {
    backgroundColor: theme.palette.background,
    color: 'white',
    order: 0,
    overflowY: 'auto',
    paddingLeft: '5px',
    paddingRight: '5px',
    paddingTop: '5px',
    '> ul': {
      listStyleType: 'none',
      padding: 0,
      margin: 0,
    }
  }
}));

export default function TopBar(props) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <IconButton centerRipple={false}>
        <MenuIcon />
      </IconButton>
    </div>
  );
}
