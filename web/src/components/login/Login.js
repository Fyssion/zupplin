import React, { useState, useEffect } from 'react';

import TextField from '@material-ui/core/TextField';
import { Typography } from '@material-ui/core';
import { Slide } from '@material-ui/core';
import { makeStyles, withStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Button from '@material-ui/core/Button';

import {Redirect} from 'react-router-dom';

import api from '../../lib/api.ts';
import './Login.css';


const styles = theme => {
  const isDarkTheme = theme.palette.type == 'dark';
  const url = `../../img/${isDarkTheme ? 'login_dark' : 'login_light'}.svg`;
  const bgcolor = isDarkTheme ? 'black' : 'white';

  console.log(url);

  return {
    loginSubtitle: {
      color: theme.palette.text.secondary
    }
  }
};

const useStyles = makeStyles(styles);


function LoginForm(props) {
  const [hideContinue, setHideContinue] = useState(true);

  const isFilled = () => {
    const email = document.getElementById('Login-email').value;
    const password = document.getElementById('Login-password').value;

    return email.trim() && password.trim();
  }

  const handleChange = () => {
    setHideContinue(!isFilled());
  }

  let style = {};

  if (hideContinue) {
    style = {visibility: 'hidden'};
  }

  return (
    <form onSubmit={props.handleLogin}>
      <TextField
        required
        error={props.emailError !== null}
        helperText={props.emailError}
        variant="outlined"
        id="Login-email"
        type="email"
        name="email"
        label="Email"
        className="Login-textfield Login-email"
        onChange={handleChange}
      />
      <br />
      <TextField
        required
        error={props.passwordError !== null}
        helperText={props.passwordError}
        variant="outlined"
        id="Login-password"
        type="password"
        name="password"
        label="Password"
        className="Login-textfield Login-password"
        autoComplete="current-password"
        onChange={handleChange}
      />
      <br />
      <div className="Login-buttonwrapper">
        <Button
          onClick={props.handleLogin}
          id="login-submit"
          className="Login-button"
          color="primary"
          variant="contained"
          type="submit"
          style={style}
        >Continue</Button>
      </div>
      <div className="Login-buttonwrapper">
        <Button
          onClick={props.handleCreate}
          id="create-submit"
          className="Login-button"
          type="submit"
          variant="outlined"
          color="primary"
        >Create An Account</Button>
      </div>
    </form>
  );
}

function CreateForm(props) {
  return (
    <form onSubmit={props.handleSubmit}>
      <TextField
        required
        error={props.emailError !== null}
        helperText={props.emailError}
        variant="outlined"
        id="Login-email"
        type="email"
        name="email"
        label="Email"
        className="Login-textfield Login-email"
        defaultValue={props.email}
      />
      <br />
      <TextField
        required
        error={props.passwordError !== null}
        helperText={props.passwordError}
        variant="outlined"
        id="Login-password"
        type="password"
        name="password"
        label="Password"
        className="Login-textfield Login-email"
        autoComplete="current-password"
        defaultValue={props.password}
      />
      <TextField
        required
        error={props.nameError !== null}
        helperText={props.nameError}
        variant="outlined"
        id="Login-name"
        className="Login-textfield Login-password"
        type="text"
        name="name"
        label="Name"
      />
      <br />
      <Button
        onClick={props.handleSubmit}
        id="real-create-submit"
        className="Login-login"
        type="submit"
        className="Login-button"
        variant="contained"
        color="primary"
      >Continue</Button>
    </form>
  );
}

class Login extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      redirect: localStorage.getItem('token') !== null,
      title: 'Sign in to Zupplin',
      subtitle: 'Please enter your email and password.',
      create: false,
      email: null,
      password: null,
      emailError: null,
      passwordError: null,
      nameError: null,
      otherError: null,
    };
  }

  render() {
    const classes = this.props.classes

    if (this.state.redirect) {
      return (<Redirect to="/" />);
    }

    let errorClass = '';

    if (this.state.error === 'none') {
      errorClass = 'Login-noerror';
    } else {
      errorClass = 'Login-error';
    }

    let otherError = null;
    if (this.state.otherError) {
      otherError = <Typography varient="p" className={errorClass} >{this.state.error}</Typography>;
    }

    return (
      <Container maxWidth="xs" className="Login" id="LoginModal">
        <Typography variant="h4">{this.state.title}</Typography>
        <Typography variant="subtitle1" className={classes.loginSubtitle}>
          {this.state.subtitle}
        </Typography>
        {this.state.create
        ? <CreateForm
            handleSubmit={this.handleCreateSubmit}
            emailError={this.state.emailError}
            passwordError={this.state.passwordError}
            nameError={this.state.nameError}
            email={this.state.email}
            password={this.state.password}
          />
        : <LoginForm
            handleLogin={this.handleLogin}
            handleCreate={this.handleCreate}
            emailError={this.state.emailError}
            passwordError={this.state.passwordError}
          />}
        {otherError}
      </Container>
    );
  }

  handleLogin = event => {
    event.preventDefault();

    const { email, password } = this.getEmailPassword();

    if (!this.validateEmailPassword(email, password)) {
      return;
    }

    this.login(event, email, password);
  }

  handleCreate = event => {
    event.preventDefault();

    const { email, password } = this.getEmailPassword();

    this.setState({
      title: 'Create your account',
      subtitle: 'Please enter your email, a password, and a name.',
      create: true,
      email: email,
      password: password,
      emailError: null,
      passwordError: null,
      otherError: null
    });
  }

  getEmailPassword = () => {
    const email = document.getElementById('Login-email').value;
    const password = document.getElementById('Login-password').value;
    return { email, password };
  }

  validateEmail(email) {
    const re = /\S+@\S+\.\S+/;
    return re.test(email.toLowerCase());
}

  login = (event, email, password) => {
    api.post('/login', {
      email: email,
      password: password
    })
    .then ((response) => {
      localStorage.setItem('token', response.data['token']);
      this.props.login();
      this.setState({redirect: true});
    })
    .catch((error) => {
      if (error.response) {

        if (error.response.status == 401) {
          const err = 'Email or password is incorrect.';
          this.setErrorState({
            emailError: err,
            passwordError: err
          });
        }

        else if (error.response.status == 429) {
          this.setErrorState({otherError: 'You are doing that too much. Try again later.'});
        }

        else {
          this.setErrorState({
            otherError: `The server failed to respond properly. Try again later. Error ${error.response.status}`
          });
        }
      }

      else {
        this.setErrorState({otherError: 'A request could not be made. Try again later.'});
      }

    });
  }

  handleCreateSubmit = event => {
    event.preventDefault();

    const { email, password } = this.getEmailPassword();
    const name = document.getElementById('Login-name').value;

    if (!this.validateEmailPassword(email, password)) {
      return;
    }

    if (!name) {
      this.setErrorState({nameError: 'A name is required. It doesn\'t have to be your real name.'});
      return false;
    }

    console.log('creating account...');

    api.post('/accounts', {
      email: this.state.email,
      password: this.state.password,
      name: name
    })
    .then(response => {
      console.log(response);
      this.login(event, this.state.email, this.state.password);
    })
    .catch(error => {
      if (error.response) {

        if (error.response.status == 400) {
          this.setErrorState({
            emailError: 'That email is already in use.',
          });
        }

        else if (error.response.status == 429) {
          this.setErrorState({otherError: 'You are doing that too much. Try again later.'});
        }

        else {
          this.setErrorState({
            otherError: `The server failed to respond properly. Try again later. Error ${error.response.status}`
          });
        }
      }

      else {
        this.setErrorState({otherError: 'A request could not be made. Try again later.'});
      }
    })
  }

  validateEmailPassword = (email, password) => {
    if (!email) {
      this.setErrorState({emailError: 'An email is required.'});
      return false;
    }

    if (!password) {
      this.setErrorState({passwordError: 'A password is required.'});
      return false;
    }

    if (!this.validateEmail(email)) {
      this.setErrorState({emailError: 'That email is not valid.'});
      return false;
    }

    return true;
  }

  setErrorState = errors => {
    this.setState({
      emailError: errors.emailError || null,
      passwordError: errors.passwordError || null,
      nameError: errors.nameError || null,
      otherError: errors.otherError || null
    });
  }

}

export default withStyles(styles)(Login);
