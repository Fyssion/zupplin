export const __prod__ = process.env.NODE_ENV === 'production';
export const apiBaseUrl = process.env.REACT_APP_PUBLIC_API_BASE_URL || 'https://zupplin.org/api/v1';
export const baseUrl = process.env.REACT_APP_PUBLIC_BASE_URL || 'https://web.zupplin.org';
export const wsUrl = process.env.REACT_APP_PUBLIC_WS_URL || 'wss://zupplin.org/api/v1/websocket/connect';
