import React from 'react';

import './Input.css';

export default class Input extends React.Component {
  render() {
    const hasLabel = this.props.label !== null;
    return (
      <div className={this.props.divClassName || 'form-group'}>
        {hasLabel && <label htmlFor={this.props.id}>{this.props.label}</label>}
        <input
        className={this.props.className}
        type={this.props.type || 'text'}
        id={this.props.id}
        name={this.props.name}/>
      </div>
    );
  }

  handleClick = event => {
    this.props.onClick(event);
  }
}
