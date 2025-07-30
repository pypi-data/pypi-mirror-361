# Standard library
import argparse
import re
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party
import numpy as np
import yaml
import torch
from PIL import Image, ImageDraw
from pydantic import BaseModel
from torchvision import transforms

# Project modules
from .model import Model
from .utils import CTCLabelConverter, AttnLabelConverter
from manuscript.detectors import EASTInfer
from manuscript.detectors.east.lanms import locality_aware_nms


class WordResponse(BaseModel):
    index: int
    text: str
    x1: int
    y1: int
    x2: int
    y2: int
    score: float


class StringResponse(BaseModel):
    index: int
    words: List[WordResponse]
    x1: int
    y1: int
    x2: int
    y2: int


class BlockResponse(BaseModel):
    index: int
    strings: List[StringResponse]
    x1: int
    y1: int
    x2: int
    y2: int


class PageResponse(BaseModel):
    blocks: List[BlockResponse]

    def word_count(self) -> int:
        return sum(
            len(string.words) for block in self.blocks for string in block.strings
        )

    def to_plain_text(self, line_sep: str = "\n", block_sep: str = "\n\n\n") -> str:
        block_texts: List[str] = []
        for block in self.blocks:
            lines = [" ".join(w.text for w in string.words) for string in block.strings]
            block_texts.append(line_sep.join(lines))
        return block_sep.join(block_texts)


