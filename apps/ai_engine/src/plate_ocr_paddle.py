"""License plate OCR using PaddleOCR (PP-OCRv5).

Drop-in experiment adapter — same interface as PlateOCR.read().
Does NOT replace PlateOCR in the live pipeline; used for benchmarking only.

Import order requirement (Windows):
    Import torch BEFORE this module. PaddleOCR 3.x depends on modelscope
    which internally imports torch. If torch's DLLs are already loaded when
    paddleocr is imported, the load succeeds. If paddle's DLLs are loaded
    first, torch's shm.dll loader fails with WinError 127.

    This module defers the `from paddleocr import PaddleOCR` import to
    PlateOCRPaddle.__init__() so callers control the import order.

oneDNN workaround (Windows CPU):
    PaddleOCR 3.x enables oneDNN (MKLDNN) by default, which triggers a
    NotImplementedError on some Windows CPU configurations. We patch
    paddle.inference.create_predictor to call config.disable_onednn()
    before every predictor is created. The patch is applied once when
    PlateOCRPaddle is first instantiated.

    Set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True (default in this module)
    to skip the connectivity probe on startup.
"""

from __future__ import annotations

import os
import re

import numpy as np

# Disable connectivity probe for faster startup (~2 s saved per process)
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

_ONEDNN_PATCHED = False


def _patch_paddle_disable_onednn() -> None:
    """Monkey-patch paddle.inference.create_predictor to disable oneDNN.

    Called once on first PlateOCRPaddle instantiation.
    """
    global _ONEDNN_PATCHED
    if _ONEDNN_PATCHED:
        return
    try:
        import paddle.inference as paddle_infer

        _orig = paddle_infer.create_predictor

        def _patched(config):  # type: ignore[override]
            try:
                config.disable_onednn()
            except Exception:
                pass
            return _orig(config)

        paddle_infer.create_predictor = _patched  # type: ignore[assignment]
        _ONEDNN_PATCHED = True
    except Exception:
        pass


class PlateOCRPaddle:
    """Read license plate text from a cropped plate image using PaddleOCR.

    Compatible interface with PlateOCR.read():
        text, confidence = ocr.read(plate_crop_bgr)

    Args:
        use_gpu: Use GPU inference. Defaults to False (CPU). Avoid True when
                 PyTorch GPU is also active — they share VRAM.
        lang:    PaddleOCR language code. 'en' covers VN plates (Latin A-Z,
                 digits 0-9).
    """

    def __init__(self, use_gpu: bool = False, lang: str = "en") -> None:
        _patch_paddle_disable_onednn()

        # Deferred import — caller must import torch before instantiating
        from paddleocr import PaddleOCR  # noqa: PLC0415

        self._ocr = PaddleOCR(
            lang=lang,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def read(self, plate_crop: np.ndarray) -> tuple[str | None, float]:
        """OCR a plate crop image.

        Returns:
            (plate_text, avg_confidence) where plate_text is [A-Z0-9] uppercase,
            or (None, 0.0) if nothing readable.
        """
        if plate_crop is None or plate_crop.size == 0:
            return None, 0.0

        try:
            result = self._ocr.predict(plate_crop)
        except Exception:
            return None, 0.0

        if not result or not result[0]:
            return None, 0.0

        rec_result = result[0]
        texts: list[str] = rec_result.get("rec_texts") or []
        scores: list[float] = rec_result.get("rec_scores") or []

        if not texts:
            return None, 0.0

        combined = "".join(texts).upper()
        combined = re.sub(r"[^A-Z0-9]", "", combined)

        avg_conf = sum(scores) / len(scores) if scores else 0.0

        return (combined if combined else None), avg_conf
