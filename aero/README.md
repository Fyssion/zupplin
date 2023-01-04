# zupplin - aero

![deploy](https://github.com/Fyssion/zupplin/actions/workflows/aero_deploy.yml/badge.svg)

This is the frontend client for zupplin, written in [Rust](https://www.rust-lang.org/) using [Dioxus](https://dioxuslabs.com/)
and compiled to [Wasm](https://webassembly.org/).

## Why Rust, Dioxus, and WebAssembly?

JS frameworks were getting a bit stale to me, and Dioxus seemed like a nice change of pace.
Yes, Dioxus is similar to React, but I also wanted to further my Rust skills and do something interesting.  
Also it's [fast](https://dioxuslabs.com/blog/templates-diffing/).

## Running

```sh
# Install Wasm target
rustup target add wasm32-unknown-unknown

# Install Dioxus CLI
cargo install --git https://github.com/DioxusLabs/cli

# Serve the app
dioxus serve

# Or build the app
dioxus build --release
```
