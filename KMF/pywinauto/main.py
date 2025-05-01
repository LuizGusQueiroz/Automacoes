from pywinauto import Desktop

desktop = Desktop(backend="uia")

for w in desktop.windows():
    print(w.window_text())
