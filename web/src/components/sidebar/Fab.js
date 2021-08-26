import React from 'react';
import { Fab as MuiFab } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import SpeedDial from '@material-ui/lab/SpeedDial';
import SpeedDialIcon from '@material-ui/lab/SpeedDialIcon';
import SpeedDialAction from '@material-ui/lab/SpeedDialAction';
import { makeStyles } from '@material-ui/core/styles';
import PersonAddIcon from '@material-ui/icons/PersonAdd';
import AddCommentIcon from '@material-ui/icons/AddComment';
import AddIcon from '@material-ui/icons/Add';


const useStyles = makeStyles(theme => ({
  root: {
    position: 'absolute',
    bottom: theme.spacing(2),
    right: theme.spacing(2)
  }
}));


const actions = [
  { icon: <PersonAddIcon />, name: 'Add friend' },
  { icon: <AddCommentIcon />, name: 'Create room' },
];


export default function Fab() {
    const classes = useStyles();
    const [open, setOpen] = React.useState(false);

    const handleOpen = (event, reason) => {
      // if (reason !== 'mouseEnter') {
      //   setOpen(true);
      // }
      setOpen(true);
    };

    const handleClose = () => {
      setOpen(false);
    };

    return (
      <SpeedDial
      ariaLabel="create-fab"
      className={classes.root}
      icon={<SpeedDialIcon icon={<EditIcon />} openIcon={<AddIcon />} />}
      onClose={handleClose}
      onOpen={handleOpen}
      open={open}
    >
      {actions.map((action) => (
        <SpeedDialAction
          key={action.name}
          icon={action.icon}
          tooltipTitle={action.name}
          tooltipOpen
          onClick={handleClose}
        />
      ))}
    </SpeedDial>
    );
  }
