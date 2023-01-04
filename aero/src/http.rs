use reqwest;

#[derive(Clone)]
pub struct HttpClient {
    client: reqwest::Client,
    token: String,
}

impl HttpClient {
    pub fn new(token: String) -> Self {
        Self { client: reqwest::Client::new(), token }
    }

    pub fn request<U: reqwest::IntoUrl>(self, method: reqwest::Method, url: U) -> reqwest::RequestBuilder {
        self.client.request(method, url).bearer_auth(self.token)
    }

    pub fn get<U: reqwest::IntoUrl>(self, url: U) -> reqwest::RequestBuilder {
        self.request(reqwest::Method::GET, url)
    }

    pub fn post<U: reqwest::IntoUrl>(self, url: U) -> reqwest::RequestBuilder {
        self.request(reqwest::Method::POST, url)
    }
}
