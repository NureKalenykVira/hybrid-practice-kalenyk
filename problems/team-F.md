# Команда F. Набір задач

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



## Задача F1. Radio frequencies (minimisation)

Eight radio stations must each be assigned a broadcasting frequency. Two stations that interfere with each other must get different frequencies. Interfering pairs:

- Kyiv – Zhytomyr
- Kyiv – Vinnytsia
- Kyiv – Cherkasy
- Kyiv – Poltava
- Kyiv – Chernihiv
- Zhytomyr – Vinnytsia
- Vinnytsia – Cherkasy
- Cherkasy – Poltava
- Poltava – Chernihiv
- Chernihiv – Zhytomyr
- Sumy – Poltava
- Sumy – Chernihiv
- Uman – Vinnytsia
- Uman – Cherkasy

What is the smallest number of different frequencies needed? Give the number and one valid assignment (label frequencies 1, 2, 3, …).

**Answer format.** Put into "solution" an object that maps each station name to its frequency (integer 1, 2, 3, …); put the number of different frequencies used into "objective".


## Задача F2. Publication years

Five books were published in 2001, 2004, 2009, 2013 and 2020, one book per year: a poetry collection, a biography, a novel, an essay collection and a memoir.
1. The poetry collection was published exactly 5 years after the biography.
2. The novel was published before any of the other four books.
3. The essay collection was published after the memoir.

In which year was each book published?

**Answer format.** Put into "solution" an object that maps each of "Poetry", "Biography", "Novel", "Essays", "Memoir" to its publication year (integer).


## Задача F3. Apartment building

Four people live on four floors of a small building, floors 1 to 4 (floor 1 is the lowest). Each has a different name, profession, car brand and houseplant.

1. The person who is a teacher grows an orchid.
2. The person who drives a Toyota and the person who grows an orchid live on adjacent floors.
3. The person who grows a ficus lives on floor 3.
4. The person who drives a Toyota lives on the floor directly below the person who drives a Skoda.
5. Raisa lives on a lower floor than the person who drives a Kia.
6. The person who is a pilot and the person who is a teacher live on adjacent floors.
7. The person who is a teacher lives on a lower floor than the person who is an architect.
8. Petro grows a cactus.
9. The person who is an architect lives on the floor directly below the person who grows a cactus.
10. The person who drives a Kia lives on a lower floor than Trokhym.

For each floor, determine the name, profession, car and plant.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4" and whose values are objects with the keys "Name", "Profession", "Car", "Plant". Use exactly these values — Name: "Petro", "Raisa", "Sofiia", "Trokhym"; Profession: "architect", "doctor", "teacher", "pilot"; Car: "Skoda", "Toyota", "Volvo", "Kia"; Plant: "cactus", "ficus", "orchid", "fern".


## Задача F4. Umbrellas

Three umbrellas — red, green and blue — belong to Roksolana, Stepan and Tetiana.
1. Stepan's umbrella is not red.
2. Tetiana's umbrella is neither red nor green.

Whose umbrella is which?

**Answer format.** Put into "solution" an object that maps each of "Roksolana", "Stepan", "Tetiana" to the colour of their umbrella ("red", "green", "blue").


## Задача F5. Cinema seats

Four friends sit in four seats in a cinema row, numbered 1 to 4 from left to right. Each has a different name, snack and favourite film genre.

1. The person who likes dramas sits next to the person who eats candy.
2. Marianna sits somewhere to the left of the person who likes comedies.
3. The person who eats chips likes sci-fi.
4. Nazar sits immediately to the left of the person who likes comedies.
5. Lukiian likes horror films.
6. Lukiian eats popcorn.

For each seat, determine the name, snack and favourite genre.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4" and whose values are objects with the keys "Name", "Snack", "Genre". Use exactly these values — Name: "Lukiian", "Marianna", "Nazar", "Olesia"; Snack: "popcorn", "nachos", "candy", "chips"; Genre: "comedy", "horror", "drama", "sci-fi".
