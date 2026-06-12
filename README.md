# pygame-ce Othello

pygame-ceで実装したオセロゲームです。ローカル対戦、TCPによるRemote対戦、
複数のCPU戦略、自己対戦による盤面評価重みの学習に対応しています。

## 実行方法

```bash
uv run python -m src.othello.main
```

開始画面ではゲームモードとCPU戦略を選択できます。

- Local Player vs Player
- Server / White
- Client / Black
- Server CPU / White
- Client CPU / Black

Remote CPU vs CPUでは、ServerとClientがそれぞれ異なるCPU戦略を選択できます。

## CPUアルゴリズム一覧

| 戦略 | 主な判断基準 | 特徴 |
| --- | --- | --- |
| Random | 合法手からランダム | 最も単純で予測不能 |
| Greedy | その手で反転できる石数 | 短期的な石数を重視 |
| Corner Priority | 角、次に反転石数 | 角の安定性を重視 |
| Weighted Board | 着手位置の固定重み | 盤面上の位置を重視 |
| Learning Weighted | 学習済み線形評価値 | 対局結果から重みを更新 |
| Tabular State Value | 盤面状態ごとの記憶 | JSONに記録した状態価値を使用 |

すべての戦略は共通の`CpuStrategy` Protocolを実装します。`CpuPlayer`は具体的な
アルゴリズムを知らず、選択された戦略の`select_move()`を呼び出すだけです。

```text
CpuPlayer
    |
    +-- CpuStrategy.select_move(context)
            |
            +-- RandomCpuStrategy
            +-- GreedyCpuStrategy
            +-- CornerPriorityCpuStrategy
            +-- WeightedBoardCpuStrategy
            +-- LearningWeightedCpuStrategy
            +-- TabularStateValueCpuStrategy
```

合法手がない場合は、どの戦略も`None`を返します。ゲームモード側がこれを
`PASS`として処理します。

## 1. Random

`RandomCpuStrategy`は、現在の合法手一覧から一つを等確率で選択します。

```python
random.choice(context.legal_moves)
```

### 選択手順

1. 合法手がなければ`None`を返す
2. 合法手があればランダムに一つ選ぶ

### 特徴

- 実装が単純
- 同じ盤面でも異なる手を選ぶ
- 盤面の位置、反転石数、将来の展開は評価しない
- self-playにおける比較対象や探索的な対戦相手として利用できる

計算量は、合法手一覧が作成済みであれば概ね`O(1)`です。

## 2. Greedy

`GreedyCpuStrategy`は、その着手で直ちに反転できる相手石の数が最大の手を
選択します。

```text
score(move) = len(move.flippable_positions)
```

### 選択手順

1. 各合法手の反転可能石数を数える
2. 最大値を持つ手を選ぶ
3. 同数の場合は、合法手一覧で先に現れた手を選ぶ

### 特徴

- 直近の石数を増やしやすい
- 判断基準が明確で高速
- 角や辺の価値を考慮しない
- 序盤に石を取りすぎ、相手へ多くの合法手を与える場合がある

合法手数を`M`とした場合、選択処理は概ね`O(M)`です。

## 3. Corner Priority

`CornerPriorityCpuStrategy`は角への着手を最優先します。角が合法手にない場合は、
Greedyと同じ基準で手を選びます。

対象となる角は次の4マスです。

```text
(0, 0)  (0, 7)
(7, 0)  (7, 7)
```

実装では固定値`7`ではなく、`BOARD_SIZE - 1`を使用しています。

### 選択手順

1. 合法手を先頭から確認する
2. 角が見つかれば、その手を直ちに選ぶ
3. 角がなければ、反転石数が最大の手を選ぶ

### 特徴

- 一度置くと裏返されない角を確保しやすい
- Greedyより盤面の安定性を考慮する
- 角以外ではGreedyと同じ弱点を持つ
- 角の隣に置く危険性までは独自に評価しない

## 4. Weighted Board

`WeightedBoardCpuStrategy`は、合法手の着手位置に設定された固定重みを比較します。

