import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

def drop(event):
    filepath = event.data
    print(f'{filepath} was dropped.')
    # ここでscikit-learnを用いた音源分析などを実装します。

root = TkinterDnD.Tk()
root.withdraw()  # tkinterのウィンドウを一時的に隠す

frame = tk.Frame(root, name='drag_and_drop_frame', width=300, height=300)
frame.pack()

# フレームにドロップ操作をバインド
frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', drop)

root.update()
root.deiconify()  # tkinterのウィンドウを再表示
root.mainloop()
