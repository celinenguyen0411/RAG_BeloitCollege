# Gold evaluation set

25 questions: 21 answerable and 4 unanswerable

## Required evaluation metrics

The DSDA310 Project 2 Evaluation Metrics handout fixes k=3 and requires these five metrics. Use the same gold questions and scoring rules in both conditions. Report counts with their denominators, such as “17 of 24”, rather than percentages alone.

| Metric | Definition and denominator |
|---|---|
| Hit rate | Among answerable gold questions, how many have an expected source document among the three retrieved chunks. A multi-document question is a hit if at least one expected source is present; this does not prove that all needed evidence was retrieved. |
| Quote fidelity | Among answers returning evidence quotes, how many have every returned quote present in its claimed retrieved chunk. Check by code, ignoring only case and extra whitespace. Report individual-quote matches and verified-quote answers over all questions as supplemental counts. |
| Correctness | Among all gold questions, how many answers state the same facts as the expected answer without changing a condition or omitting a condition that changes the answer. Equivalent wording is accepted. Mai and Parker score independently, then compare and resolve disagreements. No AI score substitutes for either partner. |
| Correct refusals | Among gold questions the corpus cannot answer, how many return answerable=false. |
| Wrong refusals | Among gold questions the corpus can answer, how many return answerable=false, including refusals caused by retrieval misses. A vague answer with answerable=true is not a refusal. |

Quote comparison uses exactly `" ".join((s or "").lower().split())`. It does not normalize Unicode, strip punctuation, or use fuzzy matching. Source sentences are copied directly from the processed retrieved chunks, so the quote check remains independent of the earlier Unicode cleanup during document loading.

The handout's prose defines quote fidelity over answers returning quotes, while its example code reports over all questions. To expose this ambiguity rather than silently choose a different definition, the report includes both denominators with distinct labels. For multiple quotes, an answer passes only when every selected quote matches its claimed chunk; individual-quote counts are also saved.

There are 25 gold questions: 21 answerable and 4 unanswerable. Correctness stays pending until both partners independently score all outputs and reconcile disagreements. Requests with API errors or skipped generation are not treated as successful answers/refusals; their coverage and errors are reported separately. A final report requires a completed end-to-end run.

The experiment changes only chunk size: baseline 250 words versus candidate 200 words. Both use 50-word overlap and k=3. The absolute word overlap is held fixed; its proportion of each chunk consequently differs. That consequence is disclosed rather than treated as a separate independently tuned parameter.


## Q01
Question: What steps must I follow to resolve a roommate conflict before a room change can be approved?
Expected answer: Speak directly with your roommate first. If that does not resolve the conflict, contact your RA for mediation, then your Residence Life Coordinator. A room change may occur if the problem remains unresolved and space is available. Residence Life must approve the change.
Required source document IDs: handbook-room-changes
Expected evidence:
- handbook-room-changes: Room Changes/Switching Rooms/Changing Roommates: Any room changes must be approved by the Residence Life Office . For roommate or floor mate conflicts, the process begins by speaking with your roommate or floor mate. If it cannot be worked out, you must then speak with your Resident Assistant (RA) to facilitate mediation. If resolution is still not made, then you are to speak with your Residence Life Coordinator (RLC). If the situation still isn’t resolved, then a room change may occur if there is space available.
Answerable: yes

## Q02
Question: What are the quiet hours on weekdays and weekends, and how do they change during finals?
Expected answer: Sunday through Thursday, quiet hours run from 10 p.m. to 8 a.m. On Friday and Saturday, they run from midnight to 10 a.m. During finals, 24-hour quiet hours begin the day before the first day of finals.
Required source document IDs: handbook-quiet-hours
Expected evidence:
- handbook-quiet-hours: Quiet Hours: ● Sunday-Thursday 10:00 pm-8:00 am ● Friday & Saturday 12:00 am-10:00 am ● During Finals week there are 24-hour quiet hours that are enforced starting on the day before the first day of Finals
Answerable: yes

## Q03
Question: How long can an overnight guest stay, and whose permission or notification is required?
Expected answer: A guest may stay for up to three consecutive nights. The host needs their roommate’s permission, a guest pass from Security, and must notify their RA. Hosts are responsible for their guests’ behavior.
Required source document IDs: handbook-overnight-guests
Expected evidence:
- handbook-overnight-guests: Overnight Guests: Residents may have overnight guests for up to three (3) consecutive nights. As host, you need permission from your roommate, and a guest pass from Security. You also need to notify your RA. All guests must comply with College regulations. Hosts are responsible for the conduct and behavior of their guests.
Answerable: yes

