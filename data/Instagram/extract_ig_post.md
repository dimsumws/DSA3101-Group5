## Steps to Extract Data from Universal Studios Singapore’s Instagram Posts

### 1️⃣ Navigate to the Correct Directory
- Open a terminal or command prompt.
- Change to the directory containing your scripts:
  ```bash
  cd path/to/your/scripts
  ```

### 2️⃣ Login to Instagram in Firefox
- Open **[Instagram](https://www.instagram.com/)** in **Firefox** and log in to your account.

### 3️⃣ Import Session from Firefox
- Run the following script to import your Instagram session from Firefox:
  ```bash
  python 615_import_firefox_session.py
  ```

### 4️⃣ Extract Instagram Post Data
- Run the extraction script:
  ```bash
  python extract_ig_post.py
  ```

### 5️⃣ If You Encounter the Error: `400 Bad Request - "challenge_required"`
- **Open Instagram in Firefox**.
- If Instagram prompts **"Suspicious Login Attempt"** or **"Verify It’s You"**, follow the verification steps via email/SMS.
- After completing the verification, run the extraction script again:
  ```bash
  python extract_ig_post.py
  ```
