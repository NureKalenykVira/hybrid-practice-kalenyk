# Команда A. Набір задач

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



## Задача A1. Five offices

Five developers work in five offices along a corridor, numbered 1 to 5 from left to right. Each developer has a different name, main programming language, editor, favourite drink and operating system. "To the left of" means a lower office number; "next to" means adjacent office numbers.

1. The person who drinks tea works somewhere to the left of the person who drinks cocoa.
2. The person who writes Java works somewhere to the left of the person who runs FreeBSD.
3. The person who drinks water works in an office next to the person who uses Zed.
4. The person who uses IntelliJ works in an office next to the person who uses Zed.
5. The person who drinks coffee writes Rust.
6. Anton runs FreeBSD.
7. The person who runs ChromeOS works in office 1.
8. The person who drinks water does not use Emacs.
9. The person who uses VS Code runs Linux.
10. The person who uses Zed works in the office immediately to the left of Yevhen.
11. Vira works in an office next to the person who runs macOS.
12. Bohdana works in office 5.
13. The person who writes Kotlin works in office 4.
14. The person who writes Python does not drink kefir.
15. The person who writes Rust works in the office immediately to the left of the person who writes Kotlin.
16. The person who uses Emacs works somewhere to the left of the person who writes Kotlin.
17. The person who runs macOS works in office 3.
18. The person who uses Vim works in an office next to the person who drinks tea.

For each office, determine the name, language, editor, drink and operating system.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4", "5" and whose values are objects with the keys "Name", "Language", "Editor", "Drink", "OS". Use exactly these values — Name: "Anton", "Bohdana", "Vira", "Dmytro", "Yevhen"; Language: "Rust", "Go", "Python", "Java", "Kotlin"; Editor: "Vim", "Emacs", "VS Code", "IntelliJ", "Zed"; Drink: "tea", "coffee", "kefir", "water", "cocoa"; OS: "Linux", "macOS", "Windows", "FreeBSD", "ChromeOS".


## Задача A2. Exam timetable

Four exams — Algorithms, Databases, Networks and Statistics — must be scheduled on Monday, Tuesday or Wednesday. Several exams may share a day, but two exams taken by the same student must be on different days.

Enrolments:
- Iryna: Algorithms, Databases
- Oleh: Databases, Networks
- Marta: Networks, Statistics
- Denys: Algorithms, Networks
- Sofiia: Databases, Statistics
- Yurii: Algorithms, Statistics

Additionally, Networks cannot be held on Monday.

Give a valid timetable (day for each exam).

**Answer format.** Put into "solution" an object that maps each of "Algorithms", "Databases", "Networks", "Statistics" to its day ("Monday", "Tuesday", "Wednesday").


## Задача A3. Meetup talks

Four talks are given at a meetup in time slots 1 to 4 (slot 1 is the earliest). Each talk has a different speaker, topic, format and language.

1. The person who presents in English speaks at some point earlier than Liana.
2. The person who talks about testing speaks at some point earlier than Marko.
3. The person who talks about UX speaks in slot 2.
4. The person who gives a lecture speaks in slot 2.
5. The person who runs a workshop speaks at some point earlier than Nadiia.
6. Liana speaks in the slot immediately before the person who gives a live demo.
7. The person who presents in Ukrainian speaks in slot 4.
8. The person who talks about databases speaks in slot 4.
9. The person who presents in Polish and the person who talks about testing speak in adjacent slots.
10. The person who presents in Polish and Marko speak in adjacent slots.

For each slot, determine the speaker, topic, format and language.

**Answer format.** Put into "solution" an object whose keys are "1", "2", "3", "4" and whose values are objects with the keys "Speaker", "Topic", "Format", "Language". Use exactly these values — Speaker: "Liana", "Marko", "Nadiia", "Orest"; Topic: "testing", "security", "databases", "UX"; Format: "demo", "lecture", "workshop", "panel"; Language: "Ukrainian", "English", "Polish", "German".


## Задача A4. Knights and knaves (3)

On an island, knights always tell the truth and knaves always lie. You meet Anya, Borys and Vika.
Anya says: "Borys is a knave."
Borys says: "Anya and Vika are of the same kind."
Vika says: "Borys is a knight."

Who is a knight and who is a knave?

**Answer format.** Put into "solution" an object that maps each of "Anya", "Borys", "Vika" to "knight" or "knave".


## Задача A5. Race results

Four runners — Anna, Bohdan, Kira and Dmytro — finished a race. There were no ties.
1. Kira finished before Anna.
2. Bohdan finished immediately after Anna.
3. Dmytro was neither first nor last.

In what order did they finish (positions 1–4)?

**Answer format.** Put into "solution" an object that maps each of "Anna", "Bohdan", "Kira", "Dmytro" to their finishing position (integer, 1 = first).