## Q04
Question: Which students must live in college housing and have a dining plan, and what exceptions are listed?
Expected answer: Full-time students must live in college housing and subscribe to a dining plan during their first six credit terms. Listed exceptions include married students, military veterans with two years of active duty, students with dependent children, and students commuting from their parents’ or legal guardians’ home within a 30-minute commute. Other exceptions require prior approval from the Director of Residence Life.
Required source document IDs: handbook-residency
Expected evidence:
- handbook-residency: For this reason, full-time students are required to live in College housing and subscribe to a dining plan during their first six credit terms. College housing includes residence halls, fraternities, sororities, apartments, special interest houses, and townhouses. Exceptions to this policy include married students, military veterans with two years of active duty, students with dependent children, and commuting students who live with their parents/legal guardians within a 30-minute commute. However, all students are to have current Emergency Contact information submitted via the Portal. Any other exceptions must have prior approval of the Director of Residence Life (DRL).
Answerable: yes

## Q05
Question: I locked myself out at 11 p.m. on Saturday. Who should I contact, and would that be different during weekday office hours?
Expected answer: Contact Security on Saturday night. During a college workday’s office hours, call Residence Life at 608-363-2350.
Required source document IDs: handbook-lockout
Expected evidence:
- handbook-lockout: In the event a student is locked out of their room during a college work day, the student should call the Residence Life Office (608-363-2350). If it is after office hours or on the weekend, the student should contact Security, who can let them in.
Answerable: yes

## Q06
Question: I lost my room key. What steps do I need to take to get a replacement?
Expected answer: Contact Residence Life immediately, complete a key replacement form, and take the form to Security to have a new key cut.
Required source document IDs: handbook-lockout
Expected evidence:
- handbook-lockout: If the student loses their key, they should contact Residence Life immediately, fill out a key replacement form, and take it to Security to have a new key cut for their room.
Answerable: yes

## Q07
Question: What should I do if I lose my student ID, and is the first replacement free?
Expected answer: Report the loss to Residence Life and complete a lost ID card form. The first replacement is free; additional replacements have a cost.
Required source document IDs: handbook-student-ID
Expected evidence:
- handbook-student-ID: Students who have lost their ID card/meal card/key card should report it to Residence Life and fill out a lost ID card form. Residence Life will make you a new card for free if it is your first time losing it. Additional cards will have an associated cost to the student.
Answerable: yes

## Q08
Question: I paid the guest meal price because I forgot my ID. Can I get a refund?
Expected answer: Yes. Present the receipt and your valid ID at the Food Service Office within 72 hours to receive a full refund.
Required source document IDs: handbook-student-ID
Expected evidence:
- handbook-student-ID: However, the student will be issued a receipt and can receive a refund, in full, if the student presents the receipt and their valid ID at the Food Service Office within 72 hours.
Answerable: yes

## Q09
Question: What must I do before parking in a campus Student Parking lot, and what happens if I leave a parking ticket unpaid for more than 30 days?
Expected answer: Register your vehicle with Security and purchase a parking permit. After 30 days, an unpaid ticket’s fine doubles and is added to your student account.
Required source document IDs: handbook-vehicle-parking
Expected evidence:
- handbook-vehicle-parking: Students must register their vehicles and purchase a parking permit in order to park in on campus Student Parking lots.
- handbook-vehicle-parking: Tickets must be paid within 30 days and may be paid in the Security Office. After 30 days, the fine will double and the charge will be added to the student account.
Answerable: yes

## Q10
Question: I am already living on campus for summer housing or an activity. When must I clear an Accounting/Enrollment hold, and what happens if I do not?
Expected answer: Clear the hold no later than one week before classes begin. Otherwise, you must move out and cannot attend classes or participate in co-curricular activities. Student Accounts may provide advance written permission to remain under an approved action plan.
Required source document IDs: handbook-account-holds
Expected evidence:
- handbook-account-holds: Students who are already living in the Residence Halls due to summer housing or co-curricular activities must clear an Accounting/Enrollment hold no later than one week before the first day of classes. Students who do not meet this deadline will be required to move out of the Residence Halls and may not attend classes or participate in co-curricular activities. In some cases, the Student Accounts Office may provide written authorization for a student to live or remain in campus housing while following an approved action plan. Participation in co-curricular activities may be approved in the action plan, depending on the unique situation. The student must receive this permission before moving into or continuing to live in the Residence Halls.
Answerable: yes

