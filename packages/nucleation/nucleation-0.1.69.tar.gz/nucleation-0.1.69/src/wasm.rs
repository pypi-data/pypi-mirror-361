// src/wasm.rs

use wasm_bindgen::prelude::*;
use js_sys::{self, Array, Object, Reflect};
use web_sys::console;
use crate::{
    UniversalSchematic,
    BlockState,
    formats::{litematic, schematic},
    print_utils::{format_schematic as print_schematic, format_json_schematic as print_json_schematic},
    block_position::BlockPosition,
};
use std::collections::HashMap;
use crate::bounding_box::BoundingBox;
use crate::schematic::SchematicVersion;
use crate::universal_schematic::ChunkLoadingStrategy;

#[wasm_bindgen]
pub struct LazyChunkIterator {
    // Iterator state - doesn't store all chunks, just iteration parameters
    schematic_wrapper: SchematicWrapper,
    chunk_width: i32,
    chunk_height: i32,
    chunk_length: i32,

    // Current iteration state
    current_chunk_coords: Vec<(i32, i32, i32)>, // Just the coordinates, not the data
    current_index: usize,
}


#[wasm_bindgen(start)]
pub fn start() {
    console::log_1(&"Initializing schematic utilities".into());
}

// Wrapper structs
#[wasm_bindgen]
pub struct SchematicWrapper(pub(crate) UniversalSchematic);


#[wasm_bindgen]
pub struct BlockStateWrapper(pub(crate) BlockState);

