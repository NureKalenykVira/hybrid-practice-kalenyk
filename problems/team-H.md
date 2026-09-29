# Команда H. Набір задач

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



## Задача H1. Project week schedule

Seven meetings — Kickoff, Hiring, Architecture, Demo, Marketing, Legal and Wrap-up — are scheduled from Monday to Thursday. Each day has a morning slot and an afternoon slot (8 slots in total); each meeting takes one slot, so exactly one slot stays empty.
1. Kickoff is the first meeting of the week.
2. Wrap-up is the last meeting of the week, and it is held in an afternoon slot.
3. Architecture and Demo take place on the same day; Architecture is in the morning.
4. Legal takes place on the day after Architecture.
5. Marketing takes place on the same day as Legal.
6. Legal is held in an afternoon slot.
7. Hiring is held in an afternoon slot, on an earlier day than Demo.

In which slot does each meeting take place, and which slot stays empty?

**Answer format.** Put into "solution" an object that maps each of "Kickoff", "Hiring", "Architecture", "Demo", "Marketing", "Legal", "Wrap-up" to its slot ("Mon morning", "Mon afternoon", "Tue morning", "Tue afternoon", "Wed morning", "Wed afternoon", "Thu morning", "Thu afternoon").


## Задача H2. Train carriages

Four passengers travel in four carriages of a short train, numbered 1 to 4; carriage 1 is at the front. "In front of" means a lower carriage number. Each passenger has a different name, destination, luggage item and book genre.

1. The person who reads a history book travels in the carriage directly in front of the person who reads fantasy.
2. Kharyton travels in carriage 2.
3. Tsvitana and the person who carries a backpack travel in neighbouring carriages.
4. Tsvitana travels somewhere in front of the person who is going to Kyiv.
5. The person who carries a suitcase travels in carriage 3.
6. The person who is going to Dnipro and Ustyna travel in neighbouring carriages.
7. The person who is going to Lviv travels somewhere in front of the person who carries a guitar case.
8. Kharyton reads poetry.
9. Kharyton and the person who is going to Kyiv travel in neighbouring carriages.
10. The person who reads a thriller and the person who is going to Lviv travel in neighbouring carriages.

For each carriage, determine the passenger, destination, luggage and book.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4" and whose values are objects with the keys "Name", "Destination", "Luggage", "Book". Use exactly these values — Name: "Ustyna", "Filip", "Kharyton", "Tsvitana"; Destination: "Kyiv", "Lviv", "Dnipro", "Uzhhorod"; Luggage: "suitcase", "backpack", "guitar case", "duffel bag"; Book: "thriller", "poetry", "history", "fantasy".


## Задача H3. Bug fixing

Four developers — Bohdan, Vira, Hlib and Daryna — together fixed 10 bugs. Each of them fixed at least one bug, and no two of them fixed the same number of bugs.
1. Bohdan fixed no more than 2 bugs.
2. Vira fixed fewer bugs than Hlib.
3. Hlib fixed at most as many bugs as Daryna.
4. Daryna fixed not fewer than 4 bugs.
5. Bohdan fixed more bugs than Vira.

How many bugs did each developer fix?

**Answer format.** Put into "solution" an object that maps each of "Bohdan", "Vira", "Hlib", "Daryna" to the number of bugs they fixed (integer).


## Задача H4. Knights and knaves (3)

On an island, knights always tell the truth and knaves always lie. You meet Taisiia, Ustym and Fedora.
Taisiia says: "All three of us are knaves."
Ustym says: "Exactly one of us three is a knight."
Fedora says: "Ustym is a knave."

Who is a knight and who is a knave?

**Answer format.** Put into "solution" an object that maps each of "Taisiia", "Ustym", "Fedora" to "knight" or "knave".


## Задача H5. Laptops

Three laptops — a ThinkPad, a MacBook and a Dell — belong to Vlad, Yana and Zoriana.
1. Yana's laptop is not the Dell.
2. Zoriana owns the MacBook.

Who owns which laptop?

**Answer format.** Put into "solution" an object that maps each of "Vlad", "Yana", "Zoriana" to their laptop ("ThinkPad", "MacBook", "Dell").
