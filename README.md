# Vertex reconstructed for TradingView

This repository contains a clean-room, output-equivalent reconstruction of the
Vertex oscillator. It was derived from user-provided OHLC and indicator output,
without access to the original protected source code.

The supplied Excel export contains 13,303 rows. With the screenshot defaults,
all four reconstructed series match every comparable exported value within the
workbook's two-decimal rounding precision.

| Series | Comparable rows | Mean absolute error | Maximum error | Within ±0.00501 |
| --- | ---: | ---: | ---: | ---: |
| Control | 13,303 | 0.002480878 | 0.004999422 | 100% |
| Signal | 13,299 | 0.002493430 | 0.004999787 | 100% |
| Upper band | 13,292 | 0.002501955 | 0.004999645 | 100% |
| Lower band | 13,292 | 0.002494906 | 0.004999580 | 100% |

Machine learning was not used. A deterministic formula already reproduces the
export at its full displayed precision, while an ML approximation would add
unnecessary error and overfitting risk.

## TradingView installation

1. Open TradingView's Pine Editor.
2. Copy all code from [`src/Vertex_Reconstructed.pine`](src/Vertex_Reconstructed.pine).
3. Save the script and select **Add to chart**.
4. Keep **Match exported Vertex (one-bar delay)** enabled for the verified behavior.

The default inputs match the supplied screenshots:

| Input | Default |
| --- | ---: |
| `Control_Period` | 14 |
| `Signal_Period` | 5 |
| `Signal_Method` | SMA |
| `BB_Up_Period` / `BB_Up_Deviation` | 12 / 2 |
| `BB_Dn_Period` / `BB_Dn_Deviation` | 12 / 2 |
| `LevelOb` / `LevelOs` | 6 / -6 |
| `ExtremelevelOb` / `ExtremelevelOs` | 10 / -10 |

Red is the control line, blue is the signal line, and gray is used for the
upper and lower Vertex bands.

## Reconstructed calculation

For each chart bar, exact-match mode scans the previous 14 completed bars from
newest to oldest:

1. Add a bar's close to `upSum` when its high is a new running high.
2. Add a bar's close to `downSum` when its low is a new running low.
3. Calculate `control = downSum / upSum - upSum / downSum`.
4. Calculate the signal as a five-value simple moving average of control.
5. Calculate each band from a 12-value SMA plus or minus two population
   standard deviations of control.

The one-bar delay is part of the observed export behavior and also prevents the
control value from changing intrabar.

## Strategy integration

The indicator exposes `longReversal` and `shortReversal` conditions, numeric
flags in the Data Window, and alert conditions. The optional reversal logic
arms after control reaches the corresponding band or ±6 level, then confirms
when control crosses the signal line in the reversal direction.

Treat those confirmations as inputs to your own strategy rules. Position sizing,
stops, targets, market filters, slippage, and commissions are intentionally not
hard-coded because they were not present in the source export.

## Re-run the Excel validation

```bash
python -m pip install -r requirements.txt
python tools/validate_vertex.py "/path/to/data vertex-1.xlsx"
```

The validator accepts `.xlsx`, `.xlsm`, and `.csv`. It expects newest-first rows
by default, matching the supplied workbook. Use `--chronology ascending` for an
oldest-first export.

Run the dependency-free unit tests with:

```bash
python -m unittest discover -s tests -v
```

## Limitations

- The formula is verified against the supplied symbol, timeframe, history, and
  two-decimal exported outputs. This proves output equivalence for that dataset,
  not the identity of the original implementation.
- SMA signal behavior is verified. EMA, RMA, and WMA are convenience options and
  were not present in the supplied export.
- Validate signals on the market and timeframe you intend to trade. Historical
  matching does not guarantee profitability or future results.
