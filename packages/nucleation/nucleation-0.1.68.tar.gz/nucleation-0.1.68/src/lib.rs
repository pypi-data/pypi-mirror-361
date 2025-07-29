// src/lib.rs

// Core modules
mod universal_schematic;
mod region;
mod block_state;
mod entity;
pub mod block_entity;
mod formats;
mod print_utils;
mod bounding_box;
mod metadata;
mod block_position;
pub mod utils;
mod item;
mod chunk;

// Feature-specific modules
#[cfg(feature = "wasm")]
mod wasm;
#[cfg(feature = "ffi")]
pub mod ffi;
#[cfg(feature = "python")]
mod python;
#[cfg(feature = "php")]
mod php;

// Public re-exports
pub use universal_schematic::UniversalSchematic;
pub use block_state::BlockState;
pub use region::Region;
pub use formats::{litematic, schematic};
pub use print_utils::{format_schematic, format_json_schematic};

// Re-export WASM types when building with WASM feature
#[cfg(feature = "wasm")]
pub use wasm::*;

// Re-export PHP types when building with PHP feature
#[cfg(feature = "php")]
pub use php::*;