## Q11
Question: I earned a D+ in a course. Can I repeat it, and which attempt counts toward my GPA and earned units?
Expected answer: A D+ is eligible for repetition under the policy, subject to its exceptions, faculty determination, and available space. The most recent attempt counts toward GPA and earned units. The previous attempt receives zero credit and its grade is excluded from GPA calculation.
Required source document IDs: catalog-grading-policy
Expected evidence:
- catalog-grading-policy: Repeated Courses: Students may repeat a course if they received a grade of “D+” or lower. Credit for the grade from the most recent course attempt will be used in calculating the grade point average and earned unit count. Credit for the previous course attempt will be set to zero; the previous grade will not be used in determining the grade point average. The letter grade will appear on the transcript with an “R” prefx. The grading policy on repeated courses: 1. Applies only to courses taken at Beloit College 2. Applies to “topics” courses only if the same topic is repeated. A “topics” course is one that may be repeated for credit if the topic is diferent 3. Does not apply to music lessons and music ensembles 4. Does not apply to dance courses that may be taken twice for credit Faculty of the repeated course will be able to determine if/ when a student may repeat the course. Enrollment in a repeated course is subject to availability of and space in the course, which are not guaranteed.
Answerable: yes

## Q12
Question: Under what circumstances can I receive an incomplete grade?
Expected answer: An incomplete may be granted for serious illness or injury, a family crisis, or another documented unforeseen circumstance beyond your control that prevents completion. It is intended for a limited amount of remaining work, including qualifying circumstances near the end of term or earlier circumstances followed by unsuccessful good-faith efforts to catch up. Simply missing assignments or having many absences does not qualify.
Required source document IDs: catalog-grading-policy
Expected evidence:
- catalog-grading-policy: Incompletes: Incomplete grades shall be granted only in cases of serious illness or injury, family crisis, or some other substantiated unforeseen circumstance beyond the control of the student that would make it impossible to complete all course requirements by the end of the semester. Incompletes are only an option if the student has extenuating circumstances that occur in the last two weeks of a traditional term, or if the student experienced extenuating circumstances earlier in the term and was unable to catch up with the work, despite good faith eforts to do so. An incomplete is intended for special circumstances where stu- dents have a very limited number of remaining assignments due. A student may not receive an incomplete for a course because of failure to complete required assignments on time and/or because of a signifcant number of absences occurring during the course of the term.
Answerable: yes

## Q13
Question: How do I drop a course after the first week of classes but before the drop deadline?
Expected answer: Obtain an Add/Drop Card from the Registrar’s Office, provide the course details, obtain written approval from the instructor and primary academic advisor, and submit the completed card to the Registrar.
Required source document IDs: registrar-registration
Expected evidence:
- registrar-registration: A student can drop a course after the first week of classes and before the relevant drop deadline by acquiring an Add/Drop Card from the Registrar’s Office on the second floor of Pearsons Hall. At this point in the semester, the Registrar’s Office requires the drop details and written approval of the relevant course instructor(s) and primary academic advisor (AMP or Major), via an Add/Drop Card to process a drop request. The completed Add/Drop Card should be submitted to the Registrar’s Office for final processing.
Answerable: yes

## Q14
Question: How many earned units do I need to graduate, and what minimum GPA is required overall and in my major?
Expected answer: You need at least 31 earned units, a GPA of at least 2.000 in all Beloit courses attempted, and a GPA of at least 2.000 in courses in your major. These are part of the graduation requirements, not the complete list.
Required source document IDs: registrar-graduation-requirements
Expected evidence:
- registrar-graduation-requirements: - Completion of a departmental or interdisciplinary major, with a cumulative grade point average of at least C (2.000) in all courses in the major. - Completion of at least 31 units of earned credit, with a cumulative grade point average of at least C (2.000) in all Beloit courses attempted.
Answerable: yes

## Q15
Question: How many units can a Data Science or Data Analytics major double-count toward another major or minor?
Expected answer: Up to four units.
Required source document IDs: catalog-data-science
Expected evidence:
- catalog-data-science: If students majoring in data science or data analytics want to major or minor in another discipline, up to four units are allowed to be double counted.
Answerable: yes

