# Команда B. Набір задач

Тексти задач подано англійською мовою навмисно (див. план заняття).

## Формат відповіді

Every pipeline (monolithic and hybrid) must return JSON of this shape:

```json
{"status": "unique | multiple | none | optimal",
 "solution": { "...": "..." },
 "objective": 0}
```

- `unique` — exactly one solution exists; give it in `solution`.
- `multiple` — the conditions allow more than one solution; give any one of them (or a list).
- `none` — no solution satisfies all conditions; leave `solution` empty.
- `optimal` — for optimisation problems; give the best solution and its value in `objective`.

The exact shape of `solution` for each problem is given in its **Answer format** line
(and in the `answer_format` field of `problems.json`). Follow it exactly — the evaluation script compares
keys and values literally (case and surrounding spaces are ignored).



## Задача B1. Canteen queue

Five people stand in a queue at the canteen, positions 1 (front) to 5 (back): Artem, Bohdana, Viktor, Halyna and Dmytro.
1. Viktor is somewhere in front of Halyna.
2. Artem stands directly behind Bohdana.
3. Dmytro is either at the very front or at the very back.
4. Halyna is not at the back.
5. Bohdana is not at the front.

What is the order of the queue?

**Answer format.** Put into "solution" an object that maps each of "Artem", "Bohdana", "Viktor", "Halyna", "Dmytro" to their position in the queue (integer, 1 = front).


## Задача B2. Cryptarithm

In the addition below, each letter stands for a different digit, and no number starts with 0:

    NODE
  + EDGE
  ------
   GRAPH

Additional conditions:
1. The digit 0 does not appear anywhere.
2. NODE is an even number.
3. O is greater than N.
4. A stands for the largest digit that appears in the puzzle.

Find the digit for every letter.

**Answer format.** Put into "solution" an object that maps each of "N", "O", "D", "E", "G", "R", "A", "P", "H" to its digit (integer 0–9).


## Задача B3. Meeting week

Six meetings — Planning, Design review, Budget, Hiring, Security review and Retro — take place from Monday to Wednesday. Each day has a morning slot and an afternoon slot, and each meeting takes one slot; all six slots are used.
1. Retro is the last meeting of the week.
2. Planning and Design review are on the same day, with Planning first.
3. Budget is held in a morning slot.
4. Security review is held on the day after Budget.
5. Hiring is not on Monday.
6. Budget is not on the same day as Planning.

Which slot does each meeting take?

**Answer format.** Put into "solution" an object that maps each of "Planning", "Design review", "Budget", "Hiring", "Security review", "Retro" to its slot ("Mon morning", "Mon afternoon", "Tue morning", "Tue afternoon", "Wed morning", "Wed afternoon").


## Задача B4. Siblings' ages

Four siblings — Ivan, Kateryna, Taras and Sofiia — are all of different ages; each age is a whole number of years between 1 and 30.
1. Kateryna is twice as old as Taras.
2. Ivan is 3 years older than Kateryna.
3. Sofiia is the youngest.
4. Their ages add up to 43.

How old is each sibling?

**Answer format.** Put into "solution" an object that maps each of "Ivan", "Kateryna", "Taras", "Sofiia" to their age (integer).


## Задача B5. Drinks

Olena, Petro and Maria each ordered a different drink: tea, coffee or juice.
1. Olena did not order tea.
2. Petro did not order coffee.
3. Maria ordered neither coffee nor juice.

Who ordered what?

**Answer format.** Put into "solution" an object that maps each of "Olena", "Petro", "Maria" to their drink ("tea", "coffee", "juice").