class DocumentOCRPipeline:
    def __init__(
        self,
        config_path: str,
        ocr_model_path: str,
        *,
        device: Union[str, torch.device] = None,
        detect_params: Dict[str, Any] = None,
        max_splits: int = None,
        y_tol_ratio: float = 0.6,
        x_gap_ratio: float = np.inf,
        rotate_threshold: float = 1.5,
        TTA: bool = True,
        TTA_thresh: float = 0.1,
        use_nms: bool = True,
        nms_thresh: float = 0.25,
        batch_size: int = 1,
    ):
        self.batch_size = batch_size
        # 1) device selection
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = (
                device if isinstance(device, torch.device) else torch.device(device)
            )

        # 2) load OCR model
        self.model, self.converter, self.opt = self._load_model(
            config_path, ocr_model_path
        )

        # 3) initialize EAST detector
        east_cfg = detect_params or {}
        weights = east_cfg.pop("weights_path", None)
        self.detector = EASTInfer(
            weights_path=weights,
            device=self.device.type,
            target_size=east_cfg.get("target_size", 1280),
            score_geo_scale=east_cfg.get("score_geo_scale", 0.25),
            shrink_ratio=east_cfg.get("shrink_ratio", 0.6),
            score_thresh=east_cfg.get("score_thresh", 0.9),
            iou_threshold=east_cfg.get("iou_threshold", 0.2),
        )

        # 4) layout parameters
        self.max_splits = max_splits
        self.y_tol_ratio = y_tol_ratio
        self.x_gap_ratio = x_gap_ratio
        self.rotate_threshold = rotate_threshold

        # 6) Test-time augmentation (TTA)
        self.TTA = TTA
        self.TTA_thresh = TTA_thresh

        self.use_nms = use_nms
        self.nms_thresh = nms_thresh

    def _recognize_crops_in_batches(self, crops: List[Image.Image]) -> List[str]:
        """
        If batch_size == 1, process all crops sequentially without batching.
        If batch_size > 1, split into chunks and batch-process.
        """
        if self.batch_size <= 1:
            # sequential processing
            return [self._clean_text(self._recognize_text(crop)) for crop in crops]

        # batch processing
        total = len(crops)
        texts: List[str] = []
        for i in range(0, total, self.batch_size):
            batch = crops[i : i + self.batch_size]
            texts.extend(self._recognize_batch_texts(batch))
        return texts

    def _prepare_crop(
        self, pil_img: Image.Image, box: Tuple[int, int, int, int]
    ) -> Image.Image:
        x0, y0, x1, y1 = box
        crop = pil_img.crop((x0, y0, x1, y1))
        width, height = crop.size
        if height > width * self.rotate_threshold:
            crop = crop.rotate(90, expand=True)
        return crop

    def _infer_boxes(
        self, img_array: np.ndarray
    ) -> List[Tuple[Tuple[int, int, int, int], float]]:
        det_page = self.detector.infer(img_array)
        h, w = img_array.shape[:2]
        ts = self.detector.target_size
        sx, sy = w / ts, h / ts
        results: List[Tuple[Tuple[int, int, int, int], float]] = []
        for block in det_page.blocks:
            for word in block.words:
                scaled = [(int(x * sx), int(y * sy)) for x, y in word.polygon]
                x0 = min(x for x, y in scaled)
                y0 = min(y for x, y in scaled)
                x1 = max(x for x, y in scaled)
                y1 = max(y for x, y in scaled)
                score = float(getattr(word, "score", 1.0))
                results.append(((x0, y0, x1, y1), score))
        return results

    def _iou(
        self, b1: Tuple[int, int, int, int], b2: Tuple[int, int, int, int]
    ) -> float:
        x0 = max(b1[0], b2[0])
        y0 = max(b1[1], b2[1])
        x1 = min(b1[2], b2[2])
        y1 = min(b1[3], b2[3])
        if x1 <= x0 or y1 <= y0:
            return 0.0
        inter = (x1 - x0) * (y1 - y0)
        area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
        area2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
        return inter / float(area1 + area2 - inter)

    def _merge_tta_boxes(
        self,
        boxes1: List[Tuple[Tuple[int, int, int, int], float]],
        boxes2: List[Tuple[Tuple[int, int, int, int], float]],
    ) -> List[Tuple[Tuple[int, int, int, int], float]]:
        merged = []
        for b1, s1 in boxes1:
            for b2, s2 in boxes2:
                if self._iou(b1, b2) > self.TTA_thresh:
                    x0 = min(b1[0], b2[0])
                    x1 = max(b1[2], b2[2])
                    y0 = b1[1]
                    y1 = b1[3]
                    avg_score = (s1 + s2) / 2
                    merged.append(((x0, y0, x1, y1), avg_score))
                    break
        return merged

    def _load_model(self, config_path: str, model_path: str):
        """
        Загружает конфигурацию и веса модели.
        :param config_path: путь к YAML конфигу модели
        :param model_path: путь к файлу .pth с весами
        :return: tuple (model, converter, opt)
        """
        # 1. Загружаем опции из конфига
        with open(config_path, "r", encoding="utf-8") as f:
            opt = argparse.Namespace(**yaml.safe_load(f))

        # 2. Выбираем конвертер
        if "CTC" in opt.Prediction:
            converter = CTCLabelConverter(opt.character)
        else:
            converter = AttnLabelConverter(opt.character)
        opt.num_class = len(converter.character)
        if opt.rgb:
            opt.input_channel = 3

        # 3. Строим модель и переносим её на нужное устройство
        model = Model(opt).to(self.device)

        # 4. На GPU с несколькими картами — оборачиваем в DataParallel
        if self.device.type == "cuda" and torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model)

        # 5. Загружаем checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)

        # 6. Если чекпоинт — словарь с ключом "model", берём его, иначе — весь словарь
        if isinstance(checkpoint, dict) and "model" in checkpoint:
            state_dict = checkpoint["model"]
        else:
            state_dict = checkpoint

        # 7. Убираем префикс "module." из имён, если он есть
        cleaned_state = {}
        for k, v in state_dict.items():
            if k.startswith("module."):
                cleaned_state[k[len("module.") :]] = v
            else:
                cleaned_state[k] = v

        # 8. Загружаем веса в модель
        model.load_state_dict(cleaned_state, strict=True)
        model.eval()

        return model, converter, opt

    def _resolve_intersections(
        self, boxes: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Проверяет пересечения между боксами, сжимает их на 10% (или заданное значение),
        пока пересечения не исчезнут. Возвращает список боксов в том же порядке, что и исходный.
        """

        # Сжимаем боксы до тех пор, пока пересечения не исчезнут
        def do_boxes_intersect(box1, box2):
            return not (
                box1[2] <= box2[0]
                or box2[2] <= box1[0]
                or box1[3] <= box2[1]
                or box2[3] <= box1[1]
            )

        resolved_boxes = boxes[:]
        changed = True

        while changed:
            changed = False
            new_boxes = []
            for i in range(len(resolved_boxes)):
                for j in range(i + 1, len(resolved_boxes)):
                    if do_boxes_intersect(resolved_boxes[i], resolved_boxes[j]):
                        # Находим бокс с большим пересечением
                        box1, box2 = resolved_boxes[i], resolved_boxes[j]
                        if (box1[2] - box1[0]) > (box2[2] - box2[0]):
                            # Сжимаем box1
                            x0, y0, x1, y1 = box1
                            box1 = (
                                x0,
                                y0,
                                int(x1 - (x1 - x0) * 0.1),
                                y1,
                            )  # Сжимаем на 10%
                        else:
                            # Сжимаем box2
                            x0, y0, x1, y1 = box2
                            box2 = (
                                x0,
                                y0,
                                int(x1 - (x1 - x0) * 0.1),
                                y1,
                            )  # Сжимаем на 10%

                        # Обновляем боксы
                        resolved_boxes[i] = box1
                        resolved_boxes[j] = box2
                        changed = True

            new_boxes = resolved_boxes

        return new_boxes

    def recognize_word(
        self,
        pil_img: Image.Image,
        box: Tuple[int, int, int, int],
        word_idx: int,
        score: float,
    ) -> WordResponse:
        """
        Распознаёт один бокс:
        1) Вырезает ROI из PIL-картинки
        2) При необходимости поворачивает ROI на 90 градусов
        3) Применяет модель + очищает текст
        4) Возвращает WordResponse
        """
        x0, y0, x1, y1 = box
        crop = pil_img.crop((x0, y0, x1, y1))

        # Проверяем нужно ли повернуть
        width, height = crop.size

        if height > width * self.rotate_threshold:
            crop = crop.rotate(
                90, expand=True
            )  # Поворачиваем на +90 градусов по часовой

        raw = self._recognize_text(crop)
        cleaned = self._clean_text(raw)

        return WordResponse(
            index=word_idx, text=cleaned, x1=x0, y1=y0, x2=x1, y2=y1, score=score
        )

    def visualize(
        self,
        pil_img: Image.Image,
        *,
        show_words: bool = True,
        show_blocks: bool = True,
        connect_strings: bool = True,
        show_numbers: bool = True,
        word_style: Dict[str, Any] = None,
        block_style: Dict[str, Any] = None,
        line_style: Dict[str, Any] = None,
        number_style: Dict[str, Any] = None,
    ) -> Image.Image:
        """
        Рисует на копии входного изображения:
        - слова: outline/fill по word_style
        - блоки: outline/fill по block_style
        - строки: соединительные линии между соседними словами по line_style
        - цифры порядковые для боксов (если show_numbers=True)
        """
        # Стили по умолчанию
        word_style = word_style or {
            "outline": (255, 0, 0, 255),
            "fill": (255, 0, 0, 80),  # Полупрозрачная красная заливка
            "width": 1,
        }
        block_style = block_style or {
            "outline": (0, 0, 255, 255),
            "fill": (0, 0, 255, 50),  # Полупрозрачная синяя заливка
            "width": 3,
        }
        line_style = line_style or {"fill": (0, 255, 0, 200), "width": 5}
        number_style = number_style or {
            "fill": (0, 0, 0, 255),
            "font_size": 30,
            "bg_fill": (255, 255, 255, 128),
        }

        # Получаем структуру PageResponse
        page = self(pil_img)

        # Подготовка холстов
        base = pil_img.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Рисуем блоки
        if show_blocks:
            for block in page.blocks:
                fill = block_style.get("fill")
                if fill is not None:
                    fill = (*fill[:3], fill[3]) if len(fill) == 4 else (*fill, 100)
                draw.rectangle(
                    [block.x1, block.y1, block.x2, block.y2],
                    outline=block_style["outline"],
                    width=block_style["width"],
                    fill=fill,
                )

        # Рисуем слова
        if show_words:
            for block in page.blocks:
                for string in block.strings:
                    words = sorted(string.words, key=lambda w: w.x1)
                    for i, word in enumerate(words):
                        word.index = i + 1
                        fill = word_style.get("fill")
                        if fill is not None:
                            fill = (
                                (*fill[:3], fill[3]) if len(fill) == 4 else (*fill, 100)
                            )
                            draw.rectangle(
                                [word.x1, word.y1, word.x2, word.y2],
                                fill=fill,
                                outline=None,
                            )
                        if word_style.get("outline"):
                            draw.rectangle(
                                [word.x1, word.y1, word.x2, word.y2],
                                outline=word_style["outline"],
                                width=word_style["width"],
                                fill=None,
                            )

        # Соединительные линии
        if connect_strings:
            for block in page.blocks:
                for string in block.strings:
                    words = sorted(string.words, key=lambda w: w.x1)
                    for prev, curr in zip(words, words[1:]):
                        y_prev = (prev.y1 + prev.y2) // 2
                        y_curr = (curr.y1 + curr.y2) // 2
                        draw.line(
                            [(prev.x2, y_prev), (curr.x1, y_curr)],
                            fill=line_style["fill"],
                            width=line_style["width"],
                        )

        # Порядковые номера
        if show_numbers:
            for block in page.blocks:
                for string in block.strings:
                    for word in string.words:
                        text_number = str(word.index)
                        text_size = number_style.get("font_size", 30)
                        text_x = (word.x1 + word.x2) / 2
                        text_y = (word.y1 + word.y2) / 2
                        bg_width = text_size * len(text_number)
                        bg_height = text_size
                        draw.rectangle(
                            [
                                text_x - bg_width / 2,
                                text_y - bg_height / 2,
                                text_x + bg_width / 2,
                                text_y + bg_height / 2,
                            ],
                            fill=number_style["bg_fill"],
                        )
                        draw.text(
                            (text_x - text_size / 2, text_y - text_size / 2),
                            text_number,
                            fill=number_style["fill"],
                        )

        # Комбинируем и возвращаем результат
        result = Image.alpha_composite(base, overlay)
        return result.convert("RGB")

    def __call__(self, pil_img: Image.Image) -> PageResponse:
        # 1) Преобразование и детекция
        rgb_img = pil_img.convert("RGB")
        img_array = np.array(rgb_img)
        boxes_with_scores = self._infer_boxes(img_array)

        # 2) TTA
        if self.TTA:
            flipped = np.fliplr(img_array)
            mirrored = self._infer_boxes(flipped)
            h, w = img_array.shape[:2]
            mirrored_flipped = [
                (((w - x1, y0, w - x0, y1), score))
                for ((x0, y0, x1, y1), score) in mirrored
            ]
            all_boxes = self._merge_tta_boxes(boxes_with_scores, mirrored_flipped)
        else:
            all_boxes = boxes_with_scores

        # 3) NMS
        if self.use_nms:
            lanms_input = np.stack(
                [
                    np.array([x0, y0, x1, y0, x1, y1, x0, y1, score], dtype=np.float32)
                    for ((x0, y0, x1, y1), score) in all_boxes
                ],
                axis=0,
            )
            if lanms_input.size:
                lanms_out = locality_aware_nms(lanms_input, self.nms_thresh)
            else:
                lanms_out = np.empty((0, 9), dtype=np.float32)
            processed = []
            for row in lanms_out:
                xs, ys = row[[0, 2, 4, 6]].astype(int), row[[1, 3, 5, 7]].astype(int)
                processed.append(
                    (
                        (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),
                        float(row[8]),
                    )
                )
        else:
            processed = all_boxes

        # 4) Словарь и простой список боксов
        box_to_score = {tuple(b): s for b, s in processed}
        only_boxes = [b for b, _ in processed]

        # Если batch_size не указан — используем старую логику
        if not self.batch_size:
            blocks: List[BlockResponse] = []
            cols = self._segment_columns(only_boxes)
            for b_idx, col in enumerate(cols):
                sorted_boxes = self._sort_boxes_reading_order_with_resolutions(col)
                lines = self._split_into_lines(sorted_boxes)
                strings: List[StringResponse] = []
                for s_idx, line_boxes in enumerate(lines):
                    words: List[WordResponse] = []
                    for w_idx, box in enumerate(line_boxes):
                        score = box_to_score.get(tuple(box), 1.0)
                        words.append(self.recognize_word(rgb_img, box, w_idx, score))
                    xs1 = [w.x1 for w in words]
                    ys1 = [w.y1 for w in words]
                    xs2 = [w.x2 for w in words]
                    ys2 = [w.y2 for w in words]
                    strings.append(
                        StringResponse(
                            index=s_idx,
                            words=words,
                            x1=min(xs1),
                            y1=min(ys1),
                            x2=max(xs2),
                            y2=max(ys2),
                        )
                    )
                xs1 = [s.x1 for s in strings]
                ys1 = [s.y1 for s in strings]
                xs2 = [s.x2 for s in strings]
                ys2 = [s.y2 for s in strings]
                blocks.append(
                    BlockResponse(
                        index=b_idx,
                        strings=strings,
                        x1=min(xs1),
                        y1=min(ys1),
                        x2=max(xs2),
                        y2=max(ys2),
                    )
                )
            return PageResponse(blocks=blocks)

        # Иначе — batch_size задан, новая логика:
        # 5) Разбиение на колонки->строки + сбор метаданных
        cols = self._segment_columns(only_boxes)
        meta: List[Tuple[int, int, int, Tuple[int, int, int, int], float]] = []
        for b_idx, col in enumerate(cols):
            sorted_boxes = self._sort_boxes_reading_order_with_resolutions(col)
            lines = self._split_into_lines(sorted_boxes)
            for s_idx, line in enumerate(lines):
                for w_idx, box in enumerate(line):
                    score = box_to_score.get(tuple(box), 1.0)
                    meta.append((b_idx, s_idx, w_idx, box, score))

        # 6) Батчевое распознавание всех кропов страницы
        all_crops = [self._prepare_crop(rgb_img, box) for (_, _, _, box, _) in meta]
        all_texts = self._recognize_crops_in_batches(all_crops)

        # 7) Группируем тексты обратно по (block, string)
        grouped: Dict[Tuple[int, int], List[WordResponse]] = {}
        for (b_idx, s_idx, w_idx, box, score), text in zip(meta, all_texts):
            wr = WordResponse(
                index=w_idx,
                text=text,
                x1=box[0],
                y1=box[1],
                x2=box[2],
                y2=box[3],
                score=score,
            )
            grouped.setdefault((b_idx, s_idx), []).append(wr)

        # 8) Собираем блоки и строки
        blocks: List[BlockResponse] = []
        for b_idx, col in enumerate(cols):
            # сколько строк в блоке
            s_max = max(s for (bb, s) in grouped.keys() if bb == b_idx)
            strings: List[StringResponse] = []
            for s_idx in range(s_max + 1):
                words = sorted(grouped.get((b_idx, s_idx), []), key=lambda w: w.index)
                if not words:
                    continue
                xs1 = [w.x1 for w in words]
                ys1 = [w.y1 for w in words]
                xs2 = [w.x2 for w in words]
                ys2 = [w.y2 for w in words]
                strings.append(
                    StringResponse(
                        index=s_idx,
                        words=words,
                        x1=min(xs1),
                        y1=min(ys1),
                        x2=max(xs2),
                        y2=max(ys2),
                    )
                )
            # границы блока
            xs1 = [s.x1 for s in strings]
            ys1 = [s.y1 for s in strings]
            xs2 = [s.x2 for s in strings]
            ys2 = [s.y2 for s in strings]
            blocks.append(
                BlockResponse(
                    index=b_idx,
                    strings=strings,
                    x1=min(xs1),
                    y1=min(ys1),
                    x2=max(xs2),
                    y2=max(ys2),
                )
            )

        return PageResponse(blocks=blocks)

    def _split_into_lines(
        self, boxes: List[Tuple[int, int, int, int]]
    ) -> List[List[Tuple[int, int, int, int]]]:
        """
        Группирует отсортированный (read-order) список боксов в строки,
        используя вертикальный (y_tol_ratio) и горизонтальный (x_gap_ratio) допуски.
        """
        if not boxes:
            return []

        # 1) сначала получаем «читаемый» порядок
        sorted_boxes = self._sort_boxes_reading_order_with_resolutions(boxes)

        # 2) вычисляем среднюю высоту бокса
        heights = [b[3] - b[1] for b in sorted_boxes]
        avg_h = float(np.mean(heights)) if heights else 0.0

        lines: List[List[Tuple[int, int, int, int]]] = []
        for box in sorted_boxes:
            x0, y0, x1, y1 = box
            center_y = (y0 + y1) / 2

            if not lines:
                # первая строка
                lines.append([box])
                continue

            # параметры предыдущей строки
            prev_line = lines[-1]
            prev_centers = [(b[1] + b[3]) / 2 for b in prev_line]
            prev_center_y = float(np.mean(prev_centers))
            last_box = prev_line[-1]
            last_x1 = last_box[2]

            # 3) проверяем, попадает ли новый бокс в ту же строку:
            same_row = (
                abs(center_y - prev_center_y) <= avg_h * self.y_tol_ratio
                and (x0 - last_x1) <= avg_h * self.x_gap_ratio
            )

            if same_row:
                prev_line.append(box)
            else:
                lines.append([box])

        return lines

    def _recognize_batch_texts(self, images: List[Image.Image]) -> List[str]:

        self.model.eval()

        # Преобразуем изображения в тензоры
        batch = torch.cat([self._preprocess(img) for img in images], dim=0).to(
            self.device
        )

        batch_size = batch.size(0)
        length_for_pred = torch.IntTensor([self.opt.batch_max_length] * batch_size).to(
            self.device
        )
        text_for_pred = (
            torch.LongTensor(batch_size, self.opt.batch_max_length + 1)
            .fill_(0)
            .to(self.device)
        )

        with torch.no_grad():
            if "CTC" in self.opt.Prediction:
                preds = self.model(batch, text_for_pred)
                _, indices = preds.max(2)
                preds_str = self.converter.decode(
                    indices.data, torch.IntTensor([preds.size(1)] * batch_size)
                )
            else:
                preds = self.model(batch, text_for_pred, is_train=False)
                _, indices = preds.max(2)
                preds_str = self.converter.decode(indices, length_for_pred)

        return [self._clean_text(p) for p in preds_str]

    def _preprocess(self, image: Image.Image) -> torch.Tensor:
        """
        Преобразует PIL изображение в тензор для распознавания.
        """
        # Оригинальная предобработка через transforms
        if not self.opt.rgb:
            image = image.convert("L")
        transform = transforms.Compose(
            [
                transforms.Resize((self.opt.imgH, self.opt.imgW), Image.BICUBIC),
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,)),
            ]
        )
        img = transform(image).unsqueeze(0)  # Add batch dimension
        return img.to(self.device)

    def _recognize_text(self, image: Image.Image) -> str:
        tensor = self._preprocess(image)
        batch_size = 1
        length_for_pred = torch.IntTensor([self.opt.batch_max_length] * batch_size).to(
            self.device
        )
        text_for_pred = (
            torch.LongTensor(batch_size, self.opt.batch_max_length + 1)
            .fill_(0)
            .to(self.device)
        )
        with torch.no_grad():
            if "CTC" in self.opt.Prediction:
                preds = self.model(tensor, text_for_pred)
                _, indices = preds.max(2)
                raw = self.converter.decode(
                    indices.data, torch.IntTensor([preds.size(1)])
                )
            else:
                preds = self.model(tensor, text_for_pred, is_train=False)
                _, indices = preds.max(2)
                raw = self.converter.decode(indices, torch.IntTensor([batch_size]))
        return raw[0]

    def _clean_text(self, text: str) -> str:
        txt = re.sub(r"\[s\].*", "", text)
        return " ".join([w for w in txt.split()])

    def _merge_boxes(
        self, h_boxes: List[Any], f_boxes: List[Any]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Объединяет боксы из h_boxes и f_boxes в список прямоугольников (x0, y0, x1, y1).
        Обрезает все отрицательные x0, y0 → 0, чтобы не было «выпавших» боксов.
        """
        raw_h = h_boxes[0] if h_boxes and isinstance(h_boxes[0], list) else []
        raw_f = f_boxes[0] if f_boxes and isinstance(f_boxes[0], list) else []
        merged: List[Tuple[int, int, int, int]] = []

        # горизонтальные прямоугольники
        for box in raw_h:
            x0 = max(0, int(box[0]))
            y0 = max(0, int(box[2]))
            x1 = int(box[1])
            y1 = int(box[3])
            merged.append((x0, y0, x1, y1))

        # полигональные, приводим к axis-aligned
        for poly in raw_f:
            xs = [pt[0] for pt in poly]
            ys = [pt[1] for pt in poly]
            x0 = max(0, int(min(xs)))
            y0 = max(0, int(min(ys)))
            x1 = int(max(xs))
            y1 = int(max(ys))
            merged.append((x0, y0, x1, y1))

        return merged

    def _find_gaps(self, boxes, start, end) -> List[int]:
        # собираем все перекрытия внутри [start, end]
        segs = [
            (max(b[0], start), min(b[2], end))
            for b in boxes
            if not (b[2] <= start or b[0] >= end)
        ]
        if not segs:
            return []
        segs.sort()
        # объединяем пересекающиеся
        merged = [segs[0]]
        for s, e in segs[1:]:
            ms, me = merged[-1]
            if s <= me:
                merged[-1] = (ms, max(me, e))
            else:
                merged.append((s, e))
        # находим пробелы между ними
        gaps = []
        prev_end = start
        for s, e in merged:
            if s > prev_end:
                gaps.append((prev_end, s))
            prev_end = e
        if prev_end < end:
            gaps.append((prev_end, end))
        # возвращаем центры «пустых» областей
        return [(a + b) // 2 for a, b in gaps if b - a > 1]

    def _emptiness(self, boxes, start, end) -> float:
        col = [b for b in boxes if b[0] >= start and b[2] <= end]
        if not col:
            return 1.0
        min_y, min_x = min(b[1] for b in col), max(b[3] for b in col)
        rect = (end - start) * (min_x - min_y)
        area = sum((b[2] - b[0]) * (b[3] - b[1]) for b in col)
        return (rect - area) / rect if rect else 1.0

    def _segment_columns(
        self, boxes: List[Tuple[int, int, int, int]]
    ) -> List[List[Tuple[int, int, int, int]]]:
        """
        Разбивает боксы на колонки по «пустым» вертикальным промежуткам.
        В конце отфильтровывает пустые колонки перед сортировкой.
        """
        if not boxes:
            return []

        img_width = max(b[2] for b in boxes)
        segments = [(0, img_width)]
        separators: List[int] = []

        # Находим оптимальные разрезы
        for _ in range(self.max_splits or img_width):
            best = None
            for idx, (s, e) in enumerate(segments):
                for x in self._find_gaps(boxes, s, e):
                    if not (
                        any(b[2] <= x and b[0] >= s for b in boxes)
                        and any(b[0] >= x and b[2] <= e for b in boxes)
                    ):
                        continue
                    score = self._emptiness(boxes, s, x) + self._emptiness(boxes, x, e)
                    if best is None or score < best[0]:
                        best = (score, x, idx)
            if not best:
                break
            _, x_split, idx = best
            s, e = segments.pop(idx)
            separators.append(x_split)
            segments.insert(idx, (s, x_split))
            segments.insert(idx + 1, (x_split, e))
            segments.sort()

        # Разбиваем по найденным разделителям
        parts = [(0, img_width)]
        for x in separators:
            new_parts: List[Tuple[int, int]] = []
            for s, e in parts:
                if s < x < e:
                    new_parts += [(s, x), (x, e)]
                else:
                    new_parts.append((s, e))
            parts = new_parts

        # Формируем колонки
        cols: List[List[Tuple[int, int, int, int]]] = []
        for s, e in parts:
            col = [b for b in boxes if b[0] >= s and b[2] <= e]
            cols.append(col)

        # Убираем пустые колонки
        cols = [c for c in cols if c]
        if not cols:
            return []

        # Сортируем по x-координате левого края
        return sorted(cols, key=lambda c: min(b[0] for b in c))

    def _sort_boxes_reading_order(self, boxes) -> List[Tuple[int, int, int, int]]:
        if not boxes:
            return []
        avg_h = np.mean([b[3] - b[1] for b in boxes])
        lines = []
        for b in sorted(boxes, key=lambda b: (b[1] + b[3]) / 2):
            cy = (b[1] + b[3]) / 2
            placed = False
            for ln in lines:
                line_cy = np.mean([(v[1] + v[3]) / 2 for v in ln])
                if (
                    abs(cy - line_cy) <= avg_h * self.y_tol_ratio
                    and b[0] - max(v[2] for v in ln) < avg_h * self.x_gap_ratio
                ):
                    ln.append(b)
                    placed = True
                    break
            if not placed:
                lines.append([b])
        lines.sort(key=lambda ln: np.mean([(v[1] + v[3]) / 2 for v in ln]))
        for ln in lines:
            ln.sort(key=lambda v: v[0])
        return [v for ln in lines for v in ln]

    def _sort_boxes_reading_order_with_resolutions(
        self, boxes: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Сортирует боксы с учетом сжатых размеров для правильной сортировки, но возвращает
        оригинальные размеры боксов.
        """
        # 1) Сначала разрешим пересечения (сожмем боксы)
        compressed_boxes = self._resolve_intersections(boxes)

        # 2) Теперь сортируем сжатыми размерами
        sorted_compressed_boxes = self._sort_boxes_reading_order(compressed_boxes)

        # 3) Возвращаем оригинальные боксы в том порядке, в котором они были отсортированы
        return [boxes[compressed_boxes.index(b)] for b in sorted_compressed_boxes]
