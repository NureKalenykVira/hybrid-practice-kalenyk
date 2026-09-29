# Команда G. Набір задач

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



## Задача G1. Three cities

Ulyana, Fedir and Khrystyna live in Kyiv, Lviv and Kharkiv, one person per city.
1. Khrystyna lives neither in Lviv nor in Kyiv.
2. Fedir does not live in Kyiv.

Who lives where?

**Answer format.** Put into "solution" an object that maps each of "Ulyana", "Fedir", "Khrystyna" to their city ("Kyiv", "Lviv", "Kharkiv").


## Задача G2. Knights and knaves (6)

On an island, knights always tell the truth and knaves always lie. You meet six islanders: Ivanna, Kostiantyn, Lesia, Marta, Nestor and Orysia.
Ivanna says: "Exactly three of us six are knights."
Kostiantyn says: "Ivanna and Lesia are of different kinds."
Lesia says: "If Marta is a knight, then Nestor is a knave."
Marta says: "Kostiantyn is a knave or Orysia is a knight."
Nestor says: "At most two of us six are knaves."
Orysia says: "Nestor and Marta are both knaves."

Who is a knight and who is a knave?

**Answer format.** Put into "solution" an object that maps each of "Ivanna", "Kostiantyn", "Lesia", "Marta", "Nestor", "Orysia" to "knight" or "knave".


## Задача G3. Report deadlines

Four reports — finance, HR, sales and legal — are each due on the last day of a different month: January, February, March or April 2027.
1. The finance report's due date has the smallest day-of-month number of the four.
2. The HR report is due on the 31st.
3. The legal report is due exactly one month after the HR report.

Which month is each report due in?

**Answer format.** Put into "solution" an object that maps each of "Finance", "HR", "Sales", "Legal" to the month it is due ("January", "February", "March", "April").


## Задача G4. Cousins' ages

Five cousins — Anhelina, Borys, Valeriia, Hryhorii and Diana — are 5, 8, 11, 14 and 17 years old, all different.
1. Borys is 6 years older than Diana.
2. Hryhorii is the youngest.
3. Valeriia is younger than Diana.

How old is each cousin?

**Answer format.** Put into "solution" an object that maps each of "Anhelina", "Borys", "Valeriia", "Hryhorii", "Diana" to their age (integer).


## Задача G5. Family ages

A family: grandmother Paraska, mother Raisa, father Semen, son Tymofii and daughter Uliana. All ages are whole numbers.
1. Tymofii is twice as old as Uliana.
2. Raisa is 24 years older than Tymofii.
3. Eight years ago, Raisa was seven times as old as Tymofii was then.
4. In five years, the ages of Semen and Raisa will add up to 90.
5. Paraska was 22 years old when Raisa was born.

How old is each family member?

**Answer format.** Put into "solution" an object that maps each of "Paraska", "Raisa", "Semen", "Tymofii", "Uliana" to their age (integer).
