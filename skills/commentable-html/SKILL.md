---
name: commentable-html
description: >
  Deliver work as an HTML page the reader comments on, the Google Docs model with the AI as one of
  the commenters. Comments anchor to the exact element or text the reader selected, thread across
  rounds, and survive edits to the page, because content and comments are stored apart. Also says
  how to build the page so it reads at a glance: the result first, an overview figure, one section
  per part with its own figure, and a small map after each. Use when chat is too flat for the
  deliverable (a report, a comparison, a spec, a plan, a review) and the reader will point at its
  parts. Triggers: "deliver this as html I can comment on", "make it commentable", "a page I can
  comment on", "I have comments, check and respond", "let's iterate on this in a doc",
  "commentable-html", "/commentable-html". Do not use for a quick text answer or for content with
  no parts worth pointing at.
license: MIT
---

# commentable-html

The chat stays where the reader asks for things, and the deliverable lives in an HTML page. There
the reader sees structure a terminal cannot draw, and points at the exact part they mean. They
select an element or a stretch of text, type a comment, and you both reply under it, round after
round. Every comment carries what it points at, so neither side has to describe "the third cell in
row two".

Content and comments are stored apart. You can regenerate the page between rounds, and the
comments re-attach to the new version. Never write comments into the page's markup.

## The loop

1. Build or update the page, start the server, and give the reader the link.
2. The reader presses C, clicks an element or selects text, and types a comment, as many times as
   they like.
3. The reader says in chat: "I have comments, check and respond."
4. Read every comment before you change anything, and plan one revision that answers the whole set
   (→ *Responding to a round*). Make it in a single pass over the page.
5. Reply under each comment in the page and in chat. Resolve each thread your revision settled. If
   your reply asks the reader something, leave the thread open, so its dot turns blue for them.
6. Your replies appear on the page within 4 seconds, and a reload shows the new content. Back to 2.

## Build the page for the reader

The reader scans the page, points at its parts, and comes back to it after breaks. Build it so the
point shows at a glance and the reader finds their place again after any gap.

1. Before writing, decide what the reader should know, feel and do when they finish. That decides
   what goes in.
2. If the work measured something, put the result with its number in the page's first line, ahead
   of the method and the plan. The result arrives last in the work, so it lands last on the page
   unless you move it.
3. Pick the shape from what links your points. If the links mean *because*, build a pyramid: the
   claim on top, each child answering why or how of its parent, siblings in order of importance. If
   they mean *then*, draw a flowchart: every arrow a real dependency, about seven boxes at most. Most
   pages are a pyramid with a flowchart inside the one section that is a process.
4. Open with an overview figure and its caption. The caption is the page in miniature: the claim,
   then each section once, in order. Write it as if the reader stops there, because many will.
5. Give each part of the overview its own section. Open the section with its figure (a drawing, a
   table, or real images). Under the figure, put two to four bullets of about twenty words, one
   claim each. Close the section with a map: a row of small boxes, one per section in the
   overview's order, finished sections in ink and the rest greyed out, so a reader back from a
   break finds their place at a glance.
6. If a part is a single fact, give it one sentence instead of a section.
7. Make every paragraph the caption of one part or one arrow of a figure. If a paragraph belongs to
   no figure, delete it. If two paragraphs describe the same part, keep one.
8. Build from real blocks: a `<figure>` around a picture and its `<figcaption>`, a real `<table>`
   with `<th>` headers, lists, and headings with stable ids. The comment layer labels each comment
   from them: "row · column" for a table cell, the nearest heading and the first words for text,
   and the figure's caption for a shape or an image, which has no text of its own.
9. Put every number a reader may question in text: a table cell, a caption, or an SVG `<text>`. A
   comment on text finds its place again by that text after an edit, and a comment on a bare shape
   only by the shape's position in the page.

`example/` holds a report built this way, and `example-trace/` a trace (→ *When the page explains
how something works*). Read the one that matches your page to calibrate how much a section carries.

### Write it plainly

- Lead each paragraph with its claim. If the first sentence can be deleted without loss, delete it.
- Write about the reader's problem. Leave out your process, how hard the work was, and praise for
  the page.
- Use plain words. Define a field term at first use and spell out each acronym.
- Give each thing one name and repeat it. "The run", "the experiment" and "the job" read as three
  things.
