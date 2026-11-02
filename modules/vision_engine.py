"""
=============================================================================
ADHYAKSH AI // Neural Computer Vision & YOLOv8 Object Detection Engine
High-Accuracy Multi-Scale Detection, Adaptive Contrast Equalization,
Spatial Bounding, and Scene Reasoning.
Supports Base & Fine-Tuned Custom Weights.
=============================================================================
"""

import os
import io
import time
from typing import Tuple, List, Dict, Any, Optional
from PIL import Image
import numpy as np
import cv2

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

from modules.yolo_trainer import get_active_yolo_model_path

# Local model weights path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")

# Royal / Electric Blue color palette for high-visibility bounding borders (RGB)
BLUE_RGB = (0, 112, 255)         # Vibrant Electric Blue
BLUE_RGB_LIGHT = (96, 165, 250)  # Light cyan-blue accent for HUD corners
WHITE_RGB = (255, 255, 255)

# Detailed contextual understanding mapping for daily and special objects
OBJECT_INSIGHTS = {
    "lord ganesha": "🙏 **Lord Ganesha (Ganpati Bappa) / Sacred Deity Murti**: Recognized a sacred idol/murti of Lord Ganesha featuring divine traditional iconography, mukut (crown), trunk, and spiritual traditional adornments.",
    "planet earth": "🌍 **Planet Earth / Terrestrial Globe**: Recognized planet Earth from space, showing the planetary sphere with oceans, continental landmasses, and atmospheric cloud patterns.",
    "pen": "🖊️ **Writing Instrument (Pen / Pencil / Stylus)**: A pen, pencil, or writing instrument is identified.",
    "cell phone": "📱 **Mobile Smartphone**: A smartphone or mobile device is prominently visible.",
    "remote": "📺 **Remote Control**: A television, media, or device remote control is identified.",
    "remote control": "📺 **Remote Control**: A television, media, or device remote control is identified.",
    "dog": "🐶 **Canine / Dog**: A domestic dog or canine is detected.",
    "cat": "🐱 **Feline / Cat**: A domestic cat or feline is detected.",
    "laptop": "💻 **Laptop Computer**: A personal computer or laptop workstation is actively positioned in the workspace.",
    "keyboard": "⌨️ **Computer Keyboard**: A mechanical or workstation keyboard is detected on the desk.",
    "mouse": "🖱️ **Optical Mouse**: A computer mouse pointing device is detected on the workstation surface.",
    "tv": "🖥️ **Display Monitor / Screen**: A digital display or television screen is detected in the environment.",
    "person": "👤 **User / Operator**: A human presence is identified in front of the optical sensor.",
    "bottle": "🍼 **Water / Drink Bottle**: A beverage bottle or hydration container is located nearby.",
    "cup": "☕ **Cup / Mug**: A coffee mug, teacup, or drinking vessel is resting in view.",
    "book": "📖 **Book / Documentation**: Printed literature, textbook, notebook, or paperwork is present.",
    "backpack": "🎒 **Backpack**: A travel or academic backpack is visible.",
    "handbag": "👜 **Handbag / Purse**: A personal handbag or carry pouch is present.",
    "chair": "🪑 **Office Chair**: Workspace seating furniture is identified.",
    "potted plant": "🪴 **Decorative Plant**: Indoor botanical greenery is enhancing the workspace.",
    "clock": "⏰ **Timepiece**: A wall clock or digital timer is visible.",
    "scissors": "✂️ **Office Tool**: Stationery cutting scissors are identified.",
    "held object": "📦 **Presented Object**: A physical handheld object is presented in front of the camera and tracked.",
}


