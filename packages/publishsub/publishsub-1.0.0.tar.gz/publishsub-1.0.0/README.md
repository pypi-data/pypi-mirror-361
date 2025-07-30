# publishsub

**Python用の依存関係ゼロ軽量パブリッシュ/サブスクライブメッセージングライブラリ**

ゲーム、GUIアプリケーション、並列処理通信に最適なシンプルで高速、依存関係のないpub/subライブラリです。

## 特徴

- 🚀 **依存関係ゼロ** - 外部ライブラリ不要
- 🧵 **スレッドセーフ** - マルチスレッドアプリケーションで安全に使用可能
- 🔄 **メモリ効率** - 弱参照を使用してメモリリークを防止
- 🎯 **シンプルAPI** - 最小限のセットアップで簡単に使用可能
- 🔍 **デバッグサポート** - 組み込みデバッグ機能
- 📦 **軽量** - 最小限のオーバーヘッドで高速パフォーマンス

## インストール

```bash
pip install publishsub
```

## クイックスタート

```python
import publishsub as pubsub

# イベントハンドラを定義
def on_player_join(data):
    print(f"プレイヤー {data['name']} がゲームに参加しました！")

def on_game_over(data):
    print(f"ゲーム終了！最終スコア: {data['score']}")

# イベントを購読
pubsub.subscribe("player_join", on_player_join)
pubsub.subscribe("game_over", on_game_over)

# イベントを発行
pubsub.publish("player_join", {"name": "Alice", "id": 123})
pubsub.publish("game_over", {"score": 9500, "winner": "Alice"})
```

## 高度な使用法

### クラスインスタンスの使用

```python
from publishsub import PubSub

# 独自のインスタンスを作成
ps = PubSub()

# 購読してサブスクリプションIDを取得
sub_id = ps.subscribe("my_event", lambda data: print(data))

# イベントを発行
ps.publish("my_event", "Hello World!")

# IDを使用して購読解除
ps.unsubscribe("my_event", sub_id)
```

### イベント管理

```python
import publishsub as pubsub

# 購読者数を確認
count = pubsub.subscribers_count("my_event")
print(f"イベントの購読者数: {count}")

# 購読者のいるすべてのイベントを一覧表示
events = pubsub.list_events()
print(f"アクティブなイベント: {events}")

# 特定のイベントの購読者をクリア
pubsub.clear("my_event")

# すべての購読者をクリア
pubsub.clear()
```

### デバッグモード

```python
import publishsub as pubsub

# デバッグログを有効にする
pubsub.enable_debug(True)

# すべての操作がログに記録される
pubsub.subscribe("debug_event", lambda x: print(x))
pubsub.publish("debug_event", "デバッグ情報が表示されます")
```

## 使用例

### ゲーム開発

```python
import publishsub as pubsub

# ゲームイベント
def on_enemy_spawn(enemy_data):
    print(f"敵が出現: {enemy_data['type']}")

def on_player_damage(damage_data):
    print(f"プレイヤーが {damage_data['amount']} ダメージを受けました")

# ゲームイベントを購読
pubsub.subscribe("enemy_spawn", on_enemy_spawn)
pubsub.subscribe("player_damage", on_player_damage)

# ゲームループ内で
pubsub.publish("enemy_spawn", {"type": "ゴブリン", "x": 100, "y": 200})
pubsub.publish("player_damage", {"amount": 25, "source": "ゴブリン"})
```

### GUIアプリケーション

```python
import publishsub as pubsub

# UIイベントハンドラ
def on_button_click(data):
    print(f"ボタン {data['button_id']} がクリックされました")

def on_window_resize(data):
    print(f"ウィンドウサイズが {data['width']}x{data['height']} に変更されました")

# UIイベントを購読
pubsub.subscribe("button_click", on_button_click)
pubsub.subscribe("window_resize", on_window_resize)

# UIコードで
pubsub.publish("button_click", {"button_id": "save_btn"})
pubsub.publish("window_resize", {"width": 800, "height": 600})
```

### 並列処理

```python
import publishsub as pubsub
import threading

# ワーカー間通信
def on_task_complete(data):
    print(f"タスク {data['task_id']} がワーカー {data['worker_id']} によって完了")

def on_error(data):
    print(f"タスク {data['task_id']} でエラー: {data['error']}")

# ワーカーイベントを購読
pubsub.subscribe("task_complete", on_task_complete)
pubsub.subscribe("error", on_error)

# ワーカースレッドで
def worker_thread(worker_id):
    # ... 作業を実行 ...
    pubsub.publish("task_complete", {"task_id": 123, "worker_id": worker_id})

# ワーカーを開始
for i in range(3):
    threading.Thread(target=worker_thread, args=(i,)).start()
```

## APIリファレンス

### 関数

#### `subscribe(event: str, callback: Callable) -> str`
コールバック関数でイベントを購読します。
- **event**: 購読するイベント名
- **callback**: イベントが発行されたときに呼び出される関数
- **戻り値**: 購読解除に使用するサブスクリプションID

#### `unsubscribe(event: str, subscription_id: str) -> bool`
サブスクリプションIDを使用してイベントの購読を解除します。
- **event**: イベント名
- **subscription_id**: subscribe()によって返されたサブスクリプションID
- **戻り値**: 購読解除に成功した場合True

#### `publish(event: str, data: Any = None) -> int`
オプションのデータでイベントを発行します。
- **event**: 発行するイベント名
- **data**: イベントと一緒に送信するオプションのデータ
- **戻り値**: イベントを受信した購読者数

#### `subscribers_count(event: str) -> int`
イベントのアクティブな購読者数を取得します。
- **event**: イベント名
- **戻り値**: アクティブな購読者数

#### `list_events() -> List[str]`
購読者のいるすべてのイベントのリストを取得します。
- **戻り値**: イベント名のリスト

#### `clear(event: Optional[str] = None) -> None`
イベントのすべての購読者をクリアします。イベントが指定されない場合はすべてクリアします。
- **event**: クリアする特定のイベント、またはすべてをクリアする場合はNone

#### `enable_debug(enable: bool = True) -> None`
デバッグログを有効または無効にします。
- **enable**: デバッグログを有効にする場合True、無効にする場合False

## スレッドセーフ

このライブラリは完全にスレッドセーフで、追加の同期なしにマルチスレッドアプリケーションで使用できます。

## メモリ管理

ライブラリはコールバックに弱参照を使用してメモリリークを防ぎます。購読されたメソッドを持つオブジェクトがガベージコレクションされると、それらの購読は自動的にクリーンアップされます。

## パフォーマンス

- **軽量**: 最小限のメモリフットプリント
- **高速**: 高頻度なイベント発行に最適化
- **スケーラブル**: 数千のイベントと購読者を効率的に処理

## ライセンス

MIT License - 詳細はLICENSEファイルをご覧ください。

## 貢献

貢献を歓迎します！プルリクエストをお気軽にお送りください。

## 作者

[tikipiya](https://github.com/tikipiya)が作成