- State the claim without a negated twin: "it is cheaper", not "it isn't just faster, it's cheaper".
- If a dash or a semicolon welds two clauses together, make them two sentences.
- Replace a vague word with the fact behind it: the number for "significantly", the names for
  "various". Words like robust, comprehensive, crucial and seamless usually stand in for a fact the
  sentence never gives.
- Use only facts you have. If a number is missing, write `[number?]` and ask, because a guessed
  number reads as a measured one.
- Use the active voice with a real actor: "we train the model", not "the model was trained".
- Write and reread one section at a time. Style slips over a long generation, so a page drafted in
  one pass carries more of these faults at the bottom than at the top.

### When the page explains how something works

A model's forward pass, a training step, a pipeline, a metric or any other algorithm gets a trace:
its real code, run on one real example, step by step. It keeps the page shape above, with these
rules on top.

1. Pick one real example from the project's data and use it in every section. If the project has
   no data yet, use a toy example and say so on the page.
2. Give each step its own section. Give each pass of a loop its own section too, with the same code
   and new values, the way a debugger steps it. The section's figure is the code beside a picture
   of the example, and the bullets and the map follow it as on any page.
3. Show the real code in its own language. If you write the code, give it names that say what they
   hold. If it is library code, keep its names and explain them in your comments.
4. Above each step, add a comment in plain words that says what the step does and why. End each line
   that produces something with `# -> value`: a shape, a list, a count, a string.
5. Mark what you added so it reads apart from the file. Show the file's own lines with their line
   numbers, your comments and values in one colour without numbers, and the lines that did not run
   struck through.
6. Get every value by running the code. Keep the script that computes them in the page's folder, and
   have it print or write the values the page shows, so no number is copied by hand. If nothing has
   produced a value yet, mark it ILLUSTRATION.
7. Beside each step, show the example at that moment: the table with the rows this step touched
   coloured, the text with the changed part marked, an image, or a video frame. Under the picture,
   put one box that says the step's output in plain words. On a 1440px screen with both sidebars
   docked, the code and the picture share about 760px, so let them stack when they do not fit.
8. If a step sends text to a model or gets text back, show that text in full and unfolded. A size or
   a summary hides exactly what the reader needs to check.
9. Open with the claim, then the header "In a nutshell" over one overview picture. That picture is
   the page's overview figure, so its caption still names every section once. Draw the thing the
   method works on, to scale with the example's real counts, and show the method's effect as that
   thing changing from one moment to the next. A chain of boxes that name stages shows nothing. To
   test the picture, cover its words. If it no longer shows where the method acts, redraw it.

On every other page, keep two habits from the trace: one real example instead of an abstract one,
and a picture beside the words, so no part can be read two ways.

## Scaffold a page

Make one folder per page, in the project the page reports on, and copy the assets in, so the folder
is self-contained and portable.

```
<page folder>/
  index.html               # your content, wired like assets/template.html
  comment-layer.css        # copied from assets/
  comment-layer.js
  toc-layer.css
  toc-layer.js
  serve.py
  document.comments.json   # the comment store, created by the first comment
  trace.py                 # optional: the script that computes the page's values
```

Wire the page like `assets/template.html`:

- On `<html>`, `data-comment-doc="<id>"` names the store `<id>.comments.json`.
  `data-comment-root="<selector>"` marks the content's container. Only elements inside it take
  comments, which keeps the layers' own buttons out.
- In `<head>`, link `comment-layer.css` and `toc-layer.css`.
- At the end of `<body>`, load `comment-layer.js` and then `toc-layer.js`.

Write the content as ordinary HTML. Never add comment markup by hand, because the layer owns it.

## The contents sidebar

`toc-layer.js` builds a foldable contents list on the left from the headings in the content, so
never hand-write a nav.

- `h2` headings become sections, and the `h3` rows under each section start folded. In a long
  multi-part page, give part headings `class="part"` on an `h2`, and the other `h2`s nest under them.
- If the page has fewer than 3 `h2` and `h3` headings in all, no sidebar appears.
- Give headings stable ids yourself, because comment anchors and sidebar links share them. A heading
  without an id gets one made from its text.
- The sidebar reads headings from `#content`. If the content has another container, set
  `data-content="<selector>"` on the `toc-layer.js` script tag.
- Mark an element `data-toc="skip"` to keep the headings inside it out of the sidebar, such as a
  closed `<details>` fold, because a link into a closed fold scrolls nowhere.
