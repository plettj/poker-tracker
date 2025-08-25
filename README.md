# Poker Tracker (PLO4)

Have you ever wondered how many of the `7566` possible PLO hands you've won with?

Well, that's what this program is for.

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 1em 0;">
  <img src="/output/sample_1_week_AA_grid.png" style="flex: 1 1 30%; max-width: 30%; height: auto;" />
  <img src="/output/sample_1_week_KQ_grid.png" style="flex: 1 1 30%; max-width: 30%; height: auto;" />
  <img src="/output/sample_1_week_A6_grid.png" style="flex: 1 1 30%; max-width: 35%; height: auto;" />
</div>

<div style="display: flex; justify-content: center; margin: 1em 0;">
  <img src="/output/sample_1_week_J_family.png" style="width: 100%; max-width: 98%; height: auto;" />
</div>

### Usage

1. Export all the logs from `<poker website>`, and unzip them into this project folder, under `/data/<folder name>`.
2. Run `python plo4_wins_by_hand.py <folder name>` to generate a CSV of your hand data.
3. Use `python plo4_draw_hands.py <option>` to visualize your hands!
   - `<option>`: empty, or `A`/`K`/etc., or `AA`/`KT`/etc.

### Details

There are many ways to classify the suitedness of PLO hands. This program follows the general consensus conventions, outlined below, where the notation like `[3, 1]` means `3` cards of one suit and `1` of another.

1. `[4]` - Rainbow (Badugi).
2. `[3, 1]` - Tri-suited.
3. `[2, 2]` - Double-suited pure.
4. `[2, 1, 1]` - Single-suited.
5. `[1, 1, 1, 1]` - Monotone.

Also, for the purposes of hand tracking, I have chosen to exclude monotone hands. Thus, the total number of distinct hands tracked by this program is `6851`.

### License

- Feel free to use and distribute this code freely.
- Open to contributions!
- Attributing the author ([Josiah Plett](https://plett.dev/)) is appreciated.
