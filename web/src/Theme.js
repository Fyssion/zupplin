import React from 'react';
import {
  createTheme,
  makeStyles,
  ThemeProvider,
  StylesProvider
} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';


function getPreferredColorScheme () {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function createMyTheme(type, primary) {
  const prefersDarkMode = getPreferredColorScheme();

  if (type === 'default') {
    type = prefersDarkMode ? 'dark' : 'light';
  }

  console.log('type', type);

  let MuiTouchRipple = {};
  let action = {};
  // if (!prefersDarkMode) {
  //   MuiTouchRipple = {
  //     child: {
  //       color: prefersDarkMode ? 'currentColor' : 'rgba(112, 117, 121)'
  //     },
  //     rippleVisible: {
  //       opacity: 0.08 //type === 'dark' ? 0.15 : 1
  //     },
  //     '@keyframes enter': {
  //       '0%': {
  //         transform: 'scale(0)',
  //         opacity: 0.03
  //       },
  //       '100%': {
  //         transform: 'scale(1)',
  //         opacity: 0.08 //type === 'dark' ? 0.15 : 1
  //       }
  //     }
  //   };
  //   action = {
  //     hover: 'rgba(112, 117, 121, 0.08)',
  //     hoverOpacity: 0.08
  //   };
  // }

  const theme = createTheme({
    palette: {
      type: type,
      // primary: primary,
      // secondary: { main: '#E53935' },
      action
    },
    typography: {
      useNextVariants: true
    },
    shape: {
      borderRadius: 10
    },
    overrides: {
      MuiOutlinedInput: {
        input: {
          padding: '17.5px 14px'
        }
      },
      MuiAutocomplete: {
        option: {
          paddingLeft: 0,
          paddingTop: 0,
          paddingRight: 0,
          paddingBottom: 0
        },
        paper: {
          '& > ul': {
            maxHeight: 56 * 5.5
          }
        }
      },
      MuiButton: {
        root: {
          padding: '12px 16px 11px',
          fontSize: 16,
          lineHeight: 'normal'
        }
      },
      MuiMenuList: {
        root: {
          minWidth: 150
        }
      },
      MuiList: {
        root: {
          minWidth: 150
        }
      },
      MuiListItemIcon: {
        root: {
          minWidth: 40
        },
        alignItemsFlexStart: {
          marginTop: 6
        }
      },
      // MuiListItemText: {
      //     root: {
      //         marginTop: 0,
      //         marginBottom: 0
      //     }
      // },
      MuiListItem: {
        button: {
          transition: null
        }
      },
      MuiMenuItem: {
        root: {
          paddingTop: 10,
          paddingBottom: 10
        }
      },
      MuiTouchRipple,
      MuiSnackbarContent: {
        root: {
          flexWrap: 'nowrap',
          fontSize: 'inherit'
        },
        message: {
          maxWidth: 512
        }
      },
      MuiSpeedDialIcon: {
        openIconOpen: {
          transform: 'rotate(45deg)'
        }
      }
    }
  });

  // if (type === 'dark') {
  //     updateDarkTheme(theme);
  // } else {
  //     updateLightTheme(theme);
  // }

  return theme;
}


function withTheme(WrappedComponent) {
  class ThemeWrapper extends React.Component {
    constructor(props) {
      super(props);

      let { type, primary } = { type: 'default', primary: { main: '#50A2E9' } };
      try {
        const themeOptions = JSON.parse(localStorage.getItem('themeOptions'));
        if (themeOptions) {
          type = themeOptions.type;
          primary = themeOptions.primary;
        }
      } catch {}
      const theme = createMyTheme(type, primary);
      console.log('theme', theme);

      this.state = { theme };
    }

    render() {
      return (
        <StylesProvider injectFirst={true}>
          <ThemeProvider theme={this.state.theme}>
            <CssBaseline />
            <WrappedComponent {...this.props} />
          </ThemeProvider>
        </StylesProvider>
      );
    }
  }
  // ThemeWrapper.displayName = `WithTheme(${getDisplayName(WrappedComponent)})`;

  return ThemeWrapper;
}

export default withTheme;
