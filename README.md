# Risk Radar Backend

## Backend Code Conventions

All contributors (including LLMs) **must** read and follow:

- [BACKEND_DEVELOPMENT_GUIDELINES.md](./BACKEND_DEVELOPMENT_GUIDELINES.md)
- [Rapid_MVP_App_Architecture.md](./Rapid_MVP_App_Architecture.md)

**Do not** introduce new files, apps, or patterns unless justified in these documents.  
If you propose a change, reference the relevant section in these docs.

For LLM/AI users:  
Always specify the file and function/class to edit, and check for existing conventions before suggesting changes.

> For Nessus field extraction and mapping, see [nessus_extractor.py extraction script](https://github.com/ciaran-finnegan/nessus-reporting-metrics-demo/blob/main/etl/extractors/nessus_extractor.py).

---

## Onboarding Checklist

- [ ] Read `BACKEND_DEVELOPMENT_GUIDELINES.md` and `Rapid_MVP_App_Architecture.md`
- [ ] Use the documented file layout and naming conventions
- [ ] Before making changes, check if the change is allowed by the guidelines
- [ ] If unsure, ask for clarification or propose an update to the guidelines first
- [ ] For LLM/AI: Always include these files in your context or reference them in your prompt

---

## How to Use Cursor Context / Pinned Files

**Cursor** (the AI-powered code editor) allows you to "pin" files so that the LLM always considers them when generating code or suggestions.

### To Pin Files in Cursor:

1. **Open the file** you want to pin (e.g., `BACKEND_DEVELOPMENT_GUIDELINES.md` or `Rapid_MVP_App_Architecture.md`).
2. **Right-click** on the file tab or in the file explorer.
3. Look for options like "Add Files to Cursor Chat" or "Add Files to New Cursor Chat". (The exact wording may vary by version.)
4. Select the option to add the file to your chat context. You may need to do this for each new chat session.
5. Repeat for any other files you want always included (e.g., your architecture doc).

**Result:**  
Whenever you ask Cursor to generate, refactor, or suggest code, it will use the content of these files as part of its context window—making it much more likely to follow your conventions and not introduce unnecessary changes.

### Tips

- You can add multiple files (e.g., guidelines, architecture, and key models) to your chat context.
- If you update your guidelines, re-add the file to refresh the context.
- For best results, keep your guidelines and architecture docs concise and up to date.

If you do not see a "pin" or "add to context" option, check Cursor's documentation or updates, as the feature may be named differently or require a specific workflow in your version. 