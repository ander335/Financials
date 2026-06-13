"""
Screenshot sheets from an .xlsm workbook using the Windows PrintWindow API.

Usage:
    python xlsm_screenshot.py <workbook.xlsm> <output_dir> [sheet1 sheet2 ...]

    If no sheet names are given, all sheets are captured.
"""

import sys
import time
import pathlib
import ctypes

import win32com.client as win32
import win32gui
import win32con
import win32ui
from PIL import Image


def capture_window(hwnd: int) -> Image.Image:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc  = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bmp     = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfc_dc, w, h)
    save_dc.SelectObject(bmp)

    ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

    info = bmp.GetInfo()
    img  = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                            bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    win32gui.DeleteObject(bmp.GetHandle())
    return img


def screenshot_sheets(xlsm_path: str, out_dir: str, sheet_names: list[str] | None = None):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    excel = win32.DispatchEx("Excel.Application")
    excel.Visible       = True
    excel.DisplayAlerts = False

    try:
        wb      = excel.Workbooks.Open(str(pathlib.Path(xlsm_path).resolve()),
                                       UpdateLinks=False, ReadOnly=True)
        targets = sheet_names or [wb.Worksheets(i).Name
                                  for i in range(1, wb.Worksheets.Count + 1)]

        excel.WindowState = -4137  # xlMaximized
        hwnd = excel.Hwnd
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        time.sleep(1.5)

        for name in targets:
            wb.Worksheets(name).Activate()
            excel.ActiveWindow.Zoom = 80
            time.sleep(0.5)
            capture_window(hwnd).save(str(out / f"{name}.png"))
            print(f"  {name}.png")

        wb.Close(False)
    finally:
        excel.Quit()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    xlsm_path   = sys.argv[1]
    out_dir     = sys.argv[2]
    sheet_names = sys.argv[3:] or None

    screenshot_sheets(xlsm_path, out_dir, sheet_names)


if __name__ == "__main__":
    main()
