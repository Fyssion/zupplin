use im_rc::HashMap;

use crate::{prelude::*, http::HttpClient};

pub static TOKEN: Atom<Option<String>> = |_| None;
pub static HTTP: Atom<Option<HttpClient>> = |_| None;

pub type RoomsState = HashMap<models::ID, models::Room>;
pub type MessagesState = HashMap<models::ID, HashMap<models::ID, models::Message>>;

pub static ME: Atom<Option<models::User>> = |_| None;
pub static ROOMS: Atom<RoomsState> = |_| HashMap::new();
pub static MESSAGES: Atom<MessagesState> = |_| HashMap::new();
