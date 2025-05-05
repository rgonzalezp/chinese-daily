# Feature TODO List

- **Keyword Cards in Calendar:** Implement a feature where we add a card/indicator inside the calendar cell for a specific date. The card would display one or a few keywords extracted from the notes saved for that day. This might involve generating embeddings from the notes text to find the most relevant keywords.
- **Task Checkboxes:** [ x ]Enhance the rendering of task list items (from the `tasks/*.md` files) to include interactive checkboxes. Persist the checked state of these boxes, likely associated with the specific date being viewed.
- **Saved Note Preview:** When viewing/editing notes for a specific date, add a separate, read-only preview area (perhaps a right sidebar/panel) that displays the *last successfully saved* version of the notes for that date, rendered as Markdown. 
- **Hide template:** two possibilities. Fully hide the tasks week bar behind a button or make it shorter and on hover make a preview of the tasks pop(which would be just a preview of markdown again). The pop should be like a sliding window coming out 
- Make the note good markdown by default and on double click make it editable. Add some nice css hovering animation that is in theme with th rest of the app so the user knows something could happen if they double click on it
- Create cursor rule so that the AI looks at the index file when looking to fix specific components
