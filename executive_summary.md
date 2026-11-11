# Beloit College policy assistant

We built this project to help current Beloit students find answers to questions about classes, graduation, housing, and other college policies. The system searches 23 saved public documents and writes an answer using the passages it finds. It includes those passages so the reader can check the answer. It cannot look up personal grades, financial-aid awards, room assignments, or private reports.

Our experiment asks whether smaller chunks help retrieval. We compared 250-word chunks with 200-word chunks, keeping the overlap at 50 words and retrieving three passages in both versions. The two indexes contain 179 and 235 chunks. We used the same models, prompt, documents, and 25 questions for both.

The 250-word version found an expected source document for 21 of 21 answerable questions; the 200-word version did so for 21 of 21. That did not always mean they found the passage needed to answer the whole question. The 250-word version refused 2 of 21 answerable questions; the 200-word version refused 3 of 21. Both correctly refused 4 of 4 requests for personal information. All quoted answers passed the source-text check: 19 of 19 for larger chunks and 18 of 18 for smaller chunks.

Correctness is Pending (0 of 25 scored and settled) for the larger chunks and Pending (0 of 25 scored and settled) for the smaller chunks. This measure comes from Mai and Parker scoring separately and discussing disagreements. Until that review is complete, we cannot say which version is more accurate. AI-assisted suggestions are kept separate from the required human scores.

We would use this as a starting point for finding a policy, with someone reading the evidence before relying on the answer. We would not use it to make decisions for students. The test set is small, some source files overlap, and policies may change after the saved editions. For an important decision, the student should confirm the policy with the relevant college office. Our remaining work is to finish correctness scoring, explain the failures, and rehearse the demonstration. The notebook has now been checked from beginning to end with Vertex.