## Q16
Question: Can AP credit satisfy the writing or quantitative reasoning requirements, and how does that differ from transferring a college course?
Expected answer: AP credit cannot satisfy these requirements. Eligible transferred college courses may satisfy quantitative reasoning and one writing requirement, but not the remaining two writing requirements or intercultural literacy.
Required source document IDs: registrar-transfer-credits
Expected evidence:
- registrar-transfer-credits: Domains and skills transferred before and after matriculation: (a) Students may fulfill domain requirements through transfer credit. (b) Students may transfer courses to fulfill the “Q” and one “W” requirement but not the “C” or final two “W” requirements. After matriculation at Beloit College, students may apply to the registrar to transfer credits in fulfillment of domain and/or permitted skill requirements.
- registrar-transfer-credits: AP credits may not be used to fulfill any of the Domain or Skills requirements.
Answerable: yes

## Q17
Question: I want to take a course at another college to meet Beloit’s quantitative reasoning requirement. What should I do before enrolling, and what minimum grade would make it eligible for transfer?
Expected answer: Complete the Transfer Credit Authorization Form before enrolling and have the proposed credit reviewed. A transferred course may fulfill Q, and a grade of C or better is required for transfer eligibility. Approval is not automatic.
Required source document IDs: registrar-transfer-credits
Expected evidence:
- registrar-transfer-credits: Students enrolled at Beloit who wish to transfer credits for coursework taken after matriculation should complete a Transfer Credit Authorization Form prior to taking a course elsewhere.
- registrar-transfer-credits: - The quantitative reasoning requirement may be fulfilled with a transfer course.
- registrar-transfer-credits: - A grade of “C” or better is required for the credit to transfer.
Answerable: yes

## Q18
Question: I missed the normal drop deadline but am still earning a D. Can I request a WP, what documentation is needed, and will I receive credit?
Expected answer: You may petition for a WP; approval is not guaranteed. Provide your written petition, an instructor statement confirming a D or better, and an advisor statement. Submit by the semester’s last day of classes. The Academic Performance Committee approves the withdrawal. A WP appears on the transcript but earns no credit.
Required source document IDs: registrar-registration
Expected evidence:
- registrar-registration: A student must - provide a written petition requesting a “WP” (including the course number/section/title, the semester, and instructor name). - have the instructor provide a written statement verifying that the student was passing the course with a “D” or better grade at the time of the request. - have their advisor provide a written statement. No credit is granted for a course in which a WP is received, but the course appears on the transcript with a grade of “WP”. Petition forms for students and faculty support. Petitions and letters should be emailed to deanstu@beloit.edu. A petition to the Academic Performance Committee to withdraw from a course with a “WP” grade must be submitted no later than the last day of classes of the semester in which the course is being taken.
Answerable: yes

## Q19
Question: Which senior seminar is required for the Data Science major, and which Economics course is listed among the Economics major’s required departmental courses?
Expected answer: Data Science requires DSDA 310 (0.5 unit). The Economics major’s required departmental courses include ECON 380.
Required source document IDs: catalog-data-science, catalog-econ-requirements
Expected evidence:
- catalog-data-science: Data Science Major (14.5-15 units) 1. Data Science and Data Analytics 210 (.5), 345, and 385. 2. Four units in mathematics: Mathematics 110, 115, 205, and 275. 3. Three units in computer science: Computer Science 111, 204, and 367. 4. At least 1.5 units in data science and data analytics or the humanities, chosen from Art 325, Data Analytics and Science 215, English 265, Greek, Latin, and Ancient Mediterranean Studies 249, Media Studies 150, Writing 215. 5. One disciplinary specialty chosen from the following (3 units): a. Anthropology: Two units chosen from any 100-level anthropology courses and 240 (201 and 225 are recommended). b. Biology: one 100-level biology course and 247; either 215 or 372. c. Chemistry: 117 and 220, and one chosen from 225, 240, 245, or 300. d. Economics: 199, 211, 251 (one from 271, 302, or 303 is recommended). e. Education and Youth Studies: 201, 255, 256, and 306. f. Environmental Studies: one laboratory science course, one statistics or quantitative course from any discipline, and Environmental Studies 258. g. Geology: 100 or 110; one statistics or quantitative course from any discipline; one chosen from Geology 230, 235, or 245, or Environmental Studies 258, with a geology project. h. Health and Society: 140, one statistics or quantitative course from any discipline, and Biology 215. i. Physics: Physics 101 and 335; either Physics 210 or 345. j. Political Science: 110 and 201; either 207 or 215. k. Psychology: 100, 161, 162. l. Sociology: either 100 or 150; 205 and 211. m. Sports Analytics: Economics 199, 202, 251, 300. 6. Data Science and Data Analytics 310 (.5).
- catalog-econ-requirements: Economics Major (13 units) The core of the economics major is economic theory, which is a set of tools an economist uses to understand how the world operates, and how individuals, groups and organizations behave. The major also requires supporting courses in other social sciences, so that students gain interdisciplinary perspectives on how the world operates. This major is suitable for students considering careers in public policy, international   development, education, sustainability, public policy, and others. 1. Nine departmental units: a.Economics 199, 211, 212, 251, 303, and 380. b. Three elective units: choose from Economics 201, 202, 203, 205, 209, 210, 245, 271, 304, 306, and Business 206, 230.
Answerable: yes

