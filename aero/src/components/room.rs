use crate::prelude::*;

#[inline_props]
pub fn Room(cx: Scope, room_id: models::ID) -> Element {
    let rooms = use_read(&cx, ROOMS);
    let room = rooms.get(room_id).unwrap();

    cx.render(rsx! (
        div {
            h1 { "{room.name}" }
            h3 { "This is a room." }
            p { "Its ID is {room.id}" }
        }
    ))
}
