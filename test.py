import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import joblib
import librosa
import numpy as np
import os

#一応バージョンつけとく
version = "ver1.0"

#画像の切り替え
index = 0
# モデルとLabelEncoderを読み込む
loaded_model = joblib.load('./modelData/model.pkl')
loaded_encoder = joblib.load('./modelData/encoder.pkl')

label_dic = {0:"Bass",1:"FX",2:"Lead",3:"Pad",4:"Pluck",5:"Stab"}
label_list=[[0,"Bass"],[0,"FX"],[0,"Lead"],[0,"Pad"],[0,"Pluck"],[0,"Stab"]]

max_length = int(44100 * 2)  # 今回は2秒でパディングするので、44100Hz*2秒=88200

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

def drop(event):  # ドロップされた時の処理
    filepath = event.data.strip("{}").replace("/", "\\")
    ext = os.path.splitext(filepath)[-1].lower()
    if ext not in [".mp3", ".wav"]:
        text.delete('1.0', tk.END)
        text.insert(tk.END, f'{ext}タイプの拡張子は対応していません\nmp3形式か、wav形式のファイルをドロップしてください\n')
    else:
        global dropped_filepath
        global index
        dropped_filepath = filepath
        text.delete('1.0', tk.END)
        text.insert(tk.END, f'予測の準備ができました！\n{filepath}\n')
        index=(index+1) % len(photos)
        canvas.delete('p1')	# 画像を削除
        canvas.create_image(0, 0, image=photos[index], anchor=tk.NW,tag = "p1")  # 予測中画像に変更

def predict():  # 予想関数
    result = sound_to_predict(dropped_filepath)
    global index
    index=(index+1) % len(photos)
    canvas.delete('p1')	# 画像を削除
    canvas.create_image(0, 0, image=photos[index], anchor=tk.NW,tag = "p1")  # 予測中画像に変更
    name = os.path.basename(dropped_filepath)
    print(result,"result")
    result = result_comment(result)
    text.delete('1.0', tk.END)
    text.insert(tk.END, f'{name}は{level(result[0][0])}{result[0][1]}に使えそうですね～\nもしかしたら{result[1][1]}にも使えるかもしれません！\n')

def result_comment(result): # 確率の高い順に並べてリスト化
    predict_list = label_list.copy()
    for i in range(len(result[0])):
        predict_list[i][0] = result[0][i]
    predict_list.sort(reverse=True)
    result = predict_list
    return result
def level(point):   # 確率をレベルに変換する（0.8以上で最高、0.6以上で高い、0.4以上で普通、0.2以上で低い、0.2未満で最低）
    if point >= 0.8:
        return "かなり"
    elif point >= 0.6:
        return "けっこう"
    elif point >= 0.4:
        return "普通に"
    elif point >= 0.2:
        return "ちょっと"
    else:
        return "あまり自信がないですが…"
root = TkinterDnD.Tk()
root.withdraw()  # tkinterのウィンドウを一時的に隠す

#画像の取得
photos=[
	tk.PhotoImage(file="./predict.png", width=300, height=500),
	tk.PhotoImage(file="./thinking.png", width=300, height=500)
]

root.title('音源診断！ : '+version) # 画面タイトル設定
root.geometry('500x500')  # 画面サイズ設定
root.resizable(False, False)# リサイズ固定

label = tk.Label(root, text="音源ファイルをランダムフォレストちゃんにドラッグ＆ドロップしてください")
label.pack()

image = tk.PhotoImage(file="./thinking.png", width=300, height=300)
canvas = tk.Canvas(root, name='drag_and_drop_frame', width=300, height=300, bg='grey')
canvas.create_image(0, 0, image=photos[index], anchor=tk.NW,tag = "p1")
canvas.pack()

# フレームにドロップ操作をバインド
canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', drop)

predict_button = tk.Button(root, text="予想してもらう！", command=predict)  # 決定ボタン
predict_button.pack()

text = tk.Text(root, height=10, font=("TkDefaultFont", 15))
text.pack()

root.update()
root.deiconify()  # tkinterのウィンドウを再表示
root.mainloop()