```text
 100 -20  10   5   5  10 -20 100
 -20 -50  -2  -2  -2  -2 -50 -20
  10  -2   3   2   2   3  -2  10
   5  -2   2   1   1   2  -2   5
   5  -2   2   1   1   2  -2   5
  10  -2   3   2   2   3  -2  10
 -20 -50  -2  -2  -2  -2 -50 -20
 100 -20  10   5   5  10 -20 100
```

### 重みの意図

- 角: `100`
  - 裏返されないため、最も高く評価する
- 角の斜め隣: `-50`
  - 相手に角を与えやすいため、大きく減点する
- 角の縦横隣: `-20`
  - 同様に角を奪われる危険がある
- その他の辺: `5`または`10`
  - 中央より安定しやすいため加点する
- 中央付近: `1`から`3`
  - 序盤の候補として小さな正の値を与える

### 選択手順

1. 各合法手の着手位置に対応する重みを取得する
2. 位置重みが最大の手を選ぶ
3. 同点の場合は、反転石数が多い手を選ぶ
4. それも同じ場合は、合法手一覧で先に現れた手を選ぶ

評価キーは次のタプルです。

```text
(position_weight, flippable_count)
```

この戦略の重みは固定であり、対局結果によって変化しません。

## 5. Learning Weighted

`LearningWeightedCpuStrategy`は、盤面から抽出した特徴量と学習済み重みを使って
次盤面を評価します。外部MLライブラリやニューラルネットワークは使用せず、
線形評価関数、TD(0)、ε-greedyで構成しています。

### 線形評価関数

盤面状態`s`の評価値を次の式で計算します。

```text
V(s) = w · φ(s)
```

- `V(s)`: 指定プレイヤー視点の盤面評価値
- `w`: 学習対象の重みベクトル
- `φ(s)`: 盤面から抽出した特徴量ベクトル

重みと特徴量は、それぞれ6要素です。

### 特徴量

| 番号 | 特徴量 | 計算方法 |
| --- | --- | --- |
| 1 | Bias | 常に`1.0` |
| 2 | 石数差 | `(自分の石数 - 相手の石数) / 64` |
| 3 | 合法手数差 | `(自分の合法手数 - 相手の合法手数) / 32` |
| 4 | 角数差 | `(自分の角数 - 相手の角数) / 4` |
| 5 | 辺数差 | `(自分の辺数 - 相手の辺数) / 24` |
| 6 | 位置スコア差 | `Weighted Boardの重み付き合計差 / 400` |

辺数には角を含めません。各差分は値の規模を揃え、学習時の数値発散を抑える
ために正規化しています。

### 着手評価

各合法手について、実際の盤面を変更せずに次盤面を作成します。

```text
現在盤面
  -> 合法手を仮想的に適用
  -> 次盤面の特徴量を抽出
  -> V(next_state)を計算
```

仮想盤面の作成は`core/move_simulator.py`が担当します。

### ε-greedy

既知の高評価手だけを選び続けると、新しい手を試せません。そのため、
次のε-greedy方式を使用します。

```text
確率 epsilon     : ランダムな合法手を選択
確率 1 - epsilon : 評価値が最大の合法手を選択
```

デフォルトの`epsilon`は`0.1`です。約10%の手でランダム探索を行います。

### TD(0)による更新

対局中は黒と白それぞれの着手前特徴量を記録します。対局終了後、各色の履歴を
終局側からTD(0)で更新します。

```text
delta = reward + gamma * V(next_state) - V(current_state)

w = w + learning_rate * delta * features
```

終局状態では次状態が存在しないため、`V(next_state) = 0`です。

デフォルト設定は次のとおりです。

| 設定 | 値 | 意味 |
| --- | --- | --- |
| `learning_rate` | `0.01` | 1回の更新で重みを変える割合 |
| `gamma` | `0.95` | 将来の評価を現在へ反映する割合 |
| `epsilon` | `0.1` | ランダム探索を行う確率 |

### 終局報酬

報酬は各プレイヤーの視点で決定します。

```text
勝ち   : +1.0
引き分け:  0.0
負け   : -1.0
```

終局直前の状態には勝敗報酬を与え、それ以前の状態には中間報酬`0.0`を与えて
次状態の評価を伝播させます。

### 重みの保存

