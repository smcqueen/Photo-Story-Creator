# Shared project format

The desktop application continues to use the UTF-8 JSON `.pscproj` format from
Photo Story Creator 1.9.1. The existing browser application remains the
authority for applying defaults to older projects during this first desktop
checkpoint.

Desktop file services validate the format marker and basic structure without
discarding unknown fields. This lets v2.0 open projects from v1.2 through v1.9.1
and write them without imposing a premature v2-only schema.

Any future migration must be explicit, covered by fixtures, and retain a way to
save a browser-compatible project until the v2 format is intentionally released.
