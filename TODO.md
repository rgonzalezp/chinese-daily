# Feature TODO List

- **Keyword Cards in Calendar:** Implement a feature where we add a card/indicator inside the calendar cell for a specific date. The card would display one or a few keywords extracted from the notes saved for that day. This might involve generating embeddings from the notes text to find the most relevant keywords.
- [ ] **Implement theme selection control**. The idea is to provide a gallery of themes with names. Called red sun the original, and planning on creating a new theme called bobba for shelly. The colors of this theme are going to be cream yellowish and brown pastel
- [ ] **Implement markdown editor on double click for task section as my notes section** Taking a step forward, we want to let users edit their tasks for the day directly since they might want to change it on the fly for the day.
- **Task Checkboxes:** [x]Enhance the rendering of task list items (from the `tasks/*.md` files) to include interactive checkboxes. Persist the checked state of these boxes, likely associated with the specific date being viewed.
- **Saved Note Preview:** [x]When viewing/editing notes for a specific date, add a separate, read-only preview area (perhaps a right sidebar/panel) that displays the *last successfully saved* version of the notes for that date, rendered as Markdown. 
- **Hide template:** two possibilities. Fully hide the tasks week bar behind a button or make it shorter and on hover make a preview of the tasks pop(which would be just a preview of markdown again). The pop should be like a sliding window coming out 
- [x] Make the note good markdown by default and on double click make it editable. Add some nice css hovering animation that is in theme with th rest of the app so the user knows something could happen if they double click on it
- Create cursor rule so that the AI looks at the index file when looking to fix specific components
- [x] masterful work. Now the next task might be a bit challenging since it requires some major rewiring (maybe? not sure. you need to give me some advice). We want to make it so that instead of loading the MDE editor when we click on a day, IF THERE IS ALREADY AN EXISTING NOTES FILE, we actually render a good looking markdown formatted version of the file( like in the tasks section). Now, here is the cool part, we want to make it so that if the person double clicks on the notes, we remove the markdown and we load the mde with the notes populated (making sure to do a smooth transition between states) additionally, we want to add a cool hover effect when hovering over the markdown good looking formatted file to signal to the user that it is interactable and that if they double click something will happen. Let's create a clear plan of action and then let's tackle each thing I asked one by one. Don't try to do everything in one go
- [x]bug when saving is not using the tasks version of the note saved !important

- [ ] refactor edit tasks endpoint into edit template weekly schedule vs edit task. edit task view
- [x] add visual indicators so that it is clear that tasks and my notes can be double clicked.
- [x] make headers for the date of the day and tasks and my notes bigger
- [ ] Revise UI vs Web. Not properly separated responsibilities.
- [ ] Naviation bar in view-day jiggles due to mde width higher than default layout 