学習後の重みは次のファイルへ保存されます。

```text
data/othello_rl_weights.json
```

保存形式:

```json
{
  "version": 1,
  "weights": [0.0, 0.1, -0.2, 0.5, 0.3, 0.1]
}
```

- `data/`が存在しない場合は自動作成する
- ファイルが存在しない場合は6個の`0.0`を初期重みとして使用する
- JSONが壊れている場合は初期重みへ復旧する
- 重み数が6個でない場合も初期重みへ復旧する
- 対局終了時に更新後の重みを保存する

## 6. Tabular State Value

`TabularStateValueCpuStrategy`は、特徴量へ圧縮せず、盤面状態ごとの価値を
JSONテーブルへ直接記憶します。UIから選択した場合は学習済みテーブルを読む
推論専用として動作し、対局中にtrainingやJSON更新は行いません。

```text
V(state_key) = 状態価値テーブルに保存された浮動小数点値
```

### 盤面状態キー

状態キーには評価視点のプレイヤーと64マスの内容を含めます。

```text
BLACK:EEEEEEEE/EEEEEEEE/EEEEEEEE/EEEWBEEE/EEEBWEEE/EEEEEEEE/EEEEEEEE/EEEEEEEE
```

| マス | 文字 |
| --- | --- |
| 空 | `E` |
| 黒 | `B` |
| 白 | `W` |

同じ盤面でも`BLACK:`と`WHITE:`は別状態として記憶します。現在は回転・反転に
よる正規化を行っていないため、対称な盤面も個別のキーになります。

### 着手選択

1. 合法手ごとに仮想的な次盤面を作る
2. 次盤面を状態キーへ変換する
3. JSONテーブルから価値を取得する
4. ε-greedyでランダム手または価値最大手を選ぶ

未知の状態キーは`0.0`として扱います。

### Tabular TD(0)

状態価値は次の式で更新します。

```text
delta = reward + gamma * V(next_state) - V(current_state)

V(current_state) =
    V(current_state) + learning_rate * delta
```

終局状態では`next_state`を`None`とし、`V(next_state) = 0.0`とします。
勝敗報酬は勝ち`+1.0`、引き分け`0.0`、負け`-1.0`です。

### 状態価値JSON

デフォルトの保存先:

```text
data/othello_state_values.json
```

```json
{
  "version": 2,
  "states": {
    "BLACK:EEEEEEEE/EEEEEEEE/EEEEEEEE/EEEWBEEE/EEEBWEEE/EEEEEEEE/EEEEEEEE/EEEEEEEE": {
      "value": 0.42,
      "visits": 18
    }
  }
}
```

- 未知状態は`0.0`
- 未知状態の訪問回数は`0`
- TD更新ごとに対象状態の`visits`を1増やす
- ファイルが存在しない、またはJSONが壊れている場合は空テーブルを使用
- 旧version 1は`visits=1`として読み込み可能
- 保存時に親ディレクトリを自動作成
- 一時ファイルへ書き込み後、`Path.replace()`で置換

## Parallel Training CLI

self-play trainingはpygame UIからは実行できません。次のCLIだけがtrainingを
開始できます。

```bash
uv run python -m src.othello.train \
  --strategy tabular-state-value \
  --games 10000 \
  --workers 4 \
  --output-dir data/training_shards
```

`--games`は全worker合計の対局数です。ゲーム数はworkerへ均等に分配され、
余りはworker番号が小さい順に1局ずつ追加されます。

```text
data/training_shards/
├── state_values_worker_0.json
├── state_values_worker_1.json
├── state_values_worker_2.json
└── state_values_worker_3.json
```

各workerは別processで独立した`StateValueStore`を使用します。同じJSONへ
同時書き込みしないため、process間のロックや共有メモリは使用しません。

再現可能なseedを指定する例:

```bash
uv run python -m src.othello.train \
  --strategy tabular-state-value \
  --games 1000 \
  --workers 4 \
  --output-dir data/training_shards \
  --seed 42
```

### CLI引数