## Q20
Question: My roommate’s guest has stayed four consecutive nights, and discussing it with my roommate has not helped. What do the guest rules say, and what should I do next about the conflict?
Expected answer: The normal guest limit is three consecutive nights, with the roommate’s permission, a Security guest pass, and RA notification. Since direct discussion has failed, contact the RA for mediation. If unresolved, contact the RLC; a room change requires approval and available space.
Required source document IDs: handbook-overnight-guests, handbook-room-changes
Expected evidence:
- handbook-overnight-guests: Overnight Guests: Residents may have overnight guests for up to three (3) consecutive nights. As host, you need permission from your roommate, and a guest pass from Security. You also need to notify your RA. All guests must comply with College regulations. Hosts are responsible for the conduct and behavior of their guests.
- handbook-room-changes: Room Changes/Switching Rooms/Changing Roommates: Any room changes must be approved by the Residence Life Office . For roommate or floor mate conflicts, the process begins by speaking with your roommate or floor mate. If it cannot be worked out, you must then speak with your Resident Assistant (RA) to facilitate mediation. If resolution is still not made, then you are to speak with your Residence Life Coordinator (RLC). If the situation still isn’t resolved, then a room change may occur if there is space available.
Answerable: yes

## Q21
Question: Can I bring a pet cat to campus housing, and would calling it an emotional support animal be enough?
Expected answer: Ordinary pet cats are not allowed. An ESA requires approval through the college’s accommodation process before being brought to campus; simply calling a cat an ESA is insufficient. Approval involves a documented disability and a disability-related need for the animal.
Required source document IDs: handbook-overnight-guests, handbook-emotional-support-animals
Expected evidence:
- handbook-overnight-guests: Pets: No pets, other than fish in an aquarium (5-gallon tank, maximum), are allowed to live on campus with students.
- handbook-emotional-support-animals: Students may qualify for this accommodation if (1) the student has a documented disability; (2) the animal is necessary to afford the student with a disability an equal opportunity to use and enjoy their dwelling; and (3) there is an identifiable and documented nexus between the disability and the assistance that the animal provides. The College will allow only those ESAs that are allowed by local and state laws and conform to standards within this policy. Students must receive Emotional Support Animal designation from the Director of Learning Enrichment and Disability Services (hereto referred to as “Director”) prior to bringing their animal to campus. Without such authorization, an animal cannot be kept on campus.
Answerable: yes

## Q22
Question: What is my exact personal financial-aid award for next semester?
Expected answer: The public-document corpus cannot determine your individual award. Consult your official award information or contact Financial Aid.
Required source document IDs: None
Expected evidence:
- None; the requested individual record is absent.
Answerable: no

## Q23
Question: Has my room-change request been approved, and which room have I been assigned?
Expected answer: The corpus cannot determine your request’s status or room assignment. Contact Residence Life for your individual decision.
Required source document IDs: None
Expected evidence:
- None; the requested individual record is absent.
Answerable: no

## Q24
Question: What grade am I currently earning in DSDA 310?
Expected answer: The corpus contains course and grading policies, not your current grades. Check the course’s grade information or ask your instructor.
Required source document IDs: None
Expected evidence:
- None; the requested individual record is absent.
Answerable: no

## Q25
Question: Which students have reported my roommate for violating quiet hours?
Expected answer: The public corpus does not contain individual complaint records or the identities of people who submitted complaints, so the system cannot identify them.
Required source document IDs: None
Expected evidence:
- None; the requested individual record is absent.
Answerable: no