// All your existing WASM implementations go here...
#[wasm_bindgen]
impl SchematicWrapper {

    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        SchematicWrapper(UniversalSchematic::new("Default".to_string()))
    }



    pub fn from_data(&mut self, data: &[u8]) -> Result<(), JsValue> {
        if litematic::is_litematic(data) {
            console::log_1(&"Parsing litematic data".into());
            self.from_litematic(data)
        } else if schematic::is_schematic(data) {
            console::log_1(&"Parsing schematic data".into());
            self.from_schematic(data)
        } else {
            Err(JsValue::from_str("Unknown or unsupported schematic format"))
        }
    }

    pub fn from_litematic(&mut self, data: &[u8]) -> Result<(), JsValue> {
        self.0 = litematic::from_litematic(data)
            .map_err(|e| JsValue::from_str(&format!("Litematic parsing error: {}", e)))?;
        Ok(())
    }

    pub fn to_litematic(&self) -> Result<Vec<u8>, JsValue> {
        litematic::to_litematic(&self.0)
            .map_err(|e| JsValue::from_str(&format!("Litematic conversion error: {}", e)))
    }

    pub fn from_schematic(&mut self, data: &[u8]) -> Result<(), JsValue> {
        self.0 = schematic::from_schematic(data)
            .map_err(|e| JsValue::from_str(&format!("Schematic parsing error: {}", e)))?;
        Ok(())
    }

    pub fn to_schematic(&self) -> Result<Vec<u8>, JsValue> {
        schematic::to_schematic(&self.0)
            .map_err(|e| JsValue::from_str(&format!("Schematic conversion error: {}", e)))
    }

    pub fn to_schematic_version(&self, version: &str) -> Result<Vec<u8>, JsValue> {
       let version =  schematic::to_schematic_version(&self.0, SchematicVersion::from_str(version).unwrap());
        match version {
            Ok(data) => Ok(data),
            Err(e) => Err(JsValue::from_str(&format!("Schematic version conversion error: {}", e)))
        }
    }


    pub fn get_available_schematic_versions(&self) -> Array {
        let versions = SchematicVersion::get_all();
        let js_versions = Array::new();
        for version in versions {
            js_versions.push(&JsValue::from_str(&version.to_string()));
        }
        js_versions
    }

    pub fn get_palette(&self) -> JsValue {
        let merged_region = self.0.get_merged_region();
        let palette = &merged_region.palette;

        let js_palette = Array::new();
        for block_state in palette {
            let obj = Object::new();
            Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block_state.name)).unwrap();

            let properties = Object::new();
            for (key, value) in &block_state.properties {
                Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
            }
            Reflect::set(&obj, &"properties".into(), &properties).unwrap();

            js_palette.push(&obj);
        }
        js_palette.into()
    }

    pub fn get_palette_from_region(&self, region_name: &str) -> JsValue {
        let palette = if region_name == "default" || region_name == "Default" {
            &self.0.default_region.palette
        } else {
            match self.0.other_regions.get(region_name) {
                Some(region) => &region.palette,
                None => return JsValue::NULL, // Region not found
            }
        };

        let js_palette = Array::new();
        for block_state in palette {
            let obj = Object::new();
            Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block_state.name)).unwrap();

            let properties = Object::new();
            for (key, value) in &block_state.properties {
                Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
            }
            Reflect::set(&obj, &"properties".into(), &properties).unwrap();

            js_palette.push(&obj);
        }
        js_palette.into()
    }

    pub fn get_bounding_box(&self) -> JsValue {
        let bbox = self.0.get_bounding_box();
        let obj = Object::new();
        Reflect::set(&obj, &"min".into(), &Array::of3(
            &JsValue::from(bbox.min.0),
            &JsValue::from(bbox.min.1),
            &JsValue::from(bbox.min.2)
        )).unwrap();
        Reflect::set(&obj, &"max".into(), &Array::of3(
            &JsValue::from(bbox.max.0),
            &JsValue::from(bbox.max.1),
            &JsValue::from(bbox.max.2)
        )).unwrap();
        obj.into()
    }

    pub fn get_region_bounding_box(&self, region_name: &str) -> JsValue {
        let bbox = if region_name == "default" || region_name == "Default" {
            self.0.default_region.get_bounding_box()
        } else {
            match self.0.other_regions.get(region_name) {
                Some(region) => region.get_bounding_box(),
                None => return JsValue::NULL, // Region not found
            }
        };

        let obj = Object::new();
        Reflect::set(&obj, &"min".into(), &Array::of3(
            &JsValue::from(bbox.min.0),
            &JsValue::from(bbox.min.1),
            &JsValue::from(bbox.min.2)
        )).unwrap();
        Reflect::set(&obj, &"max".into(), &Array::of3(
            &JsValue::from(bbox.max.0),
            &JsValue::from(bbox.max.1),
            &JsValue::from(bbox.max.2)
        )).unwrap();
        obj.into()
    }



    pub fn set_block(&mut self, x: i32, y: i32, z: i32, block_name: &str) {
        self.0.set_block_str(x, y, z, block_name);
    }


    pub fn copy_region(
        &mut self,
        from_schematic: &SchematicWrapper,
        min_x: i32,
        min_y: i32,
        min_z: i32,
        max_x: i32,
        max_y: i32,
        max_z: i32,
        target_x: i32,
        target_y: i32,
        target_z: i32,
        excluded_blocks: &JsValue,
    ) -> Result<(), JsValue> {
        let bounds = BoundingBox::new(
            (min_x, min_y, min_z),
            (max_x, max_y, max_z)
        );

        let excluded_blocks = if !excluded_blocks.is_undefined() && !excluded_blocks.is_null() {
            let js_array: Array = excluded_blocks.clone().dyn_into().map_err(|_| {
                JsValue::from_str("Excluded blocks should be an array")
            })?;
            let mut rust_vec: Vec<BlockState> = Vec::new();
            for i in 0..js_array.length() {
                let block_string = match js_array.get(i).as_string() {
                    Some(name) => name,
                    None => return Err(JsValue::from_str("Excluded blocks should be strings"))
                };
                let (block_state, _) = UniversalSchematic::parse_block_string(&block_string)
                    .map_err(|e| JsValue::from_str(&format!("Invalid block state: {}", e)))?;
                rust_vec.push(block_state);
            }

            rust_vec
        } else {
            Vec::new()  // Return empty vec instead of None
        };

        self.0.copy_region(
            &from_schematic.0,
            &bounds,
            (target_x, target_y, target_z),
            &excluded_blocks  // Now we can pass a direct reference to the Vec
        ).map_err(|e| JsValue::from_str(&format!("Failed to copy region: {}", e)))
    }



    pub fn set_block_with_properties(
        &mut self,
        x: i32,
        y: i32,
        z: i32,
        block_name: &str,
        properties: &JsValue,
    ) -> Result<(), JsValue> {
        // Convert JsValue to HashMap<String, String>
        let mut props = HashMap::new();

        if !properties.is_undefined() && !properties.is_null() {
            let obj: Object = properties.clone().dyn_into().map_err(|_| {
                JsValue::from_str("Properties should be an object")
            })?;

            let keys = js_sys::Object::keys(&obj);
            for i in 0..keys.length() {
                let key = keys.get(i);
                let key_str = key.as_string().ok_or_else(|| {
                    JsValue::from_str("Property keys should be strings")
                })?;

                let value = Reflect::get(&obj, &key).map_err(|_| {
                    JsValue::from_str("Error getting property value")
                })?;

                let value_str = value.as_string().ok_or_else(|| {
                    JsValue::from_str("Property values should be strings")
                })?;

                props.insert(key_str, value_str);
            }
        }

        // Create BlockState with properties
        let block_state = BlockState {
            name: block_name.to_string(),
            properties: props,
        };

        // Set the block in the schematic
        self.0.set_block(x, y, z, block_state);

        Ok(())
    }


    pub fn get_block(&self, x: i32, y: i32, z: i32) -> Option<String> {
        self.0.get_block(x, y, z).map(|block_state| block_state.name.clone())
    }

    pub fn get_block_with_properties(&self, x: i32, y: i32, z: i32) -> Option<BlockStateWrapper> {
        self.0.get_block(x, y, z).cloned().map(BlockStateWrapper)
    }

    pub fn get_block_entity(&self, x: i32, y: i32, z: i32) -> JsValue {
        let block_position = BlockPosition { x, y, z };
        if let Some(block_entity) = self.0.get_block_entity(block_position) {
            if block_entity.id.contains("chest") {
                let obj = Object::new();
                Reflect::set(&obj, &"id".into(), &JsValue::from_str(&block_entity.id)).unwrap();

                let position = Array::new();
                position.push(&JsValue::from(block_entity.position.0));
                position.push(&JsValue::from(block_entity.position.1));
                position.push(&JsValue::from(block_entity.position.2));
                Reflect::set(&obj, &"position".into(), &position).unwrap();

                // Use the new to_js_value method
                Reflect::set(&obj, &"nbt".into(), &block_entity.nbt.to_js_value()).unwrap();

                obj.into()
            } else {
                JsValue::NULL
            }
        } else {
            JsValue::NULL
        }
    }

    pub fn get_all_block_entities(&self) -> JsValue {
        let block_entities = self.0.get_block_entities_as_list();
        let js_block_entities = Array::new();
        for block_entity in block_entities {
            let obj = Object::new();
            Reflect::set(&obj, &"id".into(), &JsValue::from_str(&block_entity.id)).unwrap();

            let position = Array::new();
            position.push(&JsValue::from(block_entity.position.0));
            position.push(&JsValue::from(block_entity.position.1));
            position.push(&JsValue::from(block_entity.position.2));
            Reflect::set(&obj, &"position".into(), &position).unwrap();

            // Use the new to_js_value method
            Reflect::set(&obj, &"nbt".into(), &block_entity.nbt.to_js_value()).unwrap();

            js_block_entities.push(&obj);
        }
        js_block_entities.into()
    }


    pub fn print_schematic(&self) -> String {
        print_schematic(&self.0)
    }

    pub fn debug_info(&self) -> String {
        format!("Schematic name: {}, Regions: {}",
                self.0.metadata.name.as_ref().unwrap_or(&"Unnamed".to_string()),
                self.0.other_regions.len() + 1
        )
    }


    // Add these methods back
    pub fn get_dimensions(&self) -> Vec<i32> {
        let (x, y, z) = self.0.get_dimensions();
        vec![x, y, z]
    }

    pub fn get_block_count(&self) -> i32 {
        self.0.total_blocks()
    }

    pub fn get_volume(&self) -> i32 {
        self.0.total_volume()
    }

    pub fn get_region_names(&self) -> Vec<String> {
        self.0.get_region_names()
    }

    pub fn blocks(&self) -> Array {
        self.0.iter_blocks()
            .map(|(pos, block)| {
                let obj = js_sys::Object::new();
                js_sys::Reflect::set(&obj, &"x".into(), &pos.x.into()).unwrap();
                js_sys::Reflect::set(&obj, &"y".into(), &pos.y.into()).unwrap();
                js_sys::Reflect::set(&obj, &"z".into(), &pos.z.into()).unwrap();
                js_sys::Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block.name)).unwrap();
                let properties = js_sys::Object::new();
                for (key, value) in &block.properties {
                    js_sys::Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
                }
                js_sys::Reflect::set(&obj, &"properties".into(), &properties).unwrap();
                obj
            })
            .collect::<Array>()
    }

    pub fn chunks(&self, chunk_width: i32, chunk_height: i32, chunk_length: i32) -> Array {
        self.0.iter_chunks(chunk_width, chunk_height, chunk_length, Some(ChunkLoadingStrategy::BottomUp))
            .map(|chunk| {
                let chunk_obj = js_sys::Object::new();
                js_sys::Reflect::set(&chunk_obj, &"chunk_x".into(), &chunk.chunk_x.into()).unwrap();
                js_sys::Reflect::set(&chunk_obj, &"chunk_y".into(), &chunk.chunk_y.into()).unwrap();
                js_sys::Reflect::set(&chunk_obj, &"chunk_z".into(), &chunk.chunk_z.into()).unwrap();

                let blocks_array = chunk.positions.into_iter()
                    .map(|pos| {
                        let block = self.0.get_block(pos.x, pos.y, pos.z).unwrap();
                        let obj = js_sys::Object::new();
                        js_sys::Reflect::set(&obj, &"x".into(), &pos.x.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"y".into(), &pos.y.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"z".into(), &pos.z.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block.name)).unwrap();
                        let properties = js_sys::Object::new();
                        for (key, value) in &block.properties {
                            js_sys::Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
                        }
                        js_sys::Reflect::set(&obj, &"properties".into(), &properties).unwrap();
                        obj
                    })
                    .collect::<Array>();

                js_sys::Reflect::set(&chunk_obj, &"blocks".into(), &blocks_array).unwrap();
                chunk_obj
            })
            .collect::<Array>()
    }

    pub fn chunks_with_strategy(
        &self,
        chunk_width: i32,
        chunk_height: i32,
        chunk_length: i32,
        strategy: &str,
        camera_x: f32,
        camera_y: f32,
        camera_z: f32
    ) -> Array {
        // Map the string strategy to enum
        let strategy_enum = match strategy {
            "distance_to_camera" => Some(ChunkLoadingStrategy::DistanceToCamera(camera_x, camera_y, camera_z)),
            "top_down" => Some(ChunkLoadingStrategy::TopDown),
            "bottom_up" => Some(ChunkLoadingStrategy::BottomUp),
            "center_outward" => Some(ChunkLoadingStrategy::CenterOutward),
            "random" => Some(ChunkLoadingStrategy::Random),
            _ => None // Default
        };

        // Use the enhanced iter_chunks method
        self.0.iter_chunks(chunk_width, chunk_height, chunk_length, strategy_enum)
            .map(|chunk| {
                let chunk_obj = js_sys::Object::new();
                js_sys::Reflect::set(&chunk_obj, &"chunk_x".into(), &chunk.chunk_x.into()).unwrap();
                js_sys::Reflect::set(&chunk_obj, &"chunk_y".into(), &chunk.chunk_y.into()).unwrap();
                js_sys::Reflect::set(&chunk_obj, &"chunk_z".into(), &chunk.chunk_z.into()).unwrap();

                let blocks_array = chunk.positions.into_iter()
                    .map(|pos| {
                        let block = self.0.get_block(pos.x, pos.y, pos.z).unwrap();
                        let obj = js_sys::Object::new();
                        js_sys::Reflect::set(&obj, &"x".into(), &pos.x.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"y".into(), &pos.y.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"z".into(), &pos.z.into()).unwrap();
                        js_sys::Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block.name)).unwrap();
                        let properties = js_sys::Object::new();
                        for (key, value) in &block.properties {
                            js_sys::Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
                        }
                        js_sys::Reflect::set(&obj, &"properties".into(), &properties).unwrap();
                        obj
                    })
                    .collect::<Array>();

                js_sys::Reflect::set(&chunk_obj, &"blocks".into(), &blocks_array).unwrap();
                chunk_obj
            })
            .collect::<Array>()
    }


    pub fn get_chunk_blocks(&self, offset_x: i32, offset_y: i32, offset_z: i32, width: i32, height: i32, length: i32) -> js_sys::Array {
        let blocks = self.0.iter_blocks()
            .filter(|(pos, _)| {
                pos.x >= offset_x && pos.x < offset_x + width &&
                    pos.y >= offset_y && pos.y < offset_y + height &&
                    pos.z >= offset_z && pos.z < offset_z + length
            })
            .map(|(pos, block)| {
                let obj = js_sys::Object::new();
                js_sys::Reflect::set(&obj, &"x".into(), &pos.x.into()).unwrap();
                js_sys::Reflect::set(&obj, &"y".into(), &pos.y.into()).unwrap();
                js_sys::Reflect::set(&obj, &"z".into(), &pos.z.into()).unwrap();
                js_sys::Reflect::set(&obj, &"name".into(), &JsValue::from_str(&block.name)).unwrap();
                let properties = js_sys::Object::new();
                for (key, value) in &block.properties {
                    js_sys::Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
                }
                js_sys::Reflect::set(&obj, &"properties".into(), &properties).unwrap();
                obj
            })
            .collect::<js_sys::Array>();

        blocks
    }


    /// Get all palettes once - eliminates repeated string transfers
    /// Returns: { default: [BlockState], regions: { regionName: [BlockState] } }
    pub fn get_all_palettes(&self) -> JsValue {
        let all_palettes = self.0.get_all_palettes();

        let js_object = Object::new();

        // Convert default palette
        let default_palette = Array::new();
        for block_state in &all_palettes.default_palette {
            let block_obj = Object::new();
            Reflect::set(&block_obj, &"name".into(), &JsValue::from_str(&block_state.name)).unwrap();

            let properties = Object::new();
            for (key, value) in &block_state.properties {
                Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
            }
            Reflect::set(&block_obj, &"properties".into(), &properties).unwrap();
            default_palette.push(&block_obj);
        }
        Reflect::set(&js_object, &"default".into(), &default_palette).unwrap();

        // Convert region palettes
        let regions_obj = Object::new();
        for (region_name, palette) in &all_palettes.region_palettes {
            let region_palette = Array::new();
            for block_state in palette {
                let block_obj = Object::new();
                Reflect::set(&block_obj, &"name".into(), &JsValue::from_str(&block_state.name)).unwrap();

                let properties = Object::new();
                for (key, value) in &block_state.properties {
                    Reflect::set(&properties, &JsValue::from_str(key), &JsValue::from_str(value)).unwrap();
                }
                Reflect::set(&block_obj, &"properties".into(), &properties).unwrap();
                region_palette.push(&block_obj);
            }
            Reflect::set(&regions_obj, &JsValue::from_str(region_name), &region_palette).unwrap();
        }
        Reflect::set(&js_object, &"regions".into(), &regions_obj).unwrap();

        js_object.into()
    }

    /// Optimized chunks iterator that returns palette indices instead of full block data
    /// Returns array of: { chunk_x, chunk_y, chunk_z, blocks: [[x,y,z,palette_index],...] }
    pub fn chunks_indices(
        &self,
        chunk_width: i32,
        chunk_height: i32,
        chunk_length: i32
    ) -> Array {
        self.0.iter_chunks_indices(chunk_width, chunk_height, chunk_length, Some(ChunkLoadingStrategy::BottomUp))
            .map(|chunk| {
                let chunk_obj = Object::new();
                Reflect::set(&chunk_obj, &"chunk_x".into(), &chunk.chunk_x.into()).unwrap();
                Reflect::set(&chunk_obj, &"chunk_y".into(), &chunk.chunk_y.into()).unwrap();
                Reflect::set(&chunk_obj, &"chunk_z".into(), &chunk.chunk_z.into()).unwrap();

                // Pack blocks as array of [x, y, z, palette_index] for minimal data transfer
                let blocks_array = Array::new();
                for (pos, palette_index) in chunk.blocks {
                    let block_data = Array::new();
                    block_data.push(&pos.x.into());
                    block_data.push(&pos.y.into());
                    block_data.push(&pos.z.into());
                    block_data.push(&(palette_index as u32).into());
                    blocks_array.push(&block_data);
                }

                Reflect::set(&chunk_obj, &"blocks".into(), &blocks_array).unwrap();
                chunk_obj
            })
            .collect::<Array>()
    }

    /// Optimized chunks with strategy - returns palette indices
    pub fn chunks_indices_with_strategy(
        &self,
        chunk_width: i32,
        chunk_height: i32,
        chunk_length: i32,
        strategy: &str,
        camera_x: f32,
        camera_y: f32,
        camera_z: f32
    ) -> Array {
        let strategy_enum = match strategy {
            "distance_to_camera" => Some(ChunkLoadingStrategy::DistanceToCamera(camera_x, camera_y, camera_z)),
            "top_down" => Some(ChunkLoadingStrategy::TopDown),
            "bottom_up" => Some(ChunkLoadingStrategy::BottomUp),
            "center_outward" => Some(ChunkLoadingStrategy::CenterOutward),
            "random" => Some(ChunkLoadingStrategy::Random),
            _ => None
        };

        self.0.iter_chunks_indices(chunk_width, chunk_height, chunk_length, strategy_enum)
            .map(|chunk| {
                let chunk_obj = Object::new();
                Reflect::set(&chunk_obj, &"chunk_x".into(), &chunk.chunk_x.into()).unwrap();
                Reflect::set(&chunk_obj, &"chunk_y".into(), &chunk.chunk_y.into()).unwrap();
                Reflect::set(&chunk_obj, &"chunk_z".into(), &chunk.chunk_z.into()).unwrap();

                let blocks_array = Array::new();
                for (pos, palette_index) in chunk.blocks {
                    let block_data = Array::new();
                    block_data.push(&pos.x.into());
                    block_data.push(&pos.y.into());
                    block_data.push(&pos.z.into());
                    block_data.push(&(palette_index as u32).into());
                    blocks_array.push(&block_data);
                }

                Reflect::set(&chunk_obj, &"blocks".into(), &blocks_array).unwrap();
                chunk_obj
            })
            .collect::<Array>()
    }

    /// Get specific chunk blocks as palette indices (for lazy loading individual chunks)
    /// Returns array of [x, y, z, palette_index]
    pub fn get_chunk_blocks_indices(
        &self,
        offset_x: i32,
        offset_y: i32,
        offset_z: i32,
        width: i32,
        height: i32,
        length: i32
    ) -> Array {
        let blocks = self.0.get_chunk_blocks_indices(offset_x, offset_y, offset_z, width, height, length);

        let blocks_array = Array::new();
        for (pos, palette_index) in blocks {
            let block_data = Array::new();
            block_data.push(&pos.x.into());
            block_data.push(&pos.y.into());
            block_data.push(&pos.z.into());
            block_data.push(&(palette_index as u32).into());
            blocks_array.push(&block_data);
        }

        blocks_array
    }

    /// All blocks as palette indices - for when you need everything at once but efficiently
    /// Returns array of [x, y, z, palette_index]
    pub fn blocks_indices(&self) -> Array {
        self.0.iter_blocks_indices()
            .map(|(pos, palette_index)| {
                let block_data = Array::new();
                block_data.push(&pos.x.into());
                block_data.push(&pos.y.into());
                block_data.push(&pos.z.into());
                block_data.push(&(palette_index as u32).into());
                block_data
            })
            .collect::<Array>()
    }



    /// Get optimization stats
    pub fn get_optimization_info(&self) -> JsValue {
        let default_region = &self.0.default_region;
        let total_blocks = default_region.blocks.len();
        let non_air_blocks = default_region.blocks.iter().filter(|&&idx| idx != 0).count();
        let palette_size = default_region.palette.len();

        let info_obj = Object::new();
        Reflect::set(&info_obj, &"total_blocks".into(), &(total_blocks as u32).into()).unwrap();
        Reflect::set(&info_obj, &"non_air_blocks".into(), &(non_air_blocks as u32).into()).unwrap();
        Reflect::set(&info_obj, &"palette_size".into(), &(palette_size as u32).into()).unwrap();
        Reflect::set(&info_obj, &"compression_ratio".into(), &((total_blocks as f64) / (palette_size as f64)).into()).unwrap();

        info_obj.into()
    }

    pub fn create_lazy_chunk_iterator(
        &self,
        chunk_width: i32,
        chunk_height: i32,
        chunk_length: i32,
        strategy: &str,
        camera_x: f32,
        camera_y: f32,
        camera_z: f32
    ) -> LazyChunkIterator {
        let mut chunk_coords = self.calculate_chunk_coordinates(chunk_width, chunk_height, chunk_length);

        // Sort coordinates by strategy
        match strategy {
            "distance_to_camera" => {
                chunk_coords.sort_by(|a, b| {
                    let a_center_x = (a.0 * chunk_width) as f32 + (chunk_width as f32 / 2.0);
                    let a_center_y = (a.1 * chunk_height) as f32 + (chunk_height as f32 / 2.0);
                    let a_center_z = (a.2 * chunk_length) as f32 + (chunk_length as f32 / 2.0);

                    let b_center_x = (b.0 * chunk_width) as f32 + (chunk_width as f32 / 2.0);
                    let b_center_y = (b.1 * chunk_height) as f32 + (chunk_height as f32 / 2.0);
                    let b_center_z = (b.2 * chunk_length) as f32 + (chunk_length as f32 / 2.0);

                    let a_dist = (a_center_x - camera_x).powi(2) + (a_center_y - camera_y).powi(2) + (a_center_z - camera_z).powi(2);
                    let b_dist = (b_center_x - camera_x).powi(2) + (b_center_y - camera_y).powi(2) + (b_center_z - camera_z).powi(2);

                    a_dist.partial_cmp(&b_dist).unwrap_or(std::cmp::Ordering::Equal)
                });
            }
            "bottom_up" => {
                chunk_coords.sort_by(|a, b| a.1.cmp(&b.1));
            }
            _ => {} // Default order
        }

        LazyChunkIterator {
            schematic_wrapper: self.clone(),
            chunk_width,
            chunk_height,
            chunk_length,
            current_chunk_coords: chunk_coords,
            current_index: 0,
        }
    }

    fn calculate_chunk_coordinates(&self, chunk_width: i32, chunk_height: i32, chunk_length: i32) -> Vec<(i32, i32, i32)> {
        use std::collections::HashSet;
        let mut chunk_coords = HashSet::new();
        let bbox = self.0.get_bounding_box();

        let get_chunk_coord = |pos: i32, chunk_size: i32| -> i32 {
            let offset = if pos < 0 { chunk_size - 1 } else { 0 };
            (pos - offset) / chunk_size
        };

        for x in bbox.min.0..=bbox.max.0 {
            for y in bbox.min.1..=bbox.max.1 {
                for z in bbox.min.2..=bbox.max.2 {
                    if self.0.get_block(x, y, z).is_some() {
                        let chunk_x = get_chunk_coord(x, chunk_width);
                        let chunk_y = get_chunk_coord(y, chunk_height);
                        let chunk_z = get_chunk_coord(z, chunk_length);
                        chunk_coords.insert((chunk_x, chunk_y, chunk_z));
                    }
                }
            }
        }

        chunk_coords.into_iter().collect()
    }

}

