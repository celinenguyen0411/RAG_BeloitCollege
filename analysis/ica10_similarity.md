# In Class Activity 10
**Authors:** Parker and Mai

### 1. Corpus Passages 
1. **mail-center**: The mail center serves two primary functions: (1) as a central mail distribution center for the U.S./International mail and packages delivered to campus. As such, regular postal rules apply to all stamped mail. Any questionable stamped mail will follow the U.S. postal procedures for follow up inquiry; (2) as a College service for inter-campus mail. Incidents reported to mail center staff or by mail center staff will follow the normal campus investigation/disciplinary process. The Campus Mail Center also retains the right to add additional policies and procedures, given the nature of our on-campus facility and staffing. Students are to make sure that mail and packages include their proper name and their student box number to ensure that their mail and packages are delivered in a timely manner and to the correct person.
2. **vending-machines**: Vending machines are conveniently located in several residence halls. Additionally, more machines are available in the Powerhouse,the lower level of Pearsons Hall, and on the first floor of Morse Library Problems with the equipment, including refunds, should be reported using the contact information listed on the machine.
3. **pets**: No pets, other than fish in an aquarium (5-gallon tank, maximum), are allowed to live on campus with students. Residents having pets that live with them on campus may be required to have the pet removed from campus and/or be required to move off-campus (and charged the full room rate for the remainder of the semester as a result of not following this regulation). Residents who have pets living with them may also be charged a daily fine, a cleaning charge (to be determined by Facilities) for each area damaged by the animal, and may be billed for the replacement of flooring in areas damaged by their pet.
4. **residency**: As a residential liberal arts College, we strongly believe that a significant amount of personal growth and development occurs in the residential environment. For this reason, full-time students are required to live in College housing and subscribe to a dining plan during their first six credit terms. College housing includes residence halls, fraternities, sororities, apartments, special interest houses, and townhouses.
5. **overnight-guests**: Residents may have overnight guests for up to three (3) consecutive nights. As host, you need permission from your roommate, and a guest pass from Security. You also need to notify your RA. All guests must comply with College regulations.
6. **meal-plan**: First-year students must select from one of the top-tier meal plans. Other students may opt into any of the available meal plans. Senior students may choose to opt out of the meal plan.

### Test Questions
1. "What are the functions of the mail center at Beloit College?"
    * Target: mail-center
2. "What buildings are vending machines located in?"
    * Target: vending-machines
3. "What type of pets are allowed on campus?"
    * Target: pets

### 3. Results & Evaluation

#### D1
* Q1: What are the functions of the mail center at Beloit College?
   First choice: mail-center (0.4751)
   Second choice: residency (0.1075)
   VERDICT: correct.

Q: What buildings are vending machines located in?
   First choice: vending-machines (0.3150)
   Second choice: mail-center (0.0000)
   VERDICT: correct.

Q: What type of pets are allowed on campus?
   First choice: pets (0.3644)
   Second choice: mail-center (0.1119)
   VERDICT: correct.

#### D2
4. "Where are incoming letters and boxes processed for undergraduates?"
    * Target: mail-center

#### D3
    0.0000  mail-center  <- you expected this
    0.0000  vending-machines
    0.0000  pets
   VERDICT: every score is zero. This question shares no words with anything in the corpus, so the ranking is arbitrary - whichever passage happens to be listed first wins. Ignore the winner.

It calculates similarity strictly by checking for exact token matches between the question and the passage text. Because Question 4 uses synonyms rather than exact passage words, every vector dot product evaluates to exactly zero, and thus no match and score.

#### D4
* **Prediction:** The embedding model will correctly pick mail-center with a high score and a wide gap over the runner-up.
* **Reasoning:** Keyword search looks for exact words, but embeddings look for meaning. Even with no shared words, it will interpret the synonyms properly, so the embedding model will understand the question.

#### D5
Skipped (GOOGLE_CLOUD_PROJECT environment variable not set in local terminal).

### Last Questions 
1. Your fourth question shared no words with the passage that answers it. What did the keyword method do, and what does that tell you about what it can and cannot measure?
The keyword method gave every passage a score of zero and could not find the right passage. This shows that keyword search only measures exact matching words, not actual meaning or synonyms.

2. Look at the gap between the top two passages in the embedding run. If that gap is small, what does it imply about building a system on top of this? Would you trust the top result on its own?
A small gap means the system is unsure which passage is best because two options look very similar. You should not trust the top result alone. Instead, you should pass the top 2 or 3 passages to the AI generator to be safe.

3. Your Project 2 system retrieves passages and then answers from them. What happens to the answer when retrieval picks the wrong passage? How would you find out that this had happened?
If retrieval picks the wrong passage, the AI will give a wrong answer or guess. You can catch this by testing if the generated answer actually matches the source passage (groundedness check) or by checking citations against a test list.
