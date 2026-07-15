# Native share target roadmap

The current Vite application has no manifest, service worker, or PWA plugin, so this slice does not register a Web Share Target.

- Browser extension: add a context-menu/share action that URL-encodes `url`, `text`, and `title` into `/share` query parameters. Configure the deployed app origin and extension permissions.
- Android: provide an `ACTION_SEND` intent filter for text and images, then forward shared values to the authenticated `/share` experience (or call the share-intake API from a native shell). Handle persisted URI permissions for photos.
- iOS: add a Share Extension that accepts URLs, text, and images, stores the payload in an App Group, and opens the host app or an authenticated universal link to `/share`.
- Web Share Target: if PWA support is later adopted, add a web app manifest with a `share_target` POST action, a service worker capable of receiving multipart fields/files, installability assets, HTTPS deployment, and an authenticated handoff to `/share`.