impl Clone for SchematicWrapper {
    fn clone(&self) -> Self {
        SchematicWrapper(self.0.clone())
    }
}
#[wasm_bindgen]
impl LazyChunkIterator {
    /// Get the next chunk on-demand (generates it fresh, doesn't store it)
    pub fn next(&mut self) -> JsValue {
        if self.current_index >= self.current_chunk_coords.len() {
            return JsValue::NULL;
        }

        let (chunk_x, chunk_y, chunk_z) = self.current_chunk_coords[self.current_index];
        self.current_index += 1;

        // Calculate chunk bounds
        let min_x = chunk_x * self.chunk_width;
        let min_y = chunk_y * self.chunk_height;
        let min_z = chunk_z * self.chunk_length;

        // Generate this chunk's data on-demand (only in memory temporarily)
        let blocks = self.schematic_wrapper.get_chunk_blocks_indices(
            min_x, min_y, min_z,
            self.chunk_width, self.chunk_height, self.chunk_length
        );

        // Create result object
        let chunk_obj = Object::new();
        Reflect::set(&chunk_obj, &"chunk_x".into(), &chunk_x.into()).unwrap();
        Reflect::set(&chunk_obj, &"chunk_y".into(), &chunk_y.into()).unwrap();
        Reflect::set(&chunk_obj, &"chunk_z".into(), &chunk_z.into()).unwrap();
        Reflect::set(&chunk_obj, &"index".into(), &(self.current_index - 1).into()).unwrap();
        Reflect::set(&chunk_obj, &"total".into(), &self.current_chunk_coords.len().into()).unwrap();

        // Blocks are already in the right format: [[x,y,z,palette_index], ...]
        Reflect::set(&chunk_obj, &"blocks".into(), &blocks).unwrap();

        chunk_obj.into()
    }

