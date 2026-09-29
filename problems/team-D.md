# Команда D. Набір задач

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



## Задача D1. Knights and knaves (5)

On an island, knights always tell the truth and knaves always lie. You meet Alla, Bohdan, Vitalii, Hanna and Dariia.
Alla says: "Bohdan and Vitalii are both knights."
Bohdan says: "Hanna is a knave."
Vitalii says: "Alla is a knight or Dariia is a knight."
Hanna says: "Exactly two of us five are knights."
Dariia says: "Vitalii and I are of different kinds."

Who is a knight and who is a knave?

**Answer format.** Put into "solution" an object that maps each of "Alla", "Bohdan", "Vitalii", "Hanna", "Dariia" to "knight" or "knave".


## Задача D2. Four houses

Four neighbours live in four houses in a row, numbered 1 to 4 from left to right. Each has a different name, pet and front-door colour.

1. Ivan lives in house 2.
2. Ivan lives next to Zlata.
3. The person who has a red door has a turtle.
4. Yurii lives somewhere to the left of the person who has a yellow door.
5. Ivan does not have a rabbit.
6. The person who has a yellow door does not have a cat.
7. The person who has a cat does not have a blue door.
8. The person who has a turtle lives in house 4.
9. Zlata lives next to the person who has a blue door.

For each house, determine the name, pet and door colour.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4" and whose values are objects with the keys "Name", "Pet", "Door". Use exactly these values — Name: "Yurii", "Zlata", "Ivan", "Kateryna"; Pet: "cat", "dog", "rabbit", "turtle"; Door: "yellow", "blue", "red", "green".


## Задача D3. Parking lot

Five researchers park in five spots in a row, numbered 1 to 5 from left to right. Each researcher has a different name, car colour, research topic, pet and hobby. "To the left of" means a lower spot number; "next to" means adjacent spot numbers.

1. The person who works on robotics owns the cat.
2. The person who drives the blue car parks next to the person who plays chess.
3. The person who drives the black car parks next to Halyna.
4. The person who goes running parks next to the person who drives the blue car.
5. Maksym does not own the parrot.
6. The person who goes running parks in spot 5.
7. The person who works on security parks somewhere to the left of the person who works on graph algorithms.
8. The person who drives the blue car plays the guitar.
9. The person who drives the green car parks in spot 2.
10. The person who works on computer vision does not own the parrot.
11. Maksym does not drive the black car.
12. The person who owns the hamster parks in spot 5.
13. Maksym parks next to the person who owns the dog.
14. The person who drives the black car owns the cat.
15. Lesia parks somewhere to the left of the person who owns the hamster.
16. Ihor parks immediately to the left of the person who goes running.
17. The person who drives the red car parks somewhere to the left of the person who owns the hamster.
18. The person who owns the dog parks next to the person who paints.
19. The person who drives the green car works on graph algorithms.

For each parking spot, determine the name, car colour, topic, pet and hobby.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4", "5" and whose values are objects with the keys "Name", "Car", "Topic", "Pet", "Hobby". Use exactly these values — Name: "Halyna", "Ihor", "Lesia", "Maksym", "Nina"; Car: "red", "blue", "white", "black", "green"; Topic: "robotics", "vision", "NLP", "graphs", "security"; Pet: "cat", "dog", "parrot", "fish", "hamster"; Hobby: "chess", "climbing", "guitar", "running", "painting".


## Задача D4. Bookshelf

Four books stand on a shelf in positions 1 to 4 from left to right: a dictionary, an atlas, a novel and a cookbook.
1. The atlas stands at one of the two ends of the shelf.
2. The novel stands immediately to the right of the dictionary.
3. The cookbook is not next to the atlas.
4. The atlas is somewhere to the left of the novel.

What is the order of the books?

**Answer format.** Put into "solution" an object that maps each of "Dictionary", "Atlas", "Novel", "Cookbook" to its position on the shelf (integer, 1 = leftmost).


## Задача D5. Class photo

Six students stand in a line for a photo, in positions 1 to 6 from left to right: Yaryna, Zakhar, Ilko, Kyrylo, Lada and Marko.
1. Kyrylo stands at the right end.
2. Exactly one person stands between Yaryna and Zakhar.
3. Exactly two people stand between Ilko and Marko.
4. Zakhar stands somewhere to the left of Yaryna.
5. Marko stands somewhere to the left of Ilko.
6. Lada stands second from the left.

What is the order of the students?

**Answer format.** Put into "solution" an object that maps each of "Yaryna", "Zakhar", "Ilko", "Kyrylo", "Lada", "Marko" to their position (integer, 1 = leftmost).
