## 0 · Enabling the crate

```toml
# Cargo.toml of your binary / library
[dependencies]
nucleation = { path = "../nucleation", default-features = false, features = ["serde"] }
#            └──────────────────────┘                      └───────────────┘
#      local checkout or git URL                 enable optional helpers you need
```

### Optional feature flags

| Feature   | What it adds                                                 |
| --------- | ------------------------------------------------------------ |
| `python`  | PyO3 bindings (`nucleation::python::nucleation(...)`)        |
| `wasm`    | `wasm-bindgen` Web-API wrappers (re-exported at crate root). |
| `ffi`     | C-ABI helpers in `nucleation::ffi`.                          |
| *no flag* | Pure-Rust core only.                                         |

---

## 1 · Public re-exports (always available)

| Item                    | Kind       | Why you’d use it                                                                                                                       |
| ----------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `UniversalSchematic`    | **struct** | The *central* data-structure: holds regions, blocks, entities, NBT, etc.                                                               |
| `BlockState`            | **struct** | Immutable description of a single block (`name` + `HashMap<String,String>` properties).                                                |
| `formats::litematic`    | **module** | Low-level encode/decode helpers `to_litematic(&UniversalSchematic) → Vec<u8>`, `from_litematic(&[u8]) → Result<UniversalSchematic,_>`. |
| `formats::schematic`    | **module** | Same for classic WorldEdit `.schematic` (NBT‐based).                                                                                   |
| `format_schematic`      | **fn**     | Pretty ASCII dump (fast text preview).                                                                                                 |
| `format_json_schematic` | **fn**     | JSON dump for logging / debugging.                                                                                                     |

> **Tip:** almost everything else (regions, entities, items, etc.) is reachable *through* `UniversalSchematic` methods, so you rarely import sub-modules directly.

---

## 2 · Zero-to-airship in 30 lines

```rust
use nucleation::{UniversalSchematic, BlockState, format_schematic};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1) create an empty schematic
    let mut sch = UniversalSchematic::new("Demo".into());

    // 2) place some blocks
    sch.set_block(0, 0, 0, BlockState::new("minecraft:stone".into()));
    sch.set_block_from_string(1, 0, 0,
        r#"minecraft:barrel[facing=up]{signal=13}"#)?;

    // 3) inspect
    println!("Blocks placed: {}", sch.total_blocks());
    println!("{}", format_schematic(&sch));

    // 4) save as .litematic
    std::fs::write("demo.litematic", nucleation::litematic::to_litematic(&sch)?)?;
    Ok(())
}
```

Key highlights you can call on `sch` (the `UniversalSchematic`):

```rust
sch.get_block(x,y,z)                  // Option<&BlockState>
sch.get_block_entity(pos)             // Option<&BlockEntity>
sch.copy_region(&src, &bounds, dest, &excluded)
sch.iter_blocks()                     // iterator of (BlockPosition, &BlockState)
sch.iter_chunks(w,h,l, Some(strategy))// ordered chunk iterator
sch.get_dimensions()                  // (x,y,z)
sch.total_blocks(); sch.total_volume();
```

---

## 3 · When you enable **`wasm`**

```rust
use nucleation::{SchematicWrapper};   // re-exported by lib.rs when feature=wasm
```

* Everything from the `wasm` module is surfaced at the crate root, so
  you can compile the same source for native and Web targets by hiding the import
  behind `#[cfg(target_arch = "wasm32")]`.

---

## 4 · When you enable **`ffi`**

```rust
use nucleation::ffi::{schematic_debug_info, print_debug_info};
```

* These are raw `extern "C"` helpers; the Rust wrapper is only needed if you call
  back *into* Rust from another Rust crate that links to the C ABI.

---

## 5 · When you enable **`python`**

Nothing special within Rust—the PyO3 glue code lives in
`nucleation::python` and compiles into a `*.so`/`*.pyd`.
The Rust side does **not** re-export those symbols to avoid name clashes.

---

## 6 · Design notes & gotchas

* **All mutation is via `&mut UniversalSchematic`**; most helper structs
  (`Region`, `BlockEntity`, `Entity`, etc.) expose their own methods but are
  *internal* unless you dive into the modules.
* **Barrel `{signal=n}` sugar**—`set_block_from_string` auto-generates the correct
  item stacks so a comparator reads the requested signal.
* **Deterministic randomness**—chunk loading strategy `"Random"` hashes the
  schematic name, so the order is stable across runs.