| 引数 | デフォルト | 説明 |
| --- | --- | --- |
| `--strategy` | 必須 | 現在は`tabular-state-value`のみ |
| `--games` | `100` | 全worker合計の自己対戦回数 |
| `--workers` | `1` | self-playを実行するprocess数 |
| `--output-dir` | `data/training_shards` | worker shardの保存先 |
| `--learning-rate` | `0.1` | TD更新の学習率 |
| `--gamma` | `0.95` | 将来価値の割引率 |
| `--epsilon` | `0.1` | ランダム探索率 |
| `--save-every` | `100` | 各workerがshardを保存する対局間隔 |
| `--seed` | ランダム | worker seedの基準値 |
| `--log-level` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`から選択 |
| `--debug` | 無効 | DEBUGコンソール・ファイルログを有効化 |
| `--quiet` | 無効 | WARNING以上だけを出力 |
| `--progress-interval` | `100` | workerごとの進捗ログ出力間隔 |

training CLIはpygameとsocketを使用しません。`GameEngine`、
`TabularStateValueCpuStrategy`、状態価値テーブルだけで黒CPUと白CPUの
self-playを進めます。workerのseedは`base_seed + worker_id`です。

通常のtrainingでは1手ごと、各合法手、各状態価値、TD更新の詳細を出力せず、
開始・保存・指定間隔の勝敗集計・終了だけをINFOで表示します。詳細確認時だけ
`--debug`を指定してください。`--quiet`は他のログ指定より優先されます。

```bash
# 10局だけ詳細ログを確認
uv run python -m src.othello.train \
  --strategy tabular-state-value \
  --games 10 \
  --workers 1 \
  --debug

# WARNING以上だけを表示
uv run python -m src.othello.train \
  --strategy tabular-state-value \
  --games 1000 \
  --workers 4 \
  --quiet
```

## Merge CLI

並列training後はshardを別CLIで統合します。

```bash
uv run python -m src.othello.merge_state_values \
  --input-dir data/training_shards \
  --output data/othello_state_values.json
```

同じ状態キーが複数shardにある場合、訪問回数による加重平均を使用します。

```text
merged_value =
    sum(value_i * visits_i) / sum(visits_i)

merged_visits = sum(visits_i)
```

合計訪問数が`0`の場合、統合後の価値は`0.0`です。version 2以外のJSONや
壊れたファイルは警告ログを出してスキップします。統合結果も一時ファイルを
経由して安全に保存します。

merge CLIもデフォルトはINFOで、DEBUGログをファイルへ出しません。
`--log-level`、`--debug`、`--quiet`はtraining CLIと同じ意味で使用できます。

## Remote CPU vs CPU

Learning WeightedとTabular State ValueはRemote CPU vs CPUでも選択できます。

- Server側とClient側は、それぞれローカルのJSONファイルを使用する
- Tabular CPUはmerge済みの`data/othello_state_values.json`を読み込む
- 学習重み、状態価値、特徴量は相手へ送信しない
- Remote対戦中にTabular trainingは実行しない
- CPUの着手は通常の`HIT`として送信する
- 合法手がなければ通常の`PASS`を送信する

通信コマンドは次の4種類だけです。

```text
START
OK
HIT
PASS
```

通信JSON形式も変更していません。

```json
{"command": "HIT", "col": 3, "row": 2}
```

ServerとClientで同じ学習結果を使用したい場合は、対応するJSONファイルを
手動でコピーしてください。

## 実装ファイル

```text
src/othello/players/cpu/
├── cpu_strategy.py
├── random_strategy.py
├── greedy_strategy.py
├── corner_priority_strategy.py
├── weighted_board_strategy.py
├── learning_weighted_strategy.py
├── tabular_state_value_strategy.py
├── cpu_strategy_factory.py
└── rl/
    ├── board_state_key.py
    ├── feature_extractor.py
    ├── state_value_store.py
    ├── tabular_td_learner.py
    ├── td_evaluator.py
    ├── weight_store.py
    ├── training_config.py
    └── self_play_trainer.py
```

CLIエントリーポイントは`src/othello/train.py`です。
mergeエントリーポイントは`src/othello/merge_state_values.py`です。

並列trainingとmerge処理は`src/othello/training/`へ分離されています。

## 品質確認

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run python -m unittest discover -s tests -v
```
