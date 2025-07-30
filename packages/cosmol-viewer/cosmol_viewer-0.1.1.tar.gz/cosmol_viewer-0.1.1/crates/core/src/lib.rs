mod shader;
use std::{
    sync::{Arc, Mutex},
};

pub mod utils;
pub mod parser;
pub use eframe::egui;

use eframe::egui::{Color32, Stroke};

use shader::Canvas;

pub use crate::utils::{Shape};
pub mod shapes;
use crate::{scene::Scene};

pub mod scene;

pub struct AppWrapper(pub Arc<Mutex<Option<App>>>);

impl eframe::App for AppWrapper {
    fn update(&mut self, ctx: &egui::Context, frame: &mut eframe::Frame) {
        if let Some(app) = &mut *self.0.lock().unwrap() {
            app.update(ctx, frame);
        }
    }
}

pub struct App {
    canvas: Canvas,
    gl: Option<Arc<eframe::glow::Context>>,
    pub ctx: egui::Context,
}

impl App {
    pub fn new(cc: &eframe::CreationContext<'_>, scene: Scene) -> Self {
        let gl = cc.gl.clone();
        let canvas = Canvas::new(gl.as_ref().unwrap().clone(), scene).unwrap();
        App {
            gl,
            canvas,
            ctx: cc.egui_ctx.clone(),
        }
    }

    pub fn update_scene(&mut self, scene: Scene) {
        self.canvas.update_scene(scene);
    }
}

impl eframe::App for App {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui_extras::install_image_loaders(ctx);
        egui::CentralPanel::default()
            .frame(
                egui::Frame::default()
                    .fill(Color32::from_rgb(48, 48, 48))
                    .inner_margin(0.0)
                    .outer_margin(0.0)
                    .stroke(Stroke::new(0.0, Color32::from_rgb(30, 200, 30))),
            )
            .show(ctx, |ui| {
                ui.set_width(ui.available_width());
                ui.set_height(ui.available_height());

                self.canvas.custom_painting(ui);
            });
    }
}


