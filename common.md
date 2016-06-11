# Common

To keep track of common things in different Wiktionary editions that we can utilize to produce the "general" parser.

## TOC

The table of content part is pretty consistent across different language editions.

```
<div id=”mw-content-text” class="mw-content-ltr">
    <p></p>
    <div id="toc" class="toc">...</div>
    <p></p>

    ...

</div>
```

The header tags (e.g. `<h2>`, `<h3>` etc.) and many information we want .. are on the same level as the `toc` - they are all siblings of `toc`. In another word, they are not nested, so we can iterate over the children of `mw-content-text`.

## Translation table

### Language code

Many translation tables has this format:

> LANGUAGE_NAME:[TRANSLATION]()<sup>[(CODE)]()</sup>, [TRANSLATION]()<sup>[(CODE)]()</sup>, ...

#### Similarities
- All the super scripts have class `extiw`.

#### Differences
- The links may or may not be there.
- The language code may or may not be there.
- There may be one or more translations per language.
