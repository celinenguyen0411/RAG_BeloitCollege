# Ingestion Plan & Experiment Results

### 1. Corpus Metrics & Chunking Strategy
* **Corpus Overview:** 22 total documents containing 38,148 total words.
* **Experimental Comparison:**
  * **250-Word:** **165 chunks** (Selected)
  * **750-Word:** **56 chunks**
* **Selection Rationale:** We selected **250-word chunks with a 30-word overlap**. The assignment required an index of at least 150 chunks to ensure realistic retrieval. The 750-word experiment produced only 56 chunks (failing the requirement), while the 250-word experiment produced 165 chunks. The 30-word overlap keeps policy statements intact when sentences cross chunk boundaries.

### 2. Document Boundaries
Document boundaries were decided based on section headers and policy topics. A document begins at the main heading for a specific subject and ends where that policy finishes or the next heading starts, ensuring each file contains a single, self-contained topic.

### 3. Test Answer Questions
* **Question 1:** *What initial steps must a student take to resolve a roommate or floor mate conflict before a room change can be approved?*
  * **Answer:** The student must first attempt direct dialogue with their roommate/floormate and work with their Resident Assistant (RA) on mediation steps and inventory forms before Residence Life will approve a room change.
* **Question 2:** *What three academic progress standards determine continued financial-aid eligibility?*
  * **Answer:** The three Satisfactory Academic Progress (SAP) standards are: 1) Cumulative GPA (minimum 2.0), 2) Completion Rate (passing at least 67% of attempted units), and 3) Maximum Timeframe (attempting less than 150% of degree units).
* **Question 3:** *How many units can be double counted if a student majoring in Data Science or Data Analytics pursues another major or minor?*
  * **Answer:** Students majoring in Data Science or Data Analytics may double-count up to 4 units toward another major or minor.

### 4. --check Output Analysis
* **What Was Found:** Running headers, page footers, page markers, and table-of-contents listings.
* **How We Handled It:** Targeted specific page ranges in `documents.csv` to cut out front-matter boilerplate, used `unwrap()` in `text_from_pdf()` to fix margin line breaks, and deliberately kept `[page N]` markers to retain source page traceability.
* **Why It Matters:** Boilerplate text (like *"Beloit College Catalog 2025-2027"*) appears on almost every page. In TF-IDF and vector retrieval, this shared noise distorts similarity scores, causing search to surface irrelevant chunks based on repeated header terms rather than actual policy content.

### 5. Manual Handling & Deliberate Exclusions
* **Manual Handling:** We manually identified the start and end page numbers in the PDF catalog for specific policy sections and entered those page ranges into `documents.csv`.
* **Deliberately Left Out:** Unrelated department pages, cover pages, tables of contents, administrative lists, and campus boilerplate text not needed to answer the target questions.