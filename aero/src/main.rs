#![allow(non_snake_case)]

pub mod components;
pub mod http;
pub mod models;
pub mod state;
pub mod utils;

pub mod prelude {
    pub use dioxus::core::to_owned;
    pub use dioxus::prelude::*;
    pub use serde::{Serialize, Deserialize};
    pub use crate::state::*;
    pub use crate::models;
}

use gloo::storage::{LocalStorage, Storage};

use prelude::*;
use http::HttpClient;

// static API_VERSION: u8 = 1;
// pub static API_URL: &str = "https://zupplin.org/api/v1";
pub static API_URL: &str = "http://localhost:4000";

#[derive(Serialize)]
struct LoginRequest<'a> {
    pub email: &'a str,
    pub password: &'a str,
}

#[derive(Deserialize)]
struct LoginResponse {
    pub token: String
}

fn main() {
    // init debug tool for WebAssembly
    wasm_logger::init(wasm_logger::Config::default());
    console_error_panic_hook::set_once();

    dioxus::web::launch(app);
}

fn Home(cx: Scope) -> Element {
    let token = use_read(&cx, TOKEN);
    let rooms = use_read(&cx, ROOMS);

    if token.is_none() {
        return cx.render(rsx! (
            Redirect { to: "/login" }
        ))
    }

    let rooms_rendered = rooms.iter().map(|(room_id, _)| {
        cx.render(rsx!(components::Room {
            key: "{room_id}",
            room_id: room_id.clone(),
        }))
    });

    cx.render(rsx! (
        div {
            style: "text-align: center;",
            h1 { "🌗 Welcome Home! 🚀" }
            h3 { "Frontend that scales." }
            p { "Dioxus is a portable, performant, and ergonomic framework for building cross-platform user interfaces in Rust." }
            rooms_rendered
        }
    ))
}

fn Login(cx: Scope) -> Element {
    let token = use_read(&cx, TOKEN);
    let set_token = use_set(&cx, TOKEN);

    if token.is_some() {
        return cx.render(rsx! (
            Redirect { to: "/" }
        ))
    }

    cx.render(rsx! (
        div {
            style: "text-align: center;",
            h1 { "Where's your key?" }
            h3 { "This is the login page." }
            form {
                prevent_default: "onsubmit",
                onsubmit: move |event| {
                    let set_token = set_token.clone();
                    cx.spawn({
                        async move {
                            log::info!("Submitted! {event:?}");
                            let client = reqwest::Client::new();
                            let body = LoginRequest {
                                email: &event.values["email"],
                                password: &event.values["password"],
                            };
                            let token = client.post(format!("{API_URL}/login"))
                                .json(&body)
                                .send()
                                .await
                                .unwrap()
                                .json::<LoginResponse>()
                                .await
                                .unwrap()
                                .token;
                            LocalStorage::set("token", &token).ok();
                            set_token(Some(token));
                        }

                    })
                },
                div {
                    span { "Email" },
                    input { name: "email", r#type: "email", placeholder: "Email" },
                },
                div {
                    span { "Password" },
                    input { name: "password", r#type: "password", placeholder: "Password" },
                }
                div {
                    input { r#type: "submit", },
                }
            }
        }
    ))
}

fn app(cx: Scope) -> Element {
    let token = use_read(&cx, TOKEN);
    let set_token = use_set(&cx, TOKEN);
    let http = use_read(&cx, HTTP);
    let set_http = use_set(&cx, HTTP);
    let set_me = use_set(&cx, ME);
    let rooms = use_read(&cx, ROOMS);
    let set_rooms = use_set(&cx, ROOMS);
    let messages = use_read(&cx, MESSAGES);
    let set_messages = use_set(&cx, MESSAGES);

    cx.use_hook(|_| {
        log::info!("Test");
        let token = LocalStorage::get::<String>("token").ok();
        set_token(token);
    });

    if token.is_some() && http.is_none() {
        to_owned![token, set_me, rooms, set_rooms, messages, set_messages];

        let http = HttpClient::new(token.as_ref().unwrap().clone());
        set_http(Some(http.clone()));

        cx.spawn(async move {
            let me_result = http.get(format!("{API_URL}/users/me")).send().await.unwrap().json::<models::MeResponse>().await.unwrap();
            let me = Some(me_result.user);
            set_me.clone()(me.clone());

            let mut rooms = rooms.clone();
            me_result.rooms.iter().for_each(|(room_id, room)| {
                rooms.insert(room_id.clone(), room.clone());
            });
            set_rooms.clone()(rooms.clone());

            utils::websocket(
                token.as_ref().unwrap().clone(),
                me.clone(),
                set_me.clone(),
                rooms.clone(),
                set_rooms.clone(),
                messages.clone(),
                set_messages.clone(),
            ).await;
        });
    }

    log::info!("Test3");

    cx.render(rsx! (
        Router {
            Route { to: "/", Home {} },
            Route { to: "/login", Login {} },
        }
    ))
}
