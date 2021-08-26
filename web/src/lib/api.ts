import axios from 'axios';

import { apiBaseUrl } from './constants';

const api = axios.create({
    baseURL: apiBaseUrl,
    headers: {
        'User-Agent': `ZupplinWeb/1.0 ${navigator.userAgent}`,
    }
});

export default api;
