kane_tsuki
==========

鐘を突くと音っぽいものが出ます

install
==
OpenCV、pythonを入れる

OpenCVとpythonにパスを通す

kane_tsuki.pyの、
```python
sys.path.append('C:\opencv248\sources\samples\python2')
```
の箇所を各自の環境に合わせる

usage
==
kane_tsuki.py 実行

注目領域を設定する（左クリックで左上、右クリックで右下を設定)

Escで設定終了

注目領域付近で右方向に何かが動くと音が出る（はず）

Escで終了
