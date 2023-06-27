import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import joblib
import librosa
import numpy as np

# モデルとLabelEncoderを読み込む
loaded_model = joblib.load('./modelData/model.pkl')
loaded_encoder = joblib.load('./modelData/encoder.pkl')

label_dic = {0:"Bass",1:"FX",2:"Lead",3:"Pad",4:"Pluck",5:"Stab"}

max_length = int(44100 * 2)  # 今回は3秒でパディングするので、44100Hz*2秒=88200

def load_and_pad(file_path):#パッティング関数
    y, sr = librosa.load(file_path, sr=None)
    if len(y) > max_length:
        y = y[:max_length]  # もし長ければ切る
    else:
        y = np.pad(y, (0, max_length - len(y)))  # もし短ければ増やす
    return y

def sound_to_predict(file_path):
    file_path = file_path.strip("{}")  # 根本的解決にはならない修正
    file_path = file_path.replace("/", "\\")  # 根本的解決にはならない修正
    print(f'{file_path} was dropped.')
    # パッティング
    new_sound = load_and_pad(file_path)
    # MFCCの計算
    new_mfccs = librosa.feature.mfcc(y=new_sound, sr=44100, n_mfcc=40)
    # 2次元のリストにする
    new_data = [new_mfccs.flatten()]
    # 新しい音源の予測
    new_pred = loaded_model.predict(new_data)
    # 予測結果（数値）をジャンル名に戻す
    new_genre = loaded_encoder.inverse_transform(new_pred)
    print(new_genre)
    # 各ジャンルに適している確率を得ます
    new_proba = loaded_model.predict_proba(new_data)
    return new_proba


def drop(event):# ドロップされた時の処理
    filepath = event.data
    print(sound_to_predict(filepath))
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
