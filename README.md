# Poker Tracker (PLO4)

Have you ever wondered how many of the `7566` possible PLO hands you've won with?

Well, that's what this program is for.

<p align="center" float="left">
  <img src="/output/sample_1_week_AA_grid.png" alt="AA Grid" height="200px"/>
  <img src="/output/sample_1_week_KQ_grid.png" alt="KQ Grid" height="200px"/>
  <img src="/output/sample_1_week_A6_grid.png" alt="A6 Grid" height="200px"/>
</p>

<p align="center">
  <img src="/output/sample_1_week_J_family.png" alt="J Family" height="260px"/>
</p>

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

For the purposes of hand tracking, I have chosen to exclude monotone hands. The total number of distinct hands, then, is `6851`.

<details><summary>Reading the tables</summary>

<br>

The yellow parts of each table represents the hands with a suited pair. Each cell has two options.

- Left: single-suited (`[2, 1, 1]`)
- Right: double-suited pure (`[2, 2]`)

Similarly, the white parts of each table represent the following suitedness:

- Left: rainbow (`[1, 1, 1, 1]`)
- Right: tri-suited (`[3, 1]`)

For cells representing a pair, the cell has 4 parts not 2, with the suited pairs (in yellow) being at the top, and others below.

Impossible hand combinations are grey.

---

</details>

### License

- Feel free to use and distribute this code freely.
- Open to contributions!
- Attributing the author ([Josiah Plett](https://plett.dev/)) is appreciated.
