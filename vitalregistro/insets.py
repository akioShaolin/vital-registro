"""Overlap between a content view and the unobscured part of its window."""


def content_insets(window_size, content_bounds, safe_bounds, scale=(1, 1)):
    """Return left, top, right, bottom padding in Kivy coordinates.

    Android bounds have their origin at the top left. Bounds are relative to
    the window; safe_bounds already excludes system bars, cutouts and IME.
    Subtracting content bounds avoids padding again when Android resized it.
    """
    width, height = window_size
    left, top, right, bottom = content_bounds
    safe_left, safe_top, safe_right, safe_bottom = safe_bounds
    sx, sy = scale
    return (max(0, min(width, safe_left) - left) * sx,
            max(0, min(height, safe_top) - top) * sy,
            max(0, right - max(0, safe_right)) * sx,
            max(0, bottom - max(0, safe_bottom)) * sy)
