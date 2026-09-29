# Команда E. Набір задач

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



## Задача E1. Four boxes

Four boxes A, B, C and D each weigh a different whole number of kilograms, from 1 to 10 kg.
1. Box A weighs twice as much as box B.
2. Box C weighs as much as boxes A and B together.
3. Box D is the heaviest of the four.
4. Together the four boxes weigh 24 kg.

How much does each box weigh?

**Answer format.** Put into "solution" an object that maps each of "A", "B", "C", "D" to its weight in kg (integer).


## Задача E2. Dormitory

Five students live in five rooms along a dormitory corridor, numbered 1 to 5 from left to right. Each student has a different name, major, home city, musical instrument and sport. "To the left of" means a lower room number; "next to" means adjacent room numbers.

1. The person who boxes lives somewhere to the left of the person who plays volleyball.
2. Oksana plays the violin.
3. The person who plays football lives somewhere to the left of the person who plays tennis.
4. Pavlo plays the flute.
5. The person who is from Chernihiv lives in room 2.
6. Roman lives somewhere to the left of Pavlo.
7. The person who swims lives in a room next to the person who plays the piano.
8. The person who plays the violin lives in a room next to the person who plays football.
9. The person who plays the piano lives in room 3.
10. The person who studies law lives in the room immediately to the left of the person who plays the bandura.
11. The person who studies history lives in room 4.
12. The person who swims lives somewhere to the left of Taras.
13. The person who studies physics lives in room 5.
14. The person who is from Poltava lives in room 3.
15. The person who is from Odesa does not play the drums.
16. Roman studies medicine.
17. The person who is from Lviv lives in room 1.
18. The person who is from Odesa lives in room 5.
19. Roman lives in a room next to the person who plays volleyball.

For each room, determine the name, major, home city, instrument and sport.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4", "5" and whose values are objects with the keys "Name", "Major", "City", "Instrument", "Sport". Use exactly these values — Name: "Oksana", "Pavlo", "Roman", "Svitlana", "Taras"; Major: "history", "physics", "law", "medicine", "economics"; City: "Lviv", "Odesa", "Poltava", "Sumy", "Chernihiv"; Instrument: "violin", "drums", "piano", "flute", "bandura"; Sport: "football", "tennis", "swimming", "volleyball", "boxing".


## Задача E3. Ticket queue

Five people — Klara, Leonid, Myroslava, Nazar and Oksen — queue for tickets, positions 1 (front) to 5.
1. Leonid stands directly in front of Nazar.
2. Klara stands somewhere behind Myroslava.
3. Oksen is third in the queue.
4. Myroslava is not at the front.
5. Nazar is not at the back.

What is the order of the queue?

**Answer format.** Put into "solution" an object that maps each of "Klara", "Leonid", "Myroslava", "Nazar", "Oksen" to their position in the queue (integer, 1 = front).


## Задача E4. Duty roster

Five lab assistants are each on duty on exactly one day of a working week (Monday to Friday), one assistant per day. Each has a different duty task and brings a different snack.

1. The person who brings nuts is on duty on Wednesday.
2. Arsen is on duty on Thursday.
3. Vlas and Hlafira are on duty on consecutive days.
4. Danylo is on duty the day immediately before the person who waters the plants.
5. Vlas is on duty on Wednesday.
6. The person who brings apples is on duty earlier in the week than the person who brings cheese.
7. The person who runs the backups brings pastries.
8. The person who brings nuts is on duty the day immediately before the person who brings cookies.
9. The person who sorts the mail is on duty the day immediately before the person who runs the backups.
10. The person who fixes the printer is on duty the day immediately before the person who waters the plants.

For each day, determine who is on duty, their task and their snack.

**Answer format.** Put into "solution" an object whose keys are "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" and whose values are objects with the keys "Name", "Task", "Snack". Use exactly these values — Name: "Arsen", "Bozhena", "Vlas", "Hlafira", "Danylo"; Task: "backups", "inventory", "printer", "mail", "plants"; Snack: "apples", "cookies", "nuts", "cheese", "pastries".


## Задача E5. Three siblings

Oleh, Polina and Serhii are 4, 7 and 10 years old, in some order.
1. Polina is older than Oleh.
2. Serhii is not the oldest.
3. Oleh is not the youngest.

How old is each?

**Answer format.** Put into "solution" an object that maps each of "Oleh", "Polina", "Serhii" to their age (integer).
