# Команда C. Набір задач

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



## Задача C1. Knights and knaves (3)

On an island, knights always tell the truth and knaves always lie. You meet Olha, Pylyp and Rostyslav.
Olha says: "At least one of us three is a knave."
Pylyp says: "Olha is a knight."
Rostyslav says: "Pylyp is a knave."

Who is a knight and who is a knave?

**Answer format.** Put into "solution" an object that maps each of "Olha", "Pylyp", "Rostyslav" to "knight" or "knave".


## Задача C2. Release planning (optimization)

A team plans the next release. The budget is 20 developer-days, and the team can build at most 5 features. Candidate features (cost in developer-days / business value in points):

- Single sign-on (SSO): 5 / 8 — security feature
- Audit log: 3 / 4 — security feature
- Two-factor authentication (2FA): 4 / 7 — security feature
- Dark mode: 2 / 3
- Offline mode: 6 / 9
- Real-time sync: 5 / 8
- CSV export: 2 / 2
- Public API: 7 / 11
- Rate limiting: 3 / 3 — security feature
- Full-text search: 4 / 6

Rules:
1. 2FA can only be built if SSO is also built.
2. Offline mode and real-time sync cannot both be built.
3. If the public API is built, rate limiting must also be built.
4. At least two security features must be built.

Which features should be built to maximise total business value? Give the set and the total value.

**Answer format.** Put into "solution" an object {"build": [...]} listing the features to build, using the feature names exactly as written in the problem; put the total business value into "objective".


## Задача C3. Round table

Six people sit around a round table with six equally spaced chairs, numbered 1 to 6 clockwise. Iryna sits in chair 1.
1. Orest sits next to Iryna.
2. Kostiantyn sits directly opposite Iryna.
3. Liudmyla sits next to Kostiantyn.
4. Mykhailo sits next to Orest.
5. Nataliia sits in the chair immediately counter-clockwise from Liudmyla.
6. Orest does not sit in chair 2.

Who sits in which chair?

**Answer format.** Put into "solution" an object that maps each of "Iryna", "Kostiantyn", "Liudmyla", "Mykhailo", "Nataliia", "Orest" to their chair number (integer 1–6).


## Задача C4. Days off

Five colleagues — Andrii, Bohdana, Vasyl, Hanna and Denys — each take one day off during the same working week, all on different days.
1. Vasyl's day off is the day just before the weekend.
2. Hanna takes her day off in the middle of the working week.
3. Andrii's day off is the day immediately after Bohdana's.
4. Denys does not take the first working day of the week off.

On which day does each colleague rest?

**Answer format.** Put into "solution" an object that maps each of "Andrii", "Bohdana", "Vasyl", "Hanna", "Denys" to their day off ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday").


## Задача C5. Parcel delivery

Three parcels — for Liubov, Mykola and Nazar — were delivered at 9:00, 10:00 and 11:00, one per hour.
1. Mykola's parcel arrived earlier than Liubov's.
2. Nazar's parcel did not arrive at 9:00.
3. Liubov's parcel did not arrive last.

When did each parcel arrive?

**Answer format.** Put into "solution" an object that maps each of "Liubov", "Mykola", "Nazar" to the delivery time of their parcel ("9:00", "10:00", "11:00").