- At 1360px and wider the sidebar docks on the left, 248px wide, and the comments panel docks on the
  right, 340px wide, so the content gets the band between them. Narrower, the sidebar hides behind
  a "☰ Contents" button. The reader can hide it with « and resize it by dragging its edge, and the
  page remembers both.
- The colours come from `--tl-accent`, `--tl-ink`, `--tl-muted`, `--tl-faint`, `--tl-line` and
  `--tl-accent-line`. Set `data-toc="off"` on `<html>` to turn the sidebar off, but only if the
  reader asks.

## How the reader comments

Tell the reader these controls the first time you hand over a page.

- C turns comment mode on and off, and so does the switch at the top of the comments panel. Escape
  turns it off.
- In comment mode, hovering outlines an element, clicking comments on it, and selecting text
  comments on that text.
- A small dot on the left edge of a commented element marks its thread. Clicking the dot or the
  highlight opens the thread.
- The comments panel on the right lists every thread, open, orphaned and resolved, with all its
  messages. Clicking one scrolls to what it points at. The « Comments chip at the bottom right
  reopens a hidden panel and counts the unresolved threads.
- The first comment asks for the reader's name, and the browser remembers it. Clicking the name in
  the panel's header changes it.
- Hovering one of the reader's own messages shows ✎, which edits it in place. AI messages have no
  edit button.

## How you read and reply

Start the server in the page's folder and give the reader the link. Run it in the background,
because it keeps running until stopped:

```bash
python3 serve.py          # → http://127.0.0.1:8777/    a second page: python3 serve.py 8778
```

The server keeps comments in `<docId>.comments.json` beside the page. Read that file directly, and
reply by editing it: append a message to a thread's `messages`, or change its `status`. The page
checks the file every 4 seconds, so your replies appear without a reload.

The server also answers byte-range requests, so an MP4 in the folder plays and seeks in Safari and
Chrome. It lets the browser cache `.mp4 .csv .png .json` files under a `data/` folder for an hour, so
add `?v=N` to their URLs after you change them. Everything else, the comment store included, is sent
uncached.

If the page is opened as `file://`, comments live in that browser's localStorage instead. Then read
and write them through the browser, on the open tab:

```js
window.__commentLayer.threads()                    // threads with anchor labels and quotes
window.__commentLayer.reply(id, text, "AI", {session, host})
window.__commentLayer.editMessage(id, idx, text)   // rewrites messages[idx] and sets editedAt
window.__commentLayer.setStatus(id, "resolved")
window.__commentLayer.export()                     // the whole store as a JSON string
window.__commentLayer.import(jsonString)           // replaces the whole store
```

Prefer the server, because its store survives a closed tab and needs no live browser.

### The comment store

```json
{ "docId": "document", "version": 1, "threads": [
  { "id": "t…", "createdBy": "Sam", "createdAt": "ISO", "status": "open",
    "anchor": { "type": "element|range", "elementId": "…", "cssPath": "…",
                "quote": { "exact": "…", "prefix": "…", "suffix": "…" },
                "label": "− new loss · Accuracy (%)" },
    "messages": [ { "author": "Sam", "text": "…", "at": "ISO" },
                  { "author": "AI", "text": "…", "at": "ISO",
                    "agent": { "session": "…", "host": "…" } } ] } ] }
```

- Read `anchor.label` and `anchor.quote.exact` first, because they say exactly what the reader
  pointed at.
- A human `author` is the commenter's own name. If two people comment on the same paragraph, treat
  it as a disagreement to settle in your reply, not as one request made twice.
- Reply by appending `{ "author": "AI", "text": "…", "at": "<ISO time now>", "agent": {…} }` to
  `messages`. Resolve a thread by setting `"status": "resolved"`.
- Keep `author` exactly `"AI"`, because the styling and the edit button key off it. Put your
  identity in `agent`: `session` is your session id if your harness gives you one, and `host` is
  what `hostname` prints. If you cannot fill a key, leave it out rather than invent one.
- A message the reader edited carries `editedAt`, and its current `text` is the one that counts. To
  edit a message yourself, rewrite `text`, keep `at`, and set `editedAt`. Saves merge messages by
  `author` and `at`, so a changed `at` duplicates the message.
- Change `anchor` only to update its quote after you rewrite the block it points at (→ *Rewriting
  under comments*). The layer owns the rest of it.

## Responding to a round

