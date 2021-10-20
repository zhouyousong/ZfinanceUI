import pandas as pd

class SymbolSelectUIProc:
    def __init__(self, GlobalUI, APP, GlobalFavorEditorUI):
        self.GlobalMainUI = GlobalUI
        self.GlobalAPP = APP
        self.GlobalFavorEditorUI = GlobalFavorEditorUI
        self.GlobalMainUI.AddSelectableSymbols.clicked.connect(self.HandleAddSelectableSymbols)

    def HandleAddSelectableSymbols(self):
        self.GlobalFavorEditorUI.show()
        pass