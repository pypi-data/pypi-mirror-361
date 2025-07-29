# PR #41 コードレビュー結果

## 概要
PR #41はconnecpyのエラーハンドリングをConnect Protocol仕様に準拠させる重要な修正です。全体的に良い実装ですが、いくつかの重要な問題を発見しました。

## 🚨 重大な問題

### 1. JSONパースエラーの未処理

**影響箇所:**
- `client.py` (line 91)
- `async_client.py` (line 112)

**問題のコード:**
```python
else:
    raise ConnectWireError.from_dict(
        resp.json(), resp.status_code  # ← JSON以外のレスポンスで例外!
    ).to_exception()
```

**問題点:**
サーバーがJSON以外のレスポンス（例: プレーンテキスト "Internal Server Error"）を返した場合、`resp.json()`が`JSONDecodeError`を発生させ、適切なエラーハンドリングができません。

**修正案:**
```python
else:
    try:
        error_data = resp.json()
    except Exception:
        # 非JSONレスポンスのフォールバック
        error_data = {"message": resp.text or f"HTTP {resp.status_code}"}
    
    raise ConnectWireError.from_dict(
        error_data, resp.status_code
    ).to_exception()
```

## ⚠️ 後方互換性の問題

### 2. JSONフィールド名の変更

**変更内容:**
- 旧フォーマット: `{"code": "...", "msg": "..."}`
- 新フォーマット: `{"code": "...", "message": "..."}`

**影響:**
- 新しいクライアントは古いサーバーのエラーメッセージを正しく解析できない
- 古いクライアントは新しいサーバーのエラーメッセージを正しく解析できない

**推奨対応:**
PR作者も言及している通り、一時的な互換性レイヤーの実装を検討すべきです。

## 📝 その他の指摘事項

### 3. 未使用コード
- `errors.py`の`get_status_code`メソッドが未使用になっています
- `exceptions.py`の`connecpy_error_from_intermediary`関数が古いマッピングを使用しています

### 4. テストカバレッジの不足

**不足しているテストケース:**
- 非JSONエラーレスポンスの処理
- 新旧JSONフォーマットの互換性
- 非常に長いエラーメッセージ（DoS対策）
- 並行エラー処理

### 5. 軽微な問題
- タイポ: `# Custom error codes not defined by Connec` → `Connect` (line 54 in `_protocol.py`)

## ✅ 優れている点

### アーキテクチャ
- `_protocol.py`モジュールによる適切なカプセル化
- frozenデータクラスによる不変性の確保
- Connect Protocol仕様への完全準拠

### テスト
- すべてのエラーコードに対する包括的なテスト
- 同期・非同期両方の実装をカバー
- HTTPステータスコードの検証

### パフォーマンス
- 効率的な実装で顕著なオーバーヘッドなし
- マッピング辞書のモジュールレベルでの初期化

## 推奨事項

### 必須対応
1. **JSONパースエラーの修正** - クリティカルなバグのため即座に対応が必要
2. **非JSONレスポンスのテスト追加** - エッジケースのカバー

### 推奨対応
3. **後方互換性の考慮** - 移行期間のための互換性レイヤー実装
4. **未使用コードの削除** - コードベースのクリーンアップ
5. **メッセージサイズ制限** - DoS攻撃の予防
6. **タイポの修正** - コメントの修正

## 結論

このPRはConnect Protocol準拠という重要な目標を達成していますが、JSONパースエラーのバグは修正が必要です。この問題を解決すれば、優れた改善となるでしょう。