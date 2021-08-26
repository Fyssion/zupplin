import React from 'react';
import logo from './logo.svg';
import './App.css';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from 'react-router-dom';

import withTheme from './Theme.js';
import Home from './components/Home';
import Login from './components/login/Login';


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {loggedIn: localStorage.getItem('token') !== null};
  }

  login = () => {
    this.setState({loggedIn: true});
  }

  logout = () => {
    this.setState({loggedIn: false});
  }

  render() {
    console.log('rendering app');
    return (
        <Router>
          <div className="App" id="App">
            <Switch>
              <Route path="/login">
                <Login login={this.login} />
              </Route>
              <Route path="/">
                {this.state.loggedIn ? <Home logout={this.logout}/> : <Redirect to="/login" />}
              </Route>
            </Switch>
          </div>
        </Router>
    );
  }
}

export default withTheme(App);
