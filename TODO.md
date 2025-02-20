# Project TODO

Here's a set of small, digestible steps:

1. **Data Gathering**  
   - Download JSON files from Cursor's forum:
     - jupyter-notebooks-in-cursor-yes-please.json (https://forum.cursor.com/t/jupyter-notebooks-in-cursor-yes-please/22015.json)
     - paid-for-cursor-pro-but-it-says-i-m-not-pro-anymore.json (https://forum.cursor.com/t/paid-for-cursor-pro-but-it-says-i-m-not-pro-anymore/50884.json)
     - sonnet-3-5-vs-o3-mini.json (https://forum.cursor.com/t/sonnet-3-5-vs-o3-mini/51054.json)
     - refund-request-for-incorrect-billing.json (https://forum.cursor.com/t/refund-request-for-incorrect-billing/28716.json)
   - Keep them in a `data/` folder.

2. **Data Normalization**  
   - Parse each JSON to extract:
     - Post-level features (post ID, author, content, timestamps).  
     - Discussion-level features (discussion ID, category ID).  
   - Combine into a single DataFrame or table.

3. **Preliminary Analysis**  
   - Check the volume of posts over time (simple line chart).  
   - Perform a basic sentiment analysis on post text.  
   - Compute average sentiment over time.

4. **Vector Embeddings**  
   - Use a library (e.g., sentence-transformers or openai) to embed posts.  
   - Investigate similarity or clustering if relevant.

5. **Validation**  
   - Confirm the DataFrame has correct columns (IDs, timestamps, content).  
   - Verify sentiment analysis yields sensible results (positive, negative, neutral).  
   - Ensure each step runs without errors in your notebook.

6. **Future Enhancements**  
   - Explore more advanced text analytics (topic modeling, LLM prompts).  
   - Possibly automate data scraping from the forum.  
   - Expand beyond these sample threads once comfortable.
