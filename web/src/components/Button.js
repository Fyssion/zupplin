import React from 'react';

export default class Button extends React.Component {
  render() {
    return React.createElement(
      this.props.type,
      {
        className: this.props.className,
        onClick: this.handleClick
      },
      ...this.props.children
    );
    // return (
    //   <div
    //   className={this.props.className || ''}
    //   onClick={this.handleClick}>
    //     {this.props.children}
    //   </div>
    // );
  }

  handleClick = event => {
    this.props.onClick(event);
  }
}
