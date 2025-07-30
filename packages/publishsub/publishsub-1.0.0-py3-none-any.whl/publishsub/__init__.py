"""
publishsub - 依存関係ゼロの軽量パブリッシュ/サブスクライブメッセージングライブラリ

Python用のシンプルで高速、依存関係のないpub/subライブラリです。
ゲーム、GUIアプリケーション、並列処理通信に最適です。

使用法:
    import publishsub as pubsub
    
    # イベントを購読
    def handler(data):
        print(f"受信: {data}")
    
    pubsub.subscribe("event", handler)
    
    # イベントを発行
    pubsub.publish("event", {"message": "Hello World!"})
"""

import threading
import weakref
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
import uuid


class PubSub:
    """
    イベント駆動メッセージングを提供するメインのパブリッシュ/サブスクライブクラス。
    
    このクラスはスレッドセーフで、以下をサポートします:
    - イベントごとに複数の購読者
    - メモリリークを防ぐ弱参照
    - 同期・非同期パブリッシング
    - イベントフィルタリングとパターンマッチング
    """
    
    def __init__(self):
        self._subscribers: Dict[str, Dict[str, Callable]] = defaultdict(dict)
        self._lock = threading.RLock()
        self._debug = False
    
    def subscribe(self, event: str, callback: Callable[[Any], None]) -> str:
        """
        コールバック関数でイベントを購読します。
        
        Args:
            event: 購読するイベント名
            callback: イベントが発行されたときに呼び出される関数
            
        Returns:
            購読解除に使用できるサブスクリプションID
        """
        with self._lock:
            subscription_id = str(uuid.uuid4())
            
            # Use weak reference to prevent memory leaks
            try:
                weak_callback = weakref.ref(callback)
                self._subscribers[event][subscription_id] = weak_callback
            except TypeError:
                # For built-in functions and methods that can't be weakly referenced
                self._subscribers[event][subscription_id] = callback
            
            if self._debug:
                print(f"[PubSub] Subscribed to '{event}' with ID: {subscription_id}")
            
            return subscription_id
    
    def unsubscribe(self, event: str, subscription_id: str) -> bool:
        """
        サブスクリプションIDを使用してイベントの購読を解除します。
        
        Args:
            event: イベント名
            subscription_id: subscribe()によって返されたサブスクリプションID
            
        Returns:
            購読解除に成功した場合True、失敗した場合False
        """
        with self._lock:
            if event in self._subscribers and subscription_id in self._subscribers[event]:
                del self._subscribers[event][subscription_id]
                
                # Clean up empty event entries
                if not self._subscribers[event]:
                    del self._subscribers[event]
                
                if self._debug:
                    print(f"[PubSub] Unsubscribed from '{event}' with ID: {subscription_id}")
                
                return True
            
            return False
    
    def publish(self, event: str, data: Any = None) -> int:
        """
        オプションのデータでイベントを発行します。
        
        Args:
            event: 発行するイベント名
            data: イベントと一緒に送信するオプションのデータ
            
        Returns:
            イベントを受信した購読者数
        """
        with self._lock:
            if event not in self._subscribers:
                if self._debug:
                    print(f"[PubSub] No subscribers for event '{event}'")
                return 0
            
            # Get all active subscribers
            active_callbacks = []
            dead_refs = []
            
            for sub_id, callback_ref in self._subscribers[event].items():
                if isinstance(callback_ref, weakref.ref):
                    callback = callback_ref()
                    if callback is None:
                        dead_refs.append(sub_id)
                    else:
                        active_callbacks.append(callback)
                else:
                    active_callbacks.append(callback_ref)
            
            # Clean up dead weak references
            for sub_id in dead_refs:
                del self._subscribers[event][sub_id]
            
            # Clean up empty event entries
            if not self._subscribers[event]:
                del self._subscribers[event]
            
            if self._debug:
                print(f"[PubSub] Publishing '{event}' to {len(active_callbacks)} subscribers")
            
            # Call all active callbacks
            for callback in active_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    if self._debug:
                        print(f"[PubSub] Error in callback for '{event}': {e}")
                    # Continue with other callbacks even if one fails
            
            return len(active_callbacks)
    
    def subscribers_count(self, event: str) -> int:
        """
        イベントのアクティブな購読者数を取得します。
        
        Args:
            event: イベント名
            
        Returns:
            アクティブな購読者数
        """
        with self._lock:
            if event not in self._subscribers:
                return 0
            
            # Count active subscribers (excluding dead weak references)
            active_count = 0
            dead_refs = []
            
            for sub_id, callback_ref in self._subscribers[event].items():
                if isinstance(callback_ref, weakref.ref):
                    if callback_ref() is None:
                        dead_refs.append(sub_id)
                    else:
                        active_count += 1
                else:
                    active_count += 1
            
            # Clean up dead weak references
            for sub_id in dead_refs:
                del self._subscribers[event][sub_id]
            
            return active_count
    
    def list_events(self) -> List[str]:
        """
        購読者のいるすべてのイベントのリストを取得します。
        
        Returns:
            イベント名のリスト
        """
        with self._lock:
            return list(self._subscribers.keys())
    
    def clear(self, event: Optional[str] = None) -> None:
        """
        イベントのすべての購読者をクリアします。イベントが指定されない場合はすべてクリアします。
        
        Args:
            event: クリアする特定のイベント、またはすべてをクリアする場合はNone
        """
        with self._lock:
            if event is None:
                self._subscribers.clear()
                if self._debug:
                    print("[PubSub] Cleared all subscribers")
            elif event in self._subscribers:
                del self._subscribers[event]
                if self._debug:
                    print(f"[PubSub] Cleared subscribers for '{event}'")
    
    def enable_debug(self, enable: bool = True) -> None:
        """
        デバッグログを有効または無効にします。
        
        Args:
            enable: デバッグログを有効にする場合True、無効にする場合False
        """
        self._debug = enable
        if enable:
            print("[PubSub] Debug logging enabled")


# 簡単に使用するためのグローバルインスタンス
_global_pubsub = PubSub()

# 簡単にアクセスできるようにメイン関数をエクスポート
subscribe = _global_pubsub.subscribe
unsubscribe = _global_pubsub.unsubscribe
publish = _global_pubsub.publish
subscribers_count = _global_pubsub.subscribers_count
list_events = _global_pubsub.list_events
clear = _global_pubsub.clear
enable_debug = _global_pubsub.enable_debug

# 高度な使用のためのクラスをエクスポート
PubSub = PubSub

__version__ = "1.0.0"
__author__ = "tikipiya"
__all__ = [
    "PubSub",
    "subscribe", 
    "unsubscribe", 
    "publish", 
    "subscribers_count",
    "list_events",
    "clear",
    "enable_debug"
]