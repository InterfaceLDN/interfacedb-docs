# InterfaceDB documentation

The Docs7 documentation for [InterfaceDB](https://interfacedb.com): 51 guides, SDK examples and authentication walkthroughs.

## Preview

Requires Node.js, npm and Python 3.

```sh
make dev
```

Open [localhost:3333](http://localhost:3333). Edit the MDX pages directly; configure navigation in `docs.json`. Preview tooling is pinned to Docs7 CLI 0.1.1 and renderer 0.1.9.

```sh
make check
# With the preview running:
make verify
```

The checks cover navigation, page rendering, local links, section anchors, images and Markdown exports.

## Publish with Docs7

In [Docs7 Add New Site](https://context7.com/docs7/add), select:

- **Repository:** `InterfaceLDN/interfacedb-docs`
- **Production branch:** `main`
- **Docs path:** `.`

Publish the site, then optionally configure the custom domain. Docs7 automatically serves `llms.txt`, `llms-full.txt` and individual Markdown pages. The main InterfaceDB website redirects its existing documentation URLs after its `INTERFACEDB_DOCS_URL` build setting points to the published Docs7 origin.

## Source and licence

These guides were migrated from [InterfaceDB](https://github.com/InterfaceLDN/InterfaceDB), an independently operated fork of [Instant](https://github.com/instantdb/instant). They retain upstream terminology; hosted-service plans and availability can differ. Start with the [InterfaceDB connection guide](sdk.mdx) for SDK packages and endpoints.

The upstream base is Instant revision `7607eda60547e0068f05aeb2c43ac92c6356f65d`. Documentation has been adapted from Markdoc to Docs7 MDX with updated package references, navigation and images. See [Apache 2.0](LICENSE.md).