A round of comments is one review of one page. Answer it as a whole rather than as a queue of
tickets.

1. Read all of it before you change a line: every open and orphaned thread, every message in each,
   and each anchor's label and quote. Skim the resolved threads too, because they hold decisions a
   new comment may reopen.
2. Work out what the set means. Several comments often circle one problem: a framing that does not
   land, a missing column that makes three sections read wrong, a level of detail that is off
   throughout. Some pairs conflict. Some ask for more than their anchor covers, so "this table is
   confusing" can mean restructuring the section.
3. Plan one revision that answers the whole set, and make it in a single pass. Patching comment by
   comment leaves a page where one fix contradicts the framing another comment asked for, a new
   column lands in one table but not its twin, and the terms drift halfway down.
4. Answer every thread on its own and name what changed for that comment, even when one edit
   answered six. If a thread got no change, say so and why.
5. If comments conflict, or one cannot be done, say so in chat and in that thread. Pick a resolution
   and state the trade-off. If you judge a comment out of scope, say that instead of dropping it.
6. Before you call the round done, reread each section you rewrote against *Write it plainly*, one
   section at a time.

## Why comments survive your edits

Each comment stores three anchors: an element id, a CSS path, and a text quote with about 32
characters of context on each side. On every load the layer tries the id, then the CSS path, and
keeps either hit only if that element still holds the quoted text or something close to it. If both
fail, it searches the page for the quote and allows light edits. A comment that finds no match goes to the panel's
"Orphaned" list with its original text, and one that matched only roughly shows "≈ moved".

- Keep stable ids on the blocks readers comment on, whether you edit the page by hand or a script
  rebuilds it. When you edit by hand, change blocks in place rather than rewriting the whole file.
- A stable id alone does not hold a comment. If a rewrite cuts 30–50% of a block's words, the quote
  no longer matches and the block's threads become orphans.

### Rewriting under comments

1. Copy `<id>.comments.json` aside.
2. Rewrite block by block, and leave every `id` untouched.
3. For each thread whose block changed, set `anchor.quote.exact`, `prefix` and `suffix` to the new
   text. You did the rewrite, so you know which old block became which new one.
4. Reload and check that the "Orphaned" list is empty.

If the rewrite deleted the sentence a `range` thread quoted, leave that thread orphaned and list it
in chat. Moving it to the nearest surviving sentence would put the comment on something the reader
never wrote it about, so let the reader decide: restore the sentence, re-aim the comment, or leave it.

### When a rewrite cuts most of the page

Build the short version as its own page: a new folder, a new `data-comment-doc` so it gets its own
store, and links into the full page for anything long. Readers who ask for a cut-down page usually
still want the full one, so keep both.

If the short version must replace the page in place, move the old blocks, ids intact, into
`<details data-toc="skip">` folds: detail that supports a section goes in that section's fold, the
rest in one archive fold at the end. The quotes still match inside a fold, so no thread becomes an
orphan. A closed fold that holds open threads shows their count on its summary line, and jumping to
one of them opens the fold.

## Limits

- The reader cannot edit the text on the page, and charts do not redraw from data. If a request
  needs either, ask the reader how they want to work, such as in a notebook or a shared document.
- `serve.py` listens on 127.0.0.1 only and has no login, so it serves your own machine. To let other
  people comment, host the folder behind a login you trust, on a server that answers `GET` and `PUT`
  on `./__comments__/<docId>` the way `serve.py` does. The layer finds that route by itself, and each
  commenter signs with their own name.
- Never hand out a `file://` copy. Comments written there stay in that browser's localStorage and
  never reach you.
- Printing hides the comment controls and the sidebar.

## Checking the page in a browser

- Screenshot the page before you hand it over. Look for clipped text, overlaps, and a figure that
  disagrees with its table.
- A navigation that changes only the `#hash` does not reload the page, so add `?v=N` to the URL when
  you re-check a rebuilt page.
- A background tab never fires `requestAnimationFrame` and never scrolls smoothly. To drive one, set
  `scroll-behavior: auto` and call `__commentLayer.reanchor()`, which redraws at once.

## Upgrading an older page

Each page folder holds its own copy of the assets, so a newer version of this skill does not reach
pages built earlier. To upgrade one, copy the new `comment-layer.js` and `comment-layer.css`
together, because the script emits class names that only its own stylesheet styles. The layer reads
older stores, so existing comments load.