    pub fn has_next(&self) -> bool {
        self.current_index < self.current_chunk_coords.len()
    }

    pub fn total_chunks(&self) -> u32 {
        self.current_chunk_coords.len() as u32
    }

    pub fn current_position(&self) -> u32 {
        self.current_index as u32
    }

    pub fn reset(&mut self) {
        self.current_index = 0;
    }

    pub fn skip_to(&mut self, index: u32) {
        self.current_index = (index as usize).min(self.current_chunk_coords.len());
    }
}


#[wasm_bindgen]
impl BlockStateWrapper {
    #[wasm_bindgen(constructor)]
    pub fn new(name: &str) -> Self {
        BlockStateWrapper(BlockState::new(name.to_string()))
    }

    pub fn with_property(&mut self, key: &str, value: &str) {
        self.0 = self.0.clone().with_property(key.to_string(), value.to_string());
    }

    pub fn name(&self) -> String {
        self.0.name.clone()
    }

    pub fn properties(&self) -> JsValue {
        let properties = self.0.properties.clone();
        let js_properties = js_sys::Object::new();
        for (key, value) in properties {
            js_sys::Reflect::set(&js_properties, &key.into(), &value.into()).unwrap();
        }
        js_properties.into()
    }
}


// Standalone functions
#[wasm_bindgen]
pub fn debug_schematic(schematic: &SchematicWrapper) -> String {
    format!("{}\n{}", schematic.debug_info(), print_schematic(&schematic.0))
}

#[wasm_bindgen]
pub fn debug_json_schematic(schematic: &SchematicWrapper) -> String {
    format!("{}\n{}", schematic.debug_info(), print_json_schematic(&schematic.0))
}