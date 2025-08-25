# Poker Tracker (PLO4)

Have you ever wondered how many of the `7566` possible PLO hands you've won with?

Well, that's what this program is for.

### Usage

1. Export all the logs from `<poker website>`, and unzip them into this project folder, under `/data/<folder name>`.
2. Run `python plo4_wins_by_hand.py <folder name>` to generate a CSV of your hand data.
3. Use `python plo4_draw_hands` to draw visualizations of the hands that remain.

### Details

There are many ways to classify the suitedness of PLO hands. This program follows the general consensus conventions, outlined below, where the notation like `[3, 1]` means `3` cards of one suit and `1` of another.

1. `[4]` - Rainbow (Badugi).
2. `[3, 1]` - Tri-suited.
3. `[2, 2]` - Double-suited pure.
4. `[2, 1, 1]` - Single-suited.
5. `[1, 1, 1, 1]` - Monotone.

### License

- Feel free to use and distribute this code freely.
- Open to contributions!
- Attributing the author is appreciated: [Josiah Plett](https://plett.dev/).