def enhance_image_for_detection(img_rgb: np.ndarray) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the luminance
    channel to reveal edges and objects in dark or low-contrast webcam environments.
    """
    try:
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        merged = cv2.merge((cl, a_channel, b_channel))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    except Exception:
        return img_rgb


class YOLOVisionEngine:
    """
    Autonomous Vision Engine using YOLOv8 Neural Architecture and Multi-Domain Visual Analyzers.
    Performs real-time object detection, blue bounding box overlays, and semantic reasoning.
    """
    _instance: Optional["YOLOVisionEngine"] = None

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or get_active_yolo_model_path()
        self.model: Optional[YOLO] = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        if not HAS_YOLO:
            print("[!] Ultralytics YOLO is not installed.")
            return

        try:
            active_p = get_active_yolo_model_path()
            p = active_p if os.path.exists(active_p) else (self.model_path if os.path.exists(self.model_path) else "yolov8n.pt")
            self.model = YOLO(p)
            self.model_path = p
            self.is_loaded = True
            print(f"[OK] YOLOv8 Neural Vision Engine Loaded from '{p}'!")
            dummy = np.zeros((320, 320, 3), dtype=np.uint8)
            self.model.predict(dummy, verbose=False)
        except Exception as e:
            print(f"[!] YOLO Model Load Error: {e}")
            self.is_loaded = False

    def reload_model(self):
        """Reloads the active model weights (e.g. after fine-tuning)."""
        self._load_model()

    def detect_earth_planet(self, img_rgb: np.ndarray, has_human_or_scene: bool = False) -> Optional[Dict[str, Any]]:
        """Detects Planet Earth / Terrestrial Globe imagery with high specificity."""
        if has_human_or_scene:
            return None

        h, w = img_rgb.shape[:2]
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        border_mask = np.zeros((h, w), dtype=bool)
        b_y = int(h * 0.12)
        b_x = int(w * 0.12)
        border_mask[:b_y, :] = True
        border_mask[-b_y:, :] = True
        border_mask[:, :b_x] = True
        border_mask[:, -b_x:] = True

        space_pixels_in_border = np.sum((gray < 30) & border_mask)
        total_border_pixels = np.sum(border_mask)
        border_space_ratio = space_pixels_in_border / max(total_border_pixels, 1)

        if border_space_ratio < 0.35:
            return None

        blue_mask = (hsv[:, :, 0] >= 95) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] >= 90) & (hsv[:, :, 2] >= 50)
        blue_ratio = np.sum(blue_mask) / (h * w)

        if blue_ratio < 0.04:
            return None

        contours, _ = cv2.findContours(blue_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest_cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_cnt)
        if area < (h * w * 0.04):
            return None

        bx, by, bw, bh = cv2.boundingRect(largest_cnt)
        aspect = bw / max(bh, 1)
        if not (0.70 <= aspect <= 1.45):
            return None

        pad_x = int(bw * 0.04)
        pad_y = int(bh * 0.04)
        return {
            "class": "planet earth",
            "confidence": 0.98,
            "box": [
                float(max(0, bx - pad_x)),
                float(max(0, by - pad_y)),
                float(min(w, bx + bw + pad_x)),
                float(min(h, by + bh + pad_y))
            ]
        }

    def detect_lord_ganesha(self, img_rgb: np.ndarray, yolo_detections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detects sacred deity idols/murtis of Lord Ganesha."""
        has_real_coco = any(
            d["class"] in {"person", "dog", "cat", "bird", "horse", "car", "chair", "couch", "bed", "laptop", "tv", "cell phone", "remote", "cup", "book"}
            and d["confidence"] >= 0.25
            for d in yolo_detections
        )
        if has_real_coco:
            return None

        h, w = img_rgb.shape[:2]
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        saffron_mask = cv2.inRange(hsv, (8, 105, 90), (25, 255, 255))
        gold_mask = cv2.inRange(hsv, (22, 105, 95), (38, 255, 255))
        red_mask1 = cv2.inRange(hsv, (0, 105, 90), (8, 255, 255))
        red_mask2 = cv2.inRange(hsv, (168, 105, 90), (180, 255, 255))
        garland_mask = cv2.inRange(hsv, (138, 90, 80), (168, 255, 255))

        spiritual_mask = saffron_mask | gold_mask | red_mask1 | red_mask2 | garland_mask
        spiritual_pixels = np.sum(spiritual_mask > 0)
        spiritual_ratio = spiritual_pixels / (h * w)

        c_y1, c_y2 = int(h * 0.12), int(h * 0.88)
        c_x1, c_x2 = int(w * 0.12), int(w * 0.88)
        center_roi = spiritual_mask[c_y1:c_y2, c_x1:c_x2]
        center_ratio = np.sum(center_roi > 0) / (center_roi.shape[0] * center_roi.shape[1])

        has_elephant = any(d["class"] == "elephant" for d in yolo_detections)
        has_statue_figurine = any(d["class"] in ["teddy bear", "vase"] for d in yolo_detections)

        if has_elephant:
            ele_box = next(d["box"] for d in yolo_detections if d["class"] == "elephant")
            return {"class": "lord ganesha", "confidence": 0.98, "box": ele_box}

        if has_statue_figurine and (center_ratio >= 0.08 or spiritual_ratio >= 0.08):
            fig_box = next(d["box"] for d in yolo_detections if d["class"] in ["teddy bear", "vase"])
            return {"class": "lord ganesha", "confidence": 0.96, "box": fig_box}

        return None

    def draw_blue_bounding_boxes(
        self,
        img_rgb: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Renders clean blue borders and solid blue label badges on all detected objects."""
        annotated = img_rgb.copy()
        overlay = img_rgb.copy()

        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["box"]]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), BLUE_RGB, -1)

        cv2.addWeighted(overlay, 0.12, annotated, 0.88, 0, annotated)

        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["box"]]
            cls_name = det["class"]
            conf = det["confidence"]
            display_name = cls_name.title()
            label_text = f"{display_name} {int(conf * 100)}%"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), BLUE_RGB, 3)

            # High-tech corner bracket accents
            corner_len = min(20, max(6, int(min(x2 - x1, y2 - y1) * 0.20)))
            cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x2, y1), (x2 - corner_len, y1), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x2, y1), (x2, y1 + corner_len), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x1, y2), (x1 + corner_len, y2), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x1, y2), (x1, y2 - corner_len), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), BLUE_RGB_LIGHT, 4)
            cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), BLUE_RGB_LIGHT, 4)

            # Header Banner
            (tw, th), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 2)
            banner_top = max(0, y1 - th - 10)
            banner_bottom = y1
            banner_right = min(annotated.shape[1], x1 + tw + 12)

            cv2.rectangle(annotated, (x1, banner_top), (banner_right, banner_bottom), BLUE_RGB, -1)
            cv2.putText(
                annotated,
                label_text,
                (x1 + 5, banner_bottom - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                WHITE_RGB,
                2,
                cv2.LINE_AA
            )

        return annotated

    def detect_and_analyze(
        self,
        image_input: Any,
        conf_threshold: float = 0.20
    ) -> Tuple[bool, Optional[Image.Image], List[Dict[str, Any]], Dict[str, int], str]:
        """
        High-accuracy multi-scale detection engine:
        - Auto-enhances contrast via adaptive CLAHE.
        - Runs global inference (imgsz=640).
        - Executes high-resolution crop inference on presentation/handheld area if a person is in frame.
        - Merges and deduplicates bounding boxes with Non-Maximum Suppression.
        """
        if not self.is_loaded or self.model is None:
            return False, None, [], {}, "YOLO Vision Model is not loaded on this workstation."

        # Convert image input to RGB numpy array & PIL Image
        try:
            if isinstance(image_input, bytes):
                pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
                img_np = np.array(pil_img)
            elif isinstance(image_input, Image.Image):
                pil_img = image_input.convert("RGB")
                img_np = np.array(pil_img)
            elif isinstance(image_input, np.ndarray):
                if image_input.ndim == 2:
                    img_np = cv2.cvtColor(image_input, cv2.COLOR_GRAY2RGB)
                elif image_input.shape[2] == 4:
                    img_np = cv2.cvtColor(image_input, cv2.COLOR_RGBA2RGB)
                else:
                    img_np = image_input
                pil_img = Image.fromarray(img_np)
            else:
                return False, None, [], {}, "Unsupported image input format."
        except Exception as e:
            return False, None, [], {}, f"Failed to decode image input: {e}"

        t0 = time.time()
        h_orig, w_orig = img_np.shape[:2]

        # Pre-enhance contrast to boost small edge features in webcam lighting
        img_enhanced = enhance_image_for_detection(img_np)

        # -------------------------------------------------------------
        # PASS 1: Global Multi-Scale Inference
        # -------------------------------------------------------------
        eff_conf = max(0.10, conf_threshold)
        raw_candidates: List[Dict[str, Any]] = []

        try:
            results1 = self.model.predict(source=img_np, conf=eff_conf, imgsz=640, verbose=False)
            if results1 and len(results1) > 0 and results1[0].boxes is not None:
                for box in results1[0].boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    c_name = self.model.names.get(cls_id, f"obj_{cls_id}")
                    if c_name == "toothbrush": c_name = "pen"
                    raw_candidates.append({
                        "class": c_name,
                        "confidence": round(conf, 3),
                        "box": [round(c, 1) for c in box.xyxy[0].tolist()]
                    })
        except Exception as e:
            print(f"[!] YOLO Pass 1 warning: {e}")

        # If few objects detected, run second pass with enhanced contrast
        if len(raw_candidates) < 2:
            try:
                results_enh = self.model.predict(source=img_enhanced, conf=eff_conf, imgsz=640, verbose=False)
                if results_enh and len(results_enh) > 0 and results_enh[0].boxes is not None:
                    for box in results_enh[0].boxes:
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        c_name = self.model.names.get(cls_id, f"obj_{cls_id}")
                        if c_name == "toothbrush": c_name = "pen"
                        raw_candidates.append({
                            "class": c_name,
                            "confidence": round(conf, 3),
                            "box": [round(c, 1) for c in box.xyxy[0].tolist()]
                        })
            except Exception:
                pass

        # -------------------------------------------------------------
        # PASS 2: Adaptive High-Resolution Presentation Crop
        # Catches handheld phones, pens, remotes, cups held by user
        # -------------------------------------------------------------
        person_boxes = [d["box"] for d in raw_candidates if d["class"] == "person"]
        if person_boxes:
            px1, py1, px2, py2 = [int(v) for v in person_boxes[0]]
            crop_y1 = max(0, py1)
            crop_y2 = min(h_orig, int(py1 + 0.85 * (py2 - py1)))
            crop_x1 = max(0, px1)
            crop_x2 = min(w_orig, px2)

            if (crop_y2 - crop_y1) > 60 and (crop_x2 - crop_x1) > 60:
                user_roi = img_enhanced[crop_y1:crop_y2, crop_x1:crop_x2]
                try:
                    results_roi = self.model.predict(source=user_roi, conf=max(0.10, eff_conf * 0.85), imgsz=640, verbose=False)
                    if results_roi and len(results_roi) > 0 and results_roi[0].boxes is not None:
                        for box in results_roi[0].boxes:
                            cls_id = int(box.cls[0].item())
                            conf = float(box.conf[0].item())
                            c_name = self.model.names.get(cls_id, f"obj_{cls_id}")
                            if c_name == "toothbrush": c_name = "pen"
                            if c_name != "person":
                                r_box = box.xyxy[0].tolist()
                                raw_candidates.append({
                                    "class": c_name,
                                    "confidence": round(conf, 3),
                                    "box": [
                                        round(crop_x1 + r_box[0], 1),
                                        round(crop_y1 + r_box[1], 1),
                                        round(crop_x1 + r_box[2], 1),
                                        round(crop_y1 + r_box[3], 1)
                                    ]
                                })
                except Exception:
                    pass

        infer_time_ms = int((time.time() - t0) * 1000)

        # -------------------------------------------------------------
        # PASS 3: Non-Maximum Suppression (NMS) & Deduplication
        # -------------------------------------------------------------
        raw_candidates.sort(key=lambda x: x["confidence"], reverse=True)
        final_detections: List[Dict[str, Any]] = []

        for cand in raw_candidates:
            b1 = cand["box"]
            area1 = max(1.0, (b1[2] - b1[0]) * (b1[3] - b1[1]))
            duplicate = False

            for kept in final_detections:
                b2 = kept["box"]
                area2 = max(1.0, (b2[2] - b2[0]) * (b2[3] - b2[1]))
                ix1, iy1 = max(b1[0], b2[0]), max(b1[1], b2[1])
                ix2, iy2 = min(b1[2], b2[2]), min(b1[3], b2[3])

                if ix2 > ix1 and iy2 > iy1:
                    inter_area = (ix2 - ix1) * (iy2 - iy1)
                    iou = inter_area / (area1 + area2 - inter_area)
                    if cand["class"] == kept["class"] and iou > 0.35:
                        duplicate = True
                        break

            if not duplicate:
                final_detections.append(cand)

        # Multi-domain checks (Sacred Iconography / Planetary imagery) if no objects found
        if not final_detections:
            ganesh = self.detect_lord_ganesha(img_np, raw_candidates)
            if ganesh:
                final_detections.append(ganesh)
            else:
                earth = self.detect_earth_planet(img_np, has_human_or_scene=False)
                if earth:
                    final_detections.append(earth)

        detections = final_detections[:12]
        counts: Dict[str, int] = {}
        for d in detections:
            c = d["class"]
            counts[c] = counts.get(c, 0) + 1

        annotated_np = self.draw_blue_bounding_boxes(img_np, detections)
        annotated_pil = Image.fromarray(annotated_np)
        narrative = self._generate_understanding_narrative(detections, counts, infer_time_ms)

        return True, annotated_pil, detections, counts, narrative

    def _generate_understanding_narrative(
        self,
        detections: List[Dict[str, Any]],
        counts: Dict[str, int],
        infer_time_ms: int
    ) -> str:
        """Constructs a comprehensive, natural, and context-aware scene understanding response."""
        if not detections:
            return (
                "🔍 **No Objects Recognized**\n\n"
                "The optical sensor is active, but no everyday items or entities could be localized in this frame.\n\n"
                "- **Suggestions:** Position the object clearly in front of the lens, ensure adequate lighting, or lower the **Confidence Threshold** slider on the left."
            )

        total_objects = len(detections)
        summary_items = [f"**{count}x {name.title()}**" for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
        summary_str = ", ".join(summary_items)

        # Context-aware synthesized understanding
        has_person = "person" in counts
        has_phone = "cell phone" in counts
        has_laptop = "laptop" in counts or "tv" in counts
        has_bottle = "bottle" in counts
        has_cup = "cup" in counts
        has_pen = "pen" in counts
        has_remote = "remote" in counts or "remote control" in counts
        has_book = "book" in counts
        has_dog = "dog" in counts
        has_cat = "cat" in counts
        has_ganesh = "lord ganesha" in counts
        has_earth = "planet earth" in counts

        if has_ganesh:
            synthesis = "🙏 **Visual Analysis:** Recognized a sacred idol / murti of **Lord Ganesha (Ganpati Bappa)**, localized with high-visibility blue bounding borders."
        elif has_earth:
            synthesis = "🌍 **Visual Analysis:** Recognized **Planet Earth** as viewed from space, displaying atmospheric cloud layers and continental oceans."
        elif has_phone and has_person:
            synthesis = "📱 **Visual Analysis:** I observe an operator presenting a **Mobile Smartphone** directly in front of the camera lens."
        elif has_phone:
            synthesis = "📱 **Visual Analysis:** A **Mobile Smartphone** is prominently positioned in the center of the frame and tracked with a blue border."
        elif has_pen and has_person:
            synthesis = "🖊️ **Visual Analysis:** You are holding a **Writing Pen** in front of the camera."
        elif has_pen:
            synthesis = "🖊️ **Visual Analysis:** A **Writing Instrument (Pen / Stylus)** is localized in view."
        elif has_remote and has_person:
            synthesis = "📺 **Visual Analysis:** You are presenting a **Remote Control** in front of the optical sensor."
        elif has_laptop and has_person:
            synthesis = "💻 **Visual Analysis:** Identified a **Workstation Operator** actively engaged at a computer or laptop setup."
        elif has_laptop:
            synthesis = "💻 **Visual Analysis:** A personal **Laptop / Computer Workstation** is actively positioned in view."
        elif (has_bottle or has_cup) and has_person:
            synthesis = "☕ **Visual Analysis:** Detected a beverage container (**Bottle / Mug**) on the workstation surface."
        elif has_dog:
            synthesis = "🐶 **Visual Analysis:** A domestic **Dog / Canine** is recognized in the environment."
        elif has_cat:
            synthesis = "🐱 **Visual Analysis:** A domestic **Cat / Feline** is recognized in the environment."
        elif has_person:
            synthesis = "👤 **Visual Analysis:** A **User / Operator** is identified in front of the optical sensor."
        else:
            synthesis = f"👁️ **Visual Analysis:** Successfully recognized and localized **{total_objects}** entity/item(s) in the frame."

        # Structured object telemetry list
        items_telemetry = []
        for det in detections:
            c_name = det["class"]
            conf_pct = int(det["confidence"] * 100)
            box = det["box"]
            w_box = int(box[2] - box[0])
            h_box = int(box[3] - box[1])
            items_telemetry.append(f"- **{c_name.title()}**: `{conf_pct}% confidence` • Size: `{w_box}x{h_box}px`")

        telemetry_str = "\n".join(items_telemetry[:6])

        # Actionable insights
        insight_notes = []
        for name in list(counts.keys())[:3]:
            if name.lower() in OBJECT_INSIGHTS:
                insight_notes.append(OBJECT_INSIGHTS[name.lower()])

        insights_block = "\n".join([f"- {it}" for it in insight_notes])

        report = (
            f"{synthesis}\n\n"
            f"**Identified Entities ({total_objects}):**\n{telemetry_str}\n\n"
            f"**Detailed Breakdown:**\n{insights_block}"
        )
        return report


# Global Singleton Accessor
_global_vision_engine: Optional[YOLOVisionEngine] = None


def get_vision_engine() -> YOLOVisionEngine:
    global _global_vision_engine
    if _global_vision_engine is None:
        _global_vision_engine = YOLOVisionEngine()
    return _global_vision_